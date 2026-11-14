import os
import tempfile
import pyzipper
from flask import Flask, render_template, request, send_file, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/encrypt', methods=['POST'])
def encrypt_archive():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    password = request.form.get('password', '').strip()
    
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    if not password:
        return jsonify({'error': 'Encryption password is required'}), 400

    # Use a temporary directory to handle files safely
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file.filename)
        file.save(input_path)
        
        output_zip = os.path.join(temp_dir, 'secure_archive.zip')
        
        # Encrypt with AES-256 using pyzipper
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


@app.route('/api/decrypt', methods=['POST'])
def decrypt_archive():
    if 'file' not in request.files:
        return jsonify({'error': 'No archive provided'}), 400
    
    file = request.files['file']
    password = request.form.get('password', '').strip()
    
    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    if not password:
        return jsonify({'error': 'Decryption password is required'}), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        archive_path = os.path.join(temp_dir, file.filename)
        file.save(archive_path)
        
        extract_dir = os.path.join(temp_dir, 'extracted')
        os.makedirs(extract_dir, exist_ok=True)
        
        try:
            with pyzipper.AESZipFile(archive_path, 'r') as zf:
                zf.pwd = password.encode('utf-8')
                zf.extractall(path=extract_dir)
            
            # Bundle extracted contents back into a clean zip for download
            output_zip = os.path.join(temp_dir, 'decrypted_files.zip')
            with pyzipper.AESZipFile(output_zip, 'w', compression=pyzipper.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(extract_dir):
                    for f in files:
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, extract_dir)
                        zf.write(full_p, rel_p)
                        
            return send_file(
                output_zip, 
                as_attachment=True, 
                download_name="decrypted_files.zip"
            )
            
        except RuntimeError:
            return jsonify({'error': 'Incorrect password or corrupted archive!'}), 400
        except Exception as e:
            return jsonify({'error': f'Failed to decrypt: {str(e)}'}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)
