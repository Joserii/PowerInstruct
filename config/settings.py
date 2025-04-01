from pathlib import Path
import os
# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent

# 配置文件
BASE_DATA_FOLDER = {
    'train': os.path.join(BASE_DIR, 'data', '1049个训练样本-1016'),
    'test': os.path.join(BASE_DIR, 'data', '102个测试样本-1015'),
}
# save the system prompts
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'data', 'system_prompt')
TEMPLATE_FILE = os.path.join(TEMPLATE_FOLDER, "user_templates.json")

# 设置各种目录路径
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
TEST_DATA_FOLDER = os.path.join(BASE_DIR, 'data', 'test_data')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')