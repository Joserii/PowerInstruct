from datetime import datetime
import os
import json

def allowed_single_file(filename):
    """
    检查文件扩展名是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'json', 'xml', 'txt'}

def allowed_zip_file(filename):
    """
    检查文件扩展名是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'zip', 'rar', '7z'}

def generate_unique_filename(filename, existing_extension=None):
    """
    生成唯一文件名
    """
    # 获取文件扩展名
    name, ext = os.path.splitext(filename)    
    if existing_extension:
        ext = existing_extension if existing_extension.startswith('.') else f'.{existing_extension}'
    
    # 生成带时间戳的唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{name}_{timestamp}_{os.urandom(8).hex()}{ext}"
    
    return unique_filename


# 可以添加一个辅助函数来验证文件路径
def is_safe_file_path(file_path, base_directory):
    """
    验证文件路径是否安全
    
    Args:
        file_path (str): 要验证的文件路径
        base_directory (str): 基础目录路径

    Returns:
        bool: 如果路径安全返回True，否则返回False
    """
    try:
        normalized_path = os.path.normpath(os.path.join(base_directory, file_path))
        normalized_base = os.path.normpath(base_directory)
        return normalized_path.startswith(normalized_base)
    except Exception:
        return False


def load_json(file_path):
    """
    从JSON文件加载数据
    
    Args:
        file_path (str): JSON文件路径

    Returns:
        dict: 从JSON文件中加载的数据
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)