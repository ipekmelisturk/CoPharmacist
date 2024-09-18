# Image to text using tesseract OCR
import cv2
import pytesseract
from PIL import Image

# Define the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Adjust based on your OS

def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, config='--psm 11')  # '--psm 11' for handwriting
    return text

# Example usage
text = extract_text("14.jpg")
print(text)

