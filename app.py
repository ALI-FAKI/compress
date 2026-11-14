import os
import tempfile
import pyzipper
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/create-secure-zip', methods=['POST'])
def create_secure_zip():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    password = request.form.get('password', '').strip()
    compression_mode = request.form.get('compression', 'deflate')  # 'store' or 'deflate'
    
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    if not password:
        return jsonify({'error': 'Password is required to lock the file'}), 400

    # Choose compression algorithm based on user selection
    # ZIP_STORED = No compression (Fast, good for large media files)
    # ZIP_DEFLATED = Standard compression (Smaller file size)
    compression_method = pyzipper.ZIP_STORED if compression_mode == 'none' else pyzipper.ZIP_DEFLATED

    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file.filename)
        file.save(input_path)
        
        output_zip = os.path.join(temp_dir, 'secure_package.zip')
        
        # Create AES-256 encrypted archive with selected compression
        with pyzipper.AESZipFile(
            output_zip, 
            'w', 
            compression=compression_method, 
            encryption=pyzipper.WZ_AES
        ) as zf:
            zf.pwd = password.encode('utf-8')
            zf.write(input_path, arcname=file.filename)
        
        return send_file(
            output_zip, 
            as_attachment=True, 
            download_name=f"{file.filename}.secure.zip"
        )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
