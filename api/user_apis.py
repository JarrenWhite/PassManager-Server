from flask import Blueprint, jsonify, request

# Create a Blueprint for user-related API routes
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/hello', methods=['POST'])
def hello_world():
    """Simple test endpoint that accepts data in request body and returns it in a JSON response"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    return jsonify({
        'message': 'Hello World!',
        'data': data,
        'status': 'success'
    })

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-api'
    })
