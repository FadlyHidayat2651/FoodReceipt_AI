import sys
import os
import base64
import json
import ast

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.ocr_service import OCRService
from services.llm_service_openrouter import OpenRouterLLM
from db.vector_service import VectorService
from db.receipt_db import ReceiptDB
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Now build paths to your DB files relative to base_dir
sqlite_db_path = os.path.join(base_dir, "db", "receipts.db")
vector_db_path = os.path.join(base_dir, "db", "vector_db.pkl")

class ReceiptProcessor:
    def __init__(
        self,
        vector_db_path=vector_db_path,
        sqlite_db_path=sqlite_db_path,
        llm_model_name="openai/gpt-oss-120b"
    ):
        # Initialize services
        self.ocr = OCRService()
        self.llm = OpenRouterLLM(model_name=llm_model_name)
        self.vector_service = VectorService(db_path=vector_db_path)
        self.receipt_db = ReceiptDB(db_path=sqlite_db_path, vector_service=self.vector_service)

    def process_receipt(self, base64: str):
        """
        Process a receipt image:
        1. OCR extract text
        2. Use LLM to convert to structured JSON
        3. Insert into SQLite and vector DB
        """
        text = self.ocr.extract_receipt_from_base64(base64)
        print("OCR text extracted.")

        # Prepare prompt
        prompt = f"""
        You are an expert at extracting structured data from receipts.
        You will get several information that you should extract, here are the field that you need to extract:
        1. date_of_purchase: The date when the purchase was made.
        2. vendor: The name of the store or vendor where the purchase was made.
        3. total_amount: The total amount paid for the purchase.
        4. item_json: key pair between item name and price in json format.
        5. doc_id : A unique identifier for the receipt (you can make this up).
        6. currency : The currency used in the receipt (e.g., USD, EUR, etc.).
        This is the data that you should extract from the receipt:
        {text}
        Provide the extracted information in a JSON format with the following structure:
        {{
            "doc_id": "string",
            "date_of_purchase": "string",
            "vendor": "string",
            "total_amount": "float",
            "currency": "string",
            "items_json": {{
                "item_name_1": "price_1",
                "item_name_2": "price_2"
            }}
        }}
        Ensure that the JSON is properly formatted and valid. No need to start with 'json' at the beginning, just make it a JSON string directly.
        Answer:
        """

        # Generate structured JSON
        raw_text = self.llm.generate(prompt)
        print("LLM generated structured data.")
        print(raw_text)

        # Parse JSON safely
        try:
            receipt_data = ast.literal_eval(raw_text)
        except Exception:
            raw_text_clean = raw_text.strip().replace("`", "")
            receipt_data = json.loads(raw_text_clean)

        # Insert into DB
        self.receipt_db.add_receipt(
            doc_id=receipt_data["doc_id"],
            date=receipt_data["date_of_purchase"],
            vendor=receipt_data["vendor"],
            total=receipt_data["total_amount"],
            currency=receipt_data["currency"],
            items=receipt_data["items_json"]
        )

        print(f"Receipt {receipt_data['doc_id']} inserted into DB and vector stored successfully.")
        return receipt_data
