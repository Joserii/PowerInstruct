import os
from app import create_app
from config.settings import LOGS_FOLDER, OUTPUT_FOLDER

# Make sure necessary directories exist
os.makedirs(LOGS_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
