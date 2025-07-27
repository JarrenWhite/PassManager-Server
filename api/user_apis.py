from flask import Blueprint, jsonify, request
import logging
logger = logging.getLogger("api")

from services.user_service import begin_user_registration, complete_user_registration, user_auth, user_delete


user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/begin', methods=['POST'])
def begin_user_registration_endpoint():
    """Request a secret key to begin user registration"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("begin_user_registration_endpoint: Called")
    result, status_code = begin_user_registration(data)
    logger.info(f"begin_user_registration_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@user_bp.route('/complete', methods=['POST'])
def complete_user_registration_endpoint():
    """Register a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("complete_user_registration_endpoint: Called")
    result, status_code = complete_user_registration(data)
    logger.info(f"complete_user_registration_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@user_bp.route('/auth', methods=['POST'])
def user_auth_endpoint():
    """Authorise a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("user_auth_endpoint: Called")
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

    logger.info("user_delete_endpoint: Called")
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
    }), 200

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    logger.info("health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'user-api'
    }), 200
