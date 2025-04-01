from pathlib import Path
import os
# Get the project root directory
BASE_DIR = Path(__file__).parent.parent

# save the system prompts
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'data', 'system_prompt')
TEMPLATE_FILE = os.path.join(TEMPLATE_FOLDER, "user_templates.json")

# Set various directory paths
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
TEST_DATA_FOLDER = os.path.join(BASE_DIR, 'data', 'test_data')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'output')
LOGS_FOLDER = os.path.join(BASE_DIR, 'logs')