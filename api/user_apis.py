from flask import Blueprint, jsonify

# Create a Blueprint for user-related API routes
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/hello', methods=['GET'])
def hello_world():
    """Simple test endpoint that prints 'Hello World!' and returns a JSON response"""
    print('Hello World!')
    return jsonify({
        'message': 'Hello World!',
        'status': 'success'
    })

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-api'
    })
