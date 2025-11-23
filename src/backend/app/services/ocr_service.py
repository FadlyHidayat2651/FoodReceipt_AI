import base64
from io import BytesIO
from PIL import Image, ImageEnhance
import numpy as np
import easyocr


class OCRService:
    def __init__(self):
        """Initialize EasyOCR reader"""
        print("Initializing EasyOCR... (this may take a moment on first run)")
        self.reader = easyocr.Reader(['en'])
        print("EasyOCR initialized successfully!")
    
    def preprocess_image(self, image):
        """Preprocess image to improve OCR quality"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large
        max_size = 2000
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.LANCZOS)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        return image
    
    def extract_receipt_from_base64(self, base64_string, preprocess=True):
        """
        Extract text from a base64-encoded receipt image
        
        Args:
            base64_string: Base64 encoded image string
            preprocess: Whether to preprocess the image (default: True)
        
        Returns:
            Extracted text as string
        """
        try:
            # Remove data URI prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',', 1)[1]
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_string)
            
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_bytes))
            
            # Preprocess image if enabled
            if preprocess:
                image = self.preprocess_image(image)
            
            # Convert to numpy array for EasyOCR
            img_array = np.array(image)
            
            # Extract text using EasyOCR
            results = self.reader.readtext(img_array)
            
            # Combine all detected text
            text = '\n'.join([result[1] for result in results])
            
            return text if text.strip() else "No text detected in image"
            
        except Exception as e:
            return f"Error: {str(e)}"
        
