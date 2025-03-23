# app/ocr.py
import cv2
import pytesseract
import numpy as np
from PIL import Image
import os
from pdf2image import convert_from_path

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows

def process_image(image, output_path=None):
    try:
        # Convert to OpenCV format
        img = np.array(image)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Noise reduction
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive thresholding for better contrast
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # OCR
        text = pytesseract.image_to_string(thresh, config='--psm 6')  # PSM 6 for block of text
        print(f"Extracted text: {text}")
        
        # Extract numbers
        marks = []
        for line in text.split('\n'):
            numbers = [int(s) for s in line.split() if s.isdigit()]
            marks.extend(numbers)
        
        total = sum(marks) if marks else 0
        
        if output_path:
            cv2.imwrite(output_path, thresh)
        
        return marks, total
    except Exception as e:
        print(f"Error in process_image: {str(e)}")
        return [], 0

def process_file(file_path, file_type, output_folder):
    try:
        processed_filename = 'processed_' + os.path.basename(file_path)
        processed_path = os.path.join(output_folder, processed_filename)
        
        if file_type == 'pdf':
            images = convert_from_path(file_path)
            all_marks = []
            for i, img in enumerate(images):
                marks, _ = process_image(img, processed_path if i == 0 else None)
                all_marks.extend(marks)
            total = sum(all_marks) if all_marks else 0
            return all_marks, total, processed_filename if os.path.exists(processed_path) else None
        else:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Could not load image")
            marks, total = process_image(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), processed_path)
            return marks, total, processed_filename
    except Exception as e:
        print(f"Error in process_file: {str(e)}")
        return [], 0, None