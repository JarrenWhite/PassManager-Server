from flask import Blueprint, jsonify, request
import logging
logger = logging.getLogger("api")

from services.session_service import session_create, session_auth, session_delete, session_delete_all


session_bp = Blueprint('session', __name__, url_prefix='/api/session')

@session_bp.route('/create', methods=['POST'])
def session_create_endpoint():
    """Create a session for a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("session_create_endpoint: Called")
    result, status_code = session_create(data)
    logger.info(f"session_create_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@session_bp.route('/auth', methods=['POST'])
def session_auth_endpoint():
    """Get a user from a session"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("session_auth_endpoint: Called")
    result, status_code = session_auth(data)
    logger.info(f"session_auth_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@session_bp.route('/delete', methods=['POST'])
def session_delete_endpoint():
    """Delete a given session"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("session_delete_endpoint: Called")
    result, status_code = session_delete(data)
    logger.info(f"session_delete_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@session_bp.route('/clean', methods=['POST'])
def session_delete_all_endpoint():
    """Delete all sessions for a given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.info("session_delete_all_endpoint: Called")
    result, status_code = session_delete_all(data)
    logger.info(f"session_delete_all_endpoint: Complete with status code: {status_code}")
    return jsonify(result), status_code

@session_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    logger.info("session health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'session-api'
    }), 200
