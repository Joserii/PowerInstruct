from flask import Blueprint, jsonify, request, send_from_directory
from app.services.file_service import FileService
from utils.logger import logger
from config.settings import TEMPLATE_FOLDER


bp = Blueprint('file', __name__)
file_service = FileService()

@bp.route('/')
def index():
    return send_from_directory(TEMPLATE_FOLDER, 'index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        return file_service.handle_file_upload(request)
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/upload_zip', methods=['POST'])
def upload_zip():
    try:
        return file_service.handle_zip_upload(request)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/delete_file/<path:file_path>', methods=['DELETE'])
def delete_file(file_path):
    try:
        return file_service.handle_file_deletion(file_path)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

@bp.route('/api/json-content', methods=['GET'])
def load_json_batch():
    try:
        return file_service.load_json_batch()
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
