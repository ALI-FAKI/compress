import os
import pyzipper


def compress_and_encrypt(file_paths, output_path, password=None):
    """Compresses and securely encrypts files and folders using AES-256."""
    # Use AES encryption if a password is provided, otherwise store normally
    encryption = pyzipper.WZ_AES if password else pyzipper.ZIP_STORED
    
    with pyzipper.AESZipFile(
        output_path,
        'w',
        compression=pyzipper.ZIP_DEFLATED,
        encryption=encryption
    ) as zf:
        if password:
            zf.pwd = password.encode('utf-8')
            
        for path in file_paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, os.path.dirname(path))
                        zf.write(full_path, rel_path)
            else:
                if os.path.isfile(path):
                    zf.write(path, arcname=os.path.basename(path))
                    
    return output_path


def extract_archive(archive_path, output_dir, password=None):
    """Safely extracts an AES-encrypted or standard zip archive."""
    try:
        with pyzipper.AESZipFile(archive_path, 'r') as zf:
            if password:
                zf.pwd = password.encode('utf-8')
            zf.extractall(path=output_dir)
        return True, "Extraction successful."
    except RuntimeError as re:
        err_msg = str(re).lower()
        if "password" in err_msg or "bad password" in err_msg or "encrypted" in err_msg:
            return False, "Incorrect password or password required!"
        return False, f"Failed: {re}"
    except Exception as e:
        return False, f"Failed: {e}"
