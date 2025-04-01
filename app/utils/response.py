from flask import jsonify

class Response:
    @staticmethod
    def success(data=None, message="Success"):
        response = {
            'code': 200,
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response)

    @staticmethod
    def error(message, code=500):
        return jsonify({
            'code': code,
            'success': False,
            'error': message
        }), code
