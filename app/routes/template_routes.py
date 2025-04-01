from flask import Blueprint, request
from app.services.template_service import TemplateService

bp = Blueprint('template', __name__)
template_service = TemplateService()

@bp.route('/templates', methods=['GET'])
def get_templates():
    return template_service.get_templates()

@bp.route('/save_template', methods=['POST'])
def save_template():
    return template_service.save_template(request.json)
