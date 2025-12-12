from flask import Blueprint, jsonify, request

import logging
logger = logging.getLogger("api")

from services import ServiceSession


session_bp = Blueprint('user', __name__, url_prefix='/api/session')


@session_bp.route('/start', methods=['POST'])
def start():
    """Start the process to create a login session"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Start: Called")
    result, status_code = ServiceSession.start(data)
    logger.info(f"Start complete: {status_code}")
    return jsonify(result), status_code


@session_bp.route('/auth', methods=['POST'])
def auth():
    """Complete the process to create a login session"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Auth: Called")
    result, status_code = ServiceSession.auth(data)
    logger.info(f"Auth complete: {status_code}")
    return jsonify(result), status_code


@session_bp.route('/delete', methods=['POST'])
def delete():
    """Delete an existing login session"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Delete: Called")
    result, status_code = ServiceSession.delete(data)
    logger.info(f"Delete complete: {status_code}")
    return jsonify(result), status_code


@session_bp.route('/clean', methods=['POST'])
def clean():
    """Delete all existing login sessions for the user"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Clean: Called")
    result, status_code = ServiceSession.clean(data)
    logger.info(f"Clean complete: {status_code}")
    return jsonify(result), status_code


@session_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    logger.debug("Session health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
