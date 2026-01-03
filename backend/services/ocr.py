import pytesseract
from PIL import Image
import io

class OCREngine:
    def extract_from_bytes(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip(), None
        except Exception as e:
            return "", str(e)

ocr_service = OCREngine()
