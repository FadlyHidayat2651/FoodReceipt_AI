import sys
import os
from typing_extensions import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from typing import Annotated,TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
import operator
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db.vector_service import VectorService
from db.receipt_db import ReceiptDB
from services.llm_service_openrouter import OpenRouterLLM

today = datetime.now().date()
checkpointer = MemorySaver()

# --- State Schema ---
class QnAState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    query: str
    summary: str
    answer: str
    search_params : str


class ReceiptQnAAgent:
    """Receipt Question & Answer Agent using LangGraph"""
    
    def __init__(self, db_dir: str = None, model_name: str = "openai/gpt-oss-120b"):
        """
        Initialize the Receipt QnA Agent
        
        Args:
            db_dir: Directory containing the database files (default: ../db)
            model_name: LLM model name to use
        """
        # Setup database paths
        if db_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(base_dir, "db")
        
        sqlite_db_path = os.path.join(db_dir, "receipts.db")
        vector_db_path = os.path.join(db_dir, "vector_db.pkl")
        
        # Initialize services
        self.vector_service = VectorService(db_path=vector_db_path)
        self.receipt_db = ReceiptDB(db_path=sqlite_db_path, vector_service=self.vector_service)
        self.llm = OpenRouterLLM(model_name=model_name)
    
    def _llm_search_node(self, state: QnAState) -> QnAState:
        """Generate answer based on search results"""
        query = state["query"]
        summary = state.get("summary", [])
        
        prompt =f"""
        You are an assistant that has functions to define which kind of infromation that the user wants to perform 
        on his receipts, today is {today},
        You only need to create search parameter based on the user's query.
        Here is the question from the user: {query}
        Here is also the previous conversation with the user: {state['messages']}
        Please answer the user's question using the information above.  
        """
        
        answer = self.llm.generate(prompt)
        state["search_params"] = answer
        print(f"\n=== Search Params ===\n{answer}\n")
        return state
    
    def search_receipts(self, query: str, top_k: int = 4) -> List[dict]:
        """
        Search receipts by a free-text query using vector similarity
        
        Args:
            query: The user's free-text query
            top_k: Number of top results to return
        
        Returns:
            List of receipt dictionaries
        """
        storage = []
        results = self.vector_service.query_vector(query, top_k=top_k)
        
        for doc_id, score in results:
            receipt = self.receipt_db.get_receipt(doc_id)
            if receipt:
                receipt['match_score'] = float(score)
                score = float(score)
                storage.append(receipt)
                print(f"Score: {score:.4f}, Receipt: {receipt}")
        
        return storage
    
    def _search_node(self, state: QnAState) -> QnAState:
        """Execute the search and store results in summary"""
        query = state["search_params"] 
        receipts = self.search_receipts(query)
        
        print("\n=== Search Results ===")
        print(receipts)
        
        state["summary"] = receipts
        return state
    
    def _llm_reason_node(self, state: QnAState) -> QnAState:
        """Generate answer based on search results"""
        query = state["query"]
        summary = state.get("summary", [])
        
        # Format receipts for the prompt
        receipts_text = ""
        for i, receipt in enumerate(summary, 1):
            receipts_text += f"\nReceipt {i}:\n"
            receipts_text += f"  Date: {receipt.get('date_of_purchase', 'N/A')}\n"
            receipts_text += f"  Vendor: {receipt.get('vendor', 'N/A')}\n"
            receipts_text += f"  Total: {receipt.get('total_amount', 'N/A')}\n"
            receipts_text += f"  Items: {receipt.get('items', 'N/A')}\n"
            receipts_text += f"  Match Score: {receipt.get('match_score', 'N/A'):.4f}\n"
        
        prompt =f"""
        You are an assistant that has functions to answer question about a user's receipts, today is {today},
        The answer itself can be from two sources, the first one is from the receipts that has been provided,
        and the second one is from your own knowledge. or based on the preveious converstaion with the user.
        so even though there is a matching receipt but dont related to the current question and the question somehow related to the previous conversation,
        you can use your own knowledge to answer the question.
        Always make sure that you use the correct currency format based on the given information, currency is a parameter in receipt text.
        Here is the question from the user: {query}
        Here is also the previous conversation with the user: {state['messages']}
        Here are the matching receipts:
        {receipts_text}
        Please answer the user's question using the information above.
        """
        
        answer = self.llm.generate(prompt)
        new_messages  = [f"Question: {query} Answer: {answer}"]
        print("\n=== State Messages ===")
        print(state["messages"])
        # Trim to last 5 messages
        updated_messages = (state.get("messages") or []) + new_messages
        MAX_MESSAGES = 5
        if len(updated_messages) > MAX_MESSAGES:
            updated_messages = updated_messages[-MAX_MESSAGES:]

        print("\n=== State Messages ===")
        print(updated_messages)

        return {
            "answer": answer,
            "messages": updated_messages
        }
            
    def _build_graph(self) -> StateGraph:
        """Build and compile the LangGraph agent"""
        graph = StateGraph(QnAState)
        
        # Add nodes
        graph.add_node("search_creator", self._llm_search_node)
        graph.add_node("search", self._search_node)
        graph.add_node("reason", self._llm_reason_node)
        
        # Add edges
        graph.add_edge(START, "search_creator")
        graph.add_edge("search_creator", "search")
        graph.add_edge("search", "reason")
        graph.add_edge("reason", END)
        
        agentic_result = graph.compile(checkpointer=checkpointer)
        return agentic_result
