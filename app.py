import os
import shutil
import logging
import tempfile
from flask import (
    Flask, render_template, request, send_file, jsonify
)
import pyzipper

app = Flask(__name__)

# Hard cap on upload size (bytes). Adjust if you allow larger files.
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB

ALLOWED_COMPRESSION = {'deflate', 'none'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    name = os.path.basename(name or '').strip()
    name = ''.join(ch for ch in name if ch.isprintable())
    if not name:
        name = 'file'
    return name[:180]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/create-secure-zip', methods=['POST'])
def create_secure_zip():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    # Never strip/normalize the password — every byte matters.
    password = request.form.get('password', '')
    compression_mode = request.form.get('compression', 'deflate').lower()

    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    # Only requirement: password must be non-empty.
    if not password:
        return jsonify({'error': 'Password is required to lock the file'}), 400

    if compression_mode not in ALLOWED_COMPRESSION:
        compression_mode = 'deflate'

    safe_name = sanitize_filename(file.filename)
    download_name = f"{safe_name}.secure.zip"

    compression_method = (
        pyzipper.ZIP_STORED if compression_mode == 'none'
        else pyzipper.ZIP_DEFLATED
    )

    tmp = tempfile.NamedTemporaryFile(
        mode='wb', suffix='.zip', prefix='securevault-', delete=False
    )
    tmp_path = tmp.name
    tmp.close()

    try:
        with pyzipper.AESZipFile(
            tmp_path,
            'w',
            compression=compression_method,
            encryption=pyzipper.WZ_AES,
        ) as zf:
            zf.pwd = password.encode('utf-8')
            with zf.open(safe_name, 'w') as dest:
                shutil.copyfileobj(file.stream, dest)
    except Exception:
        logger.exception('Encryption failed for upload %r', safe_name)
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return jsonify({'error': 'Encryption failed. Please try again.'}), 500

    response = send_file(
        tmp_path,
        as_attachment=True,
        download_name=download_name,
        mimetype='application/zip',
    )
    response.call_on_close(lambda: _safe_remove(tmp_path))
    return response


def _safe_remove(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


@app.errorhandler(413)
def too_large(_e):
    return jsonify({
        'error': 'File is too large. Maximum size is 200 MB.'
    }), 413


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=debug,
    )
