import pytesseract
from PIL import Image
import io
import os
import logging

class OCREngine:
    def deskew_image(self, image):
        """Redresse une image si elle est inclinée (Deskewing)."""
        try:
            import cv2
            import numpy as np
            
            # Convert PIL to OpenCV
            open_cv_image = np.array(image.convert('RGB')) 
            # Convert RGB to BGR 
            open_cv_image = open_cv_image[:, :, ::-1].copy() 
            
            # Convert to gray
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            # Flip colors (foreground must be white)
            gray = cv2.bitwise_not(gray)
            
            # Thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # Find coordinates of all non-zero pixels
            coords = np.column_stack(np.where(thresh > 0))
            
            # Min Area Rect
            angle = cv2.minAreaRect(coords)[-1]
            
            # Adjust angle
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            logging.info(f"Deskew: Angle détecté = {angle:.2f} degrés")
            
            # Correction si l'angle est significatif (> 0.5 deg)
            if abs(angle) > 0.5:
                (h, w) = open_cv_image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(open_cv_image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                
                # Convert back to PIL
                return Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))
            
            return image
            
        except Exception as e:
            logging.warning(f"Deskew failed: {e}")
            return image

    def enhance_image(self, image, method='soft'):
        """Améliore l'image pour l'OCR.
        - method='soft': Grayscale + Denoise (Idéal pour CVs modernes, fonds colorés).
        - method='hard': + Adaptive Threshold (Idéal pour scans N&B, reçus).
        """
        try:
            import cv2
            import numpy as np
            
            # Convert PIL to OpenCV
            img_np = np.array(image.convert('RGB'))
            
            # 1. Conversion Niveaux de Gris
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            
            # 2. Mise à l'échelle si trop petit (Upscaling)
            height, width = gray.shape
            if width < 1500 or height < 1500:
                scale = 2.0
                gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                logging.debug(f"Image upscaled by {scale}")
            
            # 3. Réduction du bruit (Denoising)
            denoised = cv2.fastNlMeansDenoising(gray, None, 5, 7, 21)
            
            # 4. Mode Hard : Binarisation forcée
            if method == 'hard':
                return Image.fromarray(cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2))
            
            # Mode Soft (Défaut) : On laisse Tesseract gérer le seuillage
            return Image.fromarray(denoised)
            
        except Exception as e:
            logging.warning(f"Image enhancement failed: {e}")
            return image

    def extract_from_bytes(self, file_bytes, filename=""):
        """V5: Extraction ultra-robuste avec pypdf (Texte) + Deskewing + OCR."""
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
                
                # --- NOUVEAU: Correction de rotation ---
                # DISABLED: Deskew is causing -90 degree rotation on upright documents
                # image = self.deskew_image(image)
                
                # --- TENTATIVE A: Mode Soft (Grayscale) ---
                # Idéal pour les documents nés numériques ou avec fond coloré
                img_soft = self.enhance_image(image, method='soft')
                text = pytesseract.image_to_string(img_soft, lang='fra+eng')
                
                # --- TENTATIVE B: Mode Hard (Threshold) ---
                # Si le mode Soft échoue (texte vide ou trop court), on tente le mode Hard
                # Idéal pour les scans papiers, tickets de caisse, faible contraste
                if not text or len(text.strip()) < 10:
                    logging.info("OCR Soft insuffisant, tentative mode Hard...")
                    img_hard = self.enhance_image(image, method='hard')
                    text_hard = pytesseract.image_to_string(img_hard, lang='fra+eng')
                    
                    # On garde le Hard seulement s'il a trouvé quelque chose
                    if text_hard and len(text_hard.strip()) > len(text.strip()):
                        text = text_hard

                if text and len(text.strip()) >= 2:
                    return text.strip(), None
                
                # --- DEBUG : SAUVEGARDE IMAGE ECHEC ---
                debug_filename = f"uploads/debug_ocr_fail_{os.path.basename(filename) if filename else 'unknown'}.png"
                logging.warning(f"Image OCR vide. Sauvegarde debug : {debug_filename}")
                image.save(debug_filename)
                
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
                            # --- NOUVEAU: Correction de rotation par page ---
                            # DISABLED: Deskew is causing -90 degree rotation
                            # img = self.deskew_image(img)
                            img = self.enhance_image(img)
                            texts.append(pytesseract.image_to_string(img, lang='fra+eng'))
                        result = "\n".join(texts).strip()
                        if result:
                            return result, None
                        else:
                            return "", "[V5] PDF détecté mais illisible par OCR."
                except Exception as e_pdf:
                    return "", f"[V5] Erreur OCR PDF (Poppler) : {str(e_pdf)}"

            return "", f"[V5] Format non reconnu ou texte manquant. (Source: {filename})"

        except Exception as e_final:
            return "", f"[V5] Erreur Critique OCR : {str(e_final)}"

ocr_service = OCREngine()
