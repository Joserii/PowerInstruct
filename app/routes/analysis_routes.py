from flask import Blueprint, jsonify, request
from app.services.analysis_service import AnalysisService
from utils.logger import logger

bp = Blueprint('analysis', __name__)
analysis_service = AnalysisService()

@bp.route('/clean', methods=['POST'])
def data_cleaning():
    try:
        return analysis_service.data_cleaning(request.json)
    except Exception as e:
        logger.error(f"Data cleaning failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': str(e)}), 500


@bp.route('/analyze', methods=['POST'])
def analyze_fault():
    try:
        return analysis_service.analyze_fault(request.json)
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': str(e)}), 500

@bp.route('/execute', methods=['POST'])
def execute_code():
    try:
        return analysis_service.execute_batch(request.json)
    except Exception as e:
        return jsonify({'code': 500, 'success': False, 'error': str(e)})

    

# routes.py
@bp.route('/merge_template', methods=['POST'])
def merge_template():
    try:
        data = request.get_json()
        raw_data = data.get('raw_content')
        seed_content = data.get('seed_content')
        template = data.get('template')
        
        if not seed_content or not template:
            return jsonify({
                'code': 400,
                'message': 'Missing required parameters'
            }), 400

        # 调用模板合并服务
        merged_content = analysis_service.merge_codegen_template(raw_data, seed_content, template)
        
        return jsonify({
            'code': 200,
            'merged_content': merged_content
        })
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        }), 500
