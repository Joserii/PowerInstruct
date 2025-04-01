import os
import json
from config.settings import *
from utils.logger import logger
from utils.prompt_template.directgen_prompt import datagen_1shot_system_prompt
from utils.prompt_template.codegen_prompt import codegen_1shot_system_prompt


def get_default_templates():
    """Get the default template"""
    return {
        'prompt': datagen_1shot_system_prompt(),
        'codegen': codegen_1shot_system_prompt()
    }


def load_user_templates():
    """Load the user-defined template, or return the default template if none"""
    try:
        templates = get_default_templates()
        return templates
    
    except Exception as e:
        logger.error(f"Error loading user templates: {e}")
        return get_default_templates()

def save_user_templates(templates):
    """Save user-defined templates"""
    try:
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user templates: {e}")
        return False
