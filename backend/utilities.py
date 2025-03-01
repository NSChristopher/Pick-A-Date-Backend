from flask import jsonify

class Utility:
    @staticmethod
    def standardize_response(status='success', data=[], message="", code = 200):
        return {
            'status': status,
            'data': data,
            'message': message,
        }, code