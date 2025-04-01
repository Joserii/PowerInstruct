import os
import json
from config.settings import BASE_DATA_FOLDER
from utils.logger import logger

def get_json_path(mode, error_type, example_id):
    """获取 JSON 文件路径"""
    if mode not in BASE_DATA_FOLDER:
        raise ValueError(f"Invalid mode: {mode}")

    base_path = BASE_DATA_FOLDER[mode]
    example_path = os.path.join(base_path, error_type, example_id)

    json_files = [os.path.join(example_path, f) for f in os.listdir(example_path) if f.endswith('.json')]
    
    if len(json_files) != 2:
        raise ValueError(f"Expected 2 JSON files, found {len(json_files)}")
    
    return json_files[0], json_files[1]

def load_json(file_path: str, encoding='utf-8'):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            json_data = json.load(f)
        return json_data
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        raise
    except IOError as e:
        logger.error(f"读取文件失败: {e}")
        raise

def load_record_waves(file_path: str, encoding='utf-8'):
    """加载录波文件"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            record_content = f.read()
        return record_content
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        raise
    except IOError as e:
        logger.error(f"读取文件失败: {e}")
        raise

def load_description(file_path: str, encoding='utf-8'):
    """加载描述文件"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            desc_content = f.read()
        return desc_content
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        raise
    except IOError as e:
        logger.error(f"读取文件失败: {e}")
        raise
