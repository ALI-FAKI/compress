import py7zr
import os


def compress_and_encrypt(file_paths, output_path, password=None):
    kwargs = {"filters": [{"id": py7zr.FILTER_LZMA2, "preset": 7}]}
    if password:
        kwargs["password"] = password
        kwargs["header_encryption"] = True

    with py7zr.SevenZipFile(output_path, 'w', **kwargs) as archive:
        for path in file_paths:
            if os.path.isdir(path):
                archive.writeall(path, arcname=os.path.basename(path))
            else:
                archive.write(path, arcname=os.path.basename(path))
    return output_path


def extract_archive(archive_path, output_dir, password=None):
    try:
        with py7zr.SevenZipFile(archive_path, 'r', password=password) as archive:
            archive.extractall(path=output_dir)
        return True, "Extraction successful."
    except py7zr.exceptions.PasswordRequired:
        return False, "Password required!"
    except Exception as e:
        return False, f"Failed: {e}"
