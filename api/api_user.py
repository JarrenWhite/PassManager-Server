from flask import Blueprint, jsonify, request

import logging
logger = logging.getLogger("api")

from services import ServiceUser


user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Register: Called")
    result, status_code = ServiceUser.register(data)
    logger.info(f"Register complete with code: {status_code}")
    return jsonify(result), status_code


@user_bp.route('/username', methods=['POST'])
def username():
    """Change username"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Username: Called")
    result, status_code = ServiceUser.username(data)
    logger.info(f"Username complete with code: {status_code}")
    return jsonify(result), status_code


@user_bp.route('/delete', methods=['POST'])
def delete():
    """Delete user"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Delete: Called")
    result, status_code = ServiceUser.delete(data)
    logger.info(f"Delete complete with code: {status_code}")
    return jsonify(result), status_code


@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    logger.debug("User health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
