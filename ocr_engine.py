import pytesseract
from PIL import Image
import os

class OCREngine:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
    def extract_text(self, image_path):
        """Extracts text from an image file."""
        try:
            if not os.path.exists(image_path):
                return None, "File not found"
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text, None
        except Exception as e:
            return None, str(e)

    def extract_from_bytes(self, image_bytes):
        """Extracts text from image bytes (useful for Streamlit uploads)."""
        try:
            import io
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text, None
        except Exception as e:
            return None, str(e)

ocr_engine = OCREngine()
