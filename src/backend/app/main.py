from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
import sys
import os
from threading import Lock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.agentic_ai_v2 import ReceiptQnAAgent, QnAState
from services.receipt_ingestion import ReceiptProcessor

# Initialize Flask app
app = Flask(__name__)

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Thread lock for agent access
agent_lock = Lock()
agent = None
processor = None
messages = []


def get_agent():
    """Get or create agent instance (thread-safe)"""
    global agent
    if agent is None:
        print("Initializing agent...")
        agent = ReceiptQnAAgent()
        print("Agent ready!")
    return agent


def get_processor():
    """Get or create receipt processor instance"""
    global processor
    if processor is None:
        print("Initializing receipt processor...")
        processor = ReceiptProcessor()
        print("Processor ready!")
    return processor


@app.route('/api/query', methods=['POST', 'OPTIONS'])
def query():
    """
    Query receipts
    
    Request: {"question": "your question here"}
    Response: {"answer": "..."}
    """
    # Handle CORS / preflight
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing question"}), 400

    # Lock if needed to protect shared resources
    with agent_lock:
        agent = get_agent()
        # Use a thread_id to maintain state across calls
        thread_id = "receipt_qna_thread" 

        # Build the config including thread_id
        config = {
            "configurable": {"thread_id": thread_id}
        }

        # Pass an initial state. `messages` should be a list of BaseMessage
        # If this is first call, use an empty or greeting message; if not, the checkpointer will restore.
        initial_state = {
            "messages": [],  
            "query": question,
            "summary": "",
            "answer": "",
            "search_params": ""
        }

        # Invoke the graph — this will fetch the previous state (if exists) and then run nodes
        result = agent._build_graph().invoke(initial_state, config)

    answer = result.get("answer", "")
    return jsonify({"answer": answer})



@app.route('/api/process', methods=['POST', 'OPTIONS'])
def process_receipt():
    """
    Process a receipt image from base64
    
    Request: {"base64_image": "base64_string_here"}
    Response: {"status": "success", "message": "Receipt processed successfully"}
    """
    # Handle OPTIONS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Check if request has JSON
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is empty"}), 400
        
        base64_image = data.get('base64_image')
        
        if not base64_image:
            return jsonify({"error": "Missing base64_image field"}), 400
        
        print(f"Processing base64 image...")
        
        # Use lock to prevent concurrent access
        with agent_lock:
            receipt_processor = get_processor()
            receipt_data = receipt_processor.process_receipt(base64_image)
        
        print(f"Receipt processed successfully")
        
        return jsonify({
            "status": "success",
            "message": "Receipt processed and saved to database successfully"
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run with threaded=False to avoid SQLite threading issues
    app.run(host='0.0.0.0', port=8114, debug=True, threaded=False)