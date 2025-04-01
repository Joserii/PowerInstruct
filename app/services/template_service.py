from flask import jsonify
from utils.logger import logger
from config.settings import TEMPLATE_FILE
from utils.system_prompt import load_user_templates, save_user_templates

class TemplateService:
    def __init__(self):
        self.default_templates = load_user_templates() # 获取默认模板


    def get_templates(self):
        try:
            user_templates = load_user_templates() 
            if not user_templates:
                user_templates = self.default_templates

            return jsonify({
                'code': 200,
                'success': True,
                'templates': user_templates
            })
        except Exception as e:
            logger.error(f"Failed to load templates: {str(e)}", exc_info=True)
            return jsonify({
                'code': 500,
                'success': False,
                'error': str(e)
            })


    def validate_template(self, template_type, content):
        try:
            if not content or len(content.strip()) == 0:
                return False, "Template content cannot be empty"
            
            if template_type == 'prompt':
                if len(content) > 10000:
                    return False, "Prompt template too long"
            elif template_type == 'codegen':
                if "```python" not in content:
                    return False, "CodeGen template must contain Python code block"
                    
            return True, ""
            
        except Exception as e:
            return False, str(e)

    def save_template(self, data):
        try:
            template_content = data.get('content', '')
            template_type = data.get('type', 'prompt')

            is_valid, error_message = self.validate_template(template_type, template_content)
            if not is_valid:
                return jsonify({
                    'code': 400,
                    'success': False,
                    'message': f'Template validation failed: {error_message}'
                })

            templates = load_user_templates()
            templates[template_type] = template_content

            if save_user_templates(templates):
                return jsonify({
                    'code': 200,
                    'success': True,
                    'message': 'Template saved successfully'
                })
            else:
                return jsonify({
                    'code': 500,
                    'success': False,
                    'error': 'Failed to save template'
                })
        except Exception as e:
            logger.error(f"Failed to save template: {str(e)}", exc_info=True)
            return jsonify({
                'code': 500,
                'success': False,
                'error': str(e)
            })
