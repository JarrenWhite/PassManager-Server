from flask import Blueprint, jsonify, request
import logging
logger = logging.getLogger("api")

from services.user_service import begin_user_registration, complete_user_registration, get_user_key, user_delete


user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/newkey', methods=['POST'])
def begin_user_registration_endpoint():
    """Request a secret key to begin user registration"""

    logger.info("begin_user_registration_endpoint: Called")
    result, status_code = begin_user_registration()
    logger.info(f"begin_user_registration_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@user_bp.route('/create', methods=['POST'])
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

@user_bp.route('/fetchkey', methods=['POST'])
def user_auth_endpoint():
    """Authorise a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("user_auth_endpoint: Called")
    result, status_code = get_user_key(data)
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

@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    logger.info("health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'user-api'
    }), 200
