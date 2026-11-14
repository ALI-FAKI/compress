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
    
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    if not password:
        return jsonify({'error': 'Password is required to lock the file'}), 400

    # Use a temporary directory for safe server-side processing
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file.filename)
        file.save(input_path)
        
        output_zip = os.path.join(temp_dir, 'secure_package.zip')
        
        # Compress and encrypt using AES-256 (WZ_AES) via pyzipper
        with pyzipper.AESZipFile(
            output_zip, 
            'w', 
            compression=pyzipper.ZIP_DEFLATED, 
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
