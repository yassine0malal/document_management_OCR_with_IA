# ocr_module.py
import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
from pdf2image import convert_from_path
import matplotlib.pyplot as plt 
# -----------------------------
# CONFIGURATION
# -----------------------------
# Path to Tesseract binary (only if needed)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

# Language for OCR
OCR_LANG = "eng"  # change to "eng" for English

# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

def preprocess_image(image_path):
    """
    Load an image and apply preprocessing for better OCR
    """
    # Load image in grayscale
    gray = cv2.imread(image_path, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)

    
    # Resize for better OCR (optional)
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    
    # Apply thresholding
    _, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
    
    # Remove noise
    img = cv2.medianBlur(img, 3)
    
    return img

def ocr_image(image_path):
    """
    Extract text from a single image
    """
    preprocessed_img = preprocess_image(image_path)
    # Convert OpenCV image to PIL Image
    pil_img = Image.fromarray(preprocessed_img)
    text = pytesseract.image_to_string(pil_img, lang=OCR_LANG)
    return text

def ocr_pdf(pdf_path, output_folder="temp_images"):
    """
    Extract text from a PDF file
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert PDF pages to images
    pages = convert_from_path(pdf_path, 300)
    full_text = ""

    for i, page in enumerate(pages):
        image_file = os.path.join(output_folder, f"page_{i}.jpg")
        page.save(image_file, "JPEG")
        page_text = ocr_image(image_file)
        full_text += page_text + "\n"

    return full_text

# -----------------------------
# EXAMPLE USAGE
# -----------------------------
if __name__ == "__main__":
    # Test with an image
    image_text = ocr_image("./images/1.jpeg")
    print("Text from image:")
    print(image_text)

    # Test with a PDF
    # pdf_text = ocr_pdf("./images/2.pdf")
    # print("Text from PDF:")
    # print(pdf_text)
