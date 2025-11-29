from flask import Blueprint, jsonify, request

import logging
logger = logging.getLogger("api")

from services import ServiceUser


user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/register', methods=['POST'])
def user_register():
    """Register a new user"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("Register new user: Called")
    result, status_code = ServiceUser.user_register(data)
    logger.info(f"Register new user: Complete with status code: {status_code}")
    return jsonify(result), status_code


@user_bp.route('/username', methods=['POST'])
def user_username():
    """Change username"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("Change username: Called")
    result, status_code = ServiceUser.user_username(data)
    logger.info(f"Change username: Complete with status code: {status_code}")
    return jsonify(result), status_code


@user_bp.route('/delete', methods=['POST'])
def user_delete():
    """Delete user"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("Delete user: Called")
    result, status_code = ServiceUser.user_delete(data)
    logger.info(f"Delete user: Complete with status code: {status_code}")
    return jsonify(result), status_code


@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the user API"""
    logger.debug("User health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
