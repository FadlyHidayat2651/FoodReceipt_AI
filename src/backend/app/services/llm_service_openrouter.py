import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load .env file, override=False by default
load_dotenv()

class OpenRouterLLM:
    """
    Wrapper class for OpenRouter LLM with LangChain compatibility.
    """

    def __init__(self, model_name: str, api_key: str = None, temperature: float = 0.7, max_tokens: int = 5000):
        # self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY must be provided either as argument or environment variable.")

        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize the LangChain model
        self.model = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=self.api_key
        )

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant."):
        """
        Generate text from a prompt.
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        response = self.model.invoke(messages)
        return response.content
