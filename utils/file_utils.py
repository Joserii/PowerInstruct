from datetime import datetime
import os
import json

def allowed_single_file(filename):
    """
    Check if the file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'json', 'xml', 'txt'}

def allowed_zip_file(filename):
    """
    Check if the file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'zip', 'rar', '7z'}

def generate_unique_filename(filename, existing_extension=None):
    """
    Generate unique file names
    """
    name, ext = os.path.splitext(filename)    
    if existing_extension:
        ext = existing_extension if existing_extension.startswith('.') else f'.{existing_extension}'
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{name}_{timestamp}_{os.urandom(8).hex()}{ext}"
    
    return unique_filename


def is_safe_file_path(file_path, base_directory):
    try:
        normalized_path = os.path.normpath(os.path.join(base_directory, file_path))
        normalized_base = os.path.normpath(base_directory)
        return normalized_path.startswith(normalized_base)
    except Exception:
        return False


def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)