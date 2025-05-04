import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

def preprocess_image(image_path):
    """
    Preprocess the image to remove watermarks and enhance text for OCR.
    """
    # Load the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply adaptive thresholding
    processed_img = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
    )

    # Optional: Apply morphological operations to clean noise
    kernel = np.ones((1, 1), np.uint8)
    processed_img = cv2.morphologyEx(processed_img, cv2.MORPH_CLOSE, kernel)

    # Save the processed image (for debugging)
    cv2.imwrite("processed_image.jpg", processed_img)

    return processed_img

def extract_text(image_path):
    """
    Perform OCR on the preprocessed image and filter the question.
    """
    # Preprocess the image
    processed_img = preprocess_image(image_path)

    # Perform OCR using pytesseract
    ocr_text = pytesseract.image_to_string(processed_img)

    # Use a regex pattern to extract the question
    pattern = r"Read each of the sentences.+?(She.*?weeks\.)"
    match = re.search(pattern, ocr_text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return "❌ Could not find the relevant question in the image."

# Example usage
image_path = "image_with_watermark.jpeg"  # Replace with your image path
question = extract_text(image_path)
print("Extracted Question:", question)
