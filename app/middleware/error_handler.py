from flask import jsonify
from utils.logger import logger

class ErrorHandler:
    @staticmethod
    def register_handlers(app):
        @app.errorhandler(400)
        def bad_request(error):
            logger.error(f"Bad request: {error}")
            return jsonify({'error': 'Bad Request', 'message': str(error)}), 400

        @app.errorhandler(404)
        def not_found(error):
            logger.error(f"Resource not found: {error}")
            return jsonify({'error': 'Not Found', 'message': str(error)}), 404

        @app.errorhandler(500)
        def internal_server_error(error):
            logger.error(f"Server error: {error}")
            return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500
