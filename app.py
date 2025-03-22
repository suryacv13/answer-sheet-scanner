# app.py
from flask import Flask, request, render_template
import cv2
import pytesseract
import numpy as np
from PIL import Image
import os
from pdf2image import convert_from_path
import tempfile

app = Flask(__name__)

# Configure Tesseract path (update this based on your installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# For Linux/Mac: '/usr/local/bin/tesseract' or appropriate path

def process_image(image, output_path=None):
    # Convert PIL image to OpenCV format
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Extract text
    text = pytesseract.image_to_string(thresh)
    
    # Extract numbers (marks)
    marks = []
    for line in text.split('\n'):
        numbers = [int(s) for s in line.split() if s.isdigit()]
        marks.extend(numbers)
    
    total = sum(marks) if marks else 0
    
    # Save processed image if output_path is provided
    if output_path:
        cv2.imwrite(output_path, thresh)
    
    return marks, total

def process_file(file_path, file_type, output_folder):
    processed_filename = 'processed_' + os.path.basename(file_path)
    processed_path = os.path.join(output_folder, processed_filename)
    
    if file_type == 'pdf':
        # Convert PDF to images
        images = convert_from_path(file_path)
        all_marks = []
        for i, img in enumerate(images):
            marks, _ = process_image(img, processed_path if i == 0 else None)  # Save only first page
            all_marks.extend(marks)
        total = sum(all_marks) if all_marks else 0
        return all_marks, total, processed_filename if os.path.exists(processed_path) else None
    else:  # image file
        img = cv2.imread(file_path)
        marks, total = process_image(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), processed_path)
        return marks, total, processed_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file uploaded')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No file selected')
        
        if file:
            upload_folder = 'static/uploads'  # Changed to static for serving
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            # Save uploaded file
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)
            
            try:
                marks, total, processed_filename = process_file(filepath, file_ext, upload_folder)
                return render_template('index.html', 
                                    marks=marks, 
                                    total=total, 
                                    processed_filename=processed_filename)
            except Exception as e:
                return render_template('index.html', error=f'Error processing file: {str(e)}')
    
    return render_template('index.html')

# app.py (end of file)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from env, default to 5000 locally
    app.run(host='0.0.0.0', port=port, debug=False)  # Bind to 0.0.0.0 for external access