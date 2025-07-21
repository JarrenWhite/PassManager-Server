from flask import Blueprint, jsonify, request
import logging
logger = logging.getLogger("api")

from services.user_service import user_register, user_auth, user_delete


user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/register', methods=['POST'])
def user_register_endpoint():
    """Register a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info(f"user_register_endpoint: Called")
    result, status_code = user_register(data)
    logger.info(f"user_register_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@user_bp.route('/auth', methods=['POST'])
def user_auth_endpoint():
    """Authorise a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info(f"user_auth_endpoint: Called")
    result, status_code = user_auth(data)
    logger.info(f"user_auth_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@user_bp.route('/delete', methods=['POST'])
def user_delete_endpoint():
    """Delete a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info(f"user_delete_endpoint: Called")
    result, status_code = user_delete(data)
    logger.info(f"user_delete_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@user_bp.route('/hello', methods=['POST'])
def hello_world():
    """Simple test endpoint that accepts data in request body and returns it in a JSON response"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info(f"hello_world: {data}")
    return jsonify({
        'message': 'Hello World!',
        'data': data,
        'status': 'success'
    }), 201

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    logger.info(f"health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'user-api'
    }), 201
