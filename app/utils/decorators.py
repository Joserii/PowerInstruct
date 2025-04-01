from functools import wraps
from flask import request, jsonify
from utils.logger import logger

def require_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function

def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Request to {request.path}: {request.get_json() if request.is_json else request.args}")
        return f(*args, **kwargs)
    return decorated_function
