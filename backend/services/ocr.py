import pytesseract
from PIL import Image
import io
import os
import logging

class OCREngine:
    def extract_from_bytes(self, file_bytes, filename=""):
        """V4: Extraction ultra-robuste avec pypdf (Texte) + pdf2image (OCR)."""
        try:
            # --- TENTATIVE 1 : PDF (TEXTE DIRECT) ---
            is_pdf = file_bytes.startswith(b'%PDF') or (filename and filename.lower().endswith('.pdf'))
            if is_pdf:
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(io.BytesIO(file_bytes))
                    text_content = ""
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_content += extracted + "\n"
                    
                    if len(text_content.strip()) > 30: # Seuil relevé pour assurer une qualité minimum
                        return text_content.strip(), None
                    logging.debug("PDF texte vide ou scanné, passage à l'OCR...")
                except Exception as e_pypdf:
                    logging.debug(f"Pypdf failed: {e_pypdf}")

            # --- TENTATIVE 2 : IMAGE (PIL) ---
            try:
                img_io = io.BytesIO(file_bytes)
                image = Image.open(img_io)
                
                # Conversion cruciale pour les PNG transparents (ex: remove-bg)
                if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                    background = Image.new("RGB", image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[3]) # 3 is the alpha channel
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                text = pytesseract.image_to_string(image, lang='fra+eng')
                if text and len(text.strip()) >= 2: # Seuil réduit pour capture plus large
                    return text.strip(), None
                logging.debug("Image OCR vide ou trop courte.")
            except Exception as e_img:
                logging.error(f"Tentative Image échouée : {str(e_img)}")

            # --- TENTATIVE 3 : PDF (OCR COMPLET) ---
            if is_pdf:
                try:
                    from pdf2image import convert_from_bytes
                    # DPI 300 pour une précision maximale au détriment de la vitesse
                    images = convert_from_bytes(file_bytes, dpi=300)
                    if images:
                        texts = []
                        for img in images:
                            texts.append(pytesseract.image_to_string(img, lang='fra+eng'))
                        result = "\n".join(texts).strip()
                        if result:
                            return result, None
                        else:
                            return "", "[V4] PDF détecté mais illisible par OCR."
                except Exception as e_pdf:
                    return "", f"[V4] Erreur OCR PDF (Poppler) : {str(e_pdf)}"

            return "", f"[V4] Format non reconnu ou texte manquant. (Source: {filename})"

        except Exception as e_final:
            return "", f"[V4] Erreur Critique OCR : {str(e_final)}"

ocr_service = OCREngine()
