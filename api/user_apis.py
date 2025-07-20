from flask import Blueprint, jsonify, request

# Create a Blueprint for user-related API routes
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/hello', methods=['GET'])
def hello_world():
    """Simple test endpoint that accepts arguments and returns them in a JSON response"""
    args = dict(request.args)
    message = request.args.get('message', 'Hello World!')

    return jsonify({
        'message': message,
        'arguments': args,
        'status': 'success'
    })

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-api'
    })
