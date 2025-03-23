# app/routes.py
from flask import Blueprint, request, render_template
import os
from .ocr import process_file

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files and 'marks' not in request.form:
            return render_template('index.html', error='No file uploaded')
        
        # Handle file upload and initial OCR
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return render_template('index.html', error='No file selected')
            
            upload_folder = 'app/static/uploads'
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)
            
            try:
                marks, total, processed_filename = process_file(filepath, file_ext, upload_folder)
                if not marks:
                    return render_template('index.html', 
                                        error='No marks detected',
                                        processed_filename=processed_filename)
                return render_template('index.html', 
                                    marks=marks, 
                                    total=total, 
                                    processed_filename=processed_filename,
                                    edit_mode=True)
            except Exception as e:
                return render_template('index.html', error=f'Error processing file: {str(e)}')
        
        # Handle mark editing
        elif 'marks' in request.form:
            try:
                marks = [int(m) for m in request.form.getlist('marks') if m.strip()]
                total = sum(marks)
                processed_filename = request.form.get('processed_filename')
                return render_template('index.html', 
                                    marks=marks, 
                                    total=total, 
                                    processed_filename=processed_filename,
                                    edit_mode=False)
            except ValueError:
                return render_template('index.html', error='Invalid mark values')
    
    return render_template('index.html')