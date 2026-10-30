import os
import zipfile


def compress_and_encrypt(file_paths, output_path, password=None):
    """Compresses files and folders into a standard zip archive safely on Android and PC."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
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
    """Extracts a zip archive safely, supporting optional password protection."""
    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            if password:
                zf.setpassword(password.encode('utf-8'))
            zf.extractall(path=output_dir)
        return True, "Extraction successful."
    except RuntimeError as re:
        if "password" in str(re).lower():
            return False, "Incorrect password or password required!"
        return False, f"Failed: {re}"
    except Exception as e:
        return False, f"Failed: {e}"
