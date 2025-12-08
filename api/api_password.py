from flask import Blueprint, jsonify, request

import logging
logger = logging.getLogger("api")

from services import ServicePassword


password_bp = Blueprint('user', __name__, url_prefix='/api/password')


@password_bp.route('/start', methods=['POST'])
def start():
    """Start the password change process"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Start: Called")
    result, status_code = ServicePassword.start(data)
    logger.info(f"Start complete: {status_code}")
    return jsonify(result), status_code


@password_bp.route('/auth', methods=['POST'])
def auth():
    """Finish creation of a password change session"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Auth: Called")
    result, status_code = ServicePassword.auth(data)
    logger.info(f"Auth complete: {status_code}")
    return jsonify(result), status_code


@password_bp.route('/complete', methods=['POST'])
def complete():
    """Complete an ongoing password change"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Complete: Called")
    result, status_code = ServicePassword.complete(data)
    logger.info(f"Complete complete: {status_code}")
    return jsonify(result), status_code


@password_bp.route('/abort', methods=['POST'])
def abort():
    """Abort an ongoing password change"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Abort: Called")
    result, status_code = ServicePassword.abort(data)
    logger.info(f"Abort complete: {status_code}")
    return jsonify(result), status_code


@password_bp.route('/get', methods=['POST'])
def get():
    """Get a data entry during an ongoing password change"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Get: Called")
    result, status_code = ServicePassword.get(data)
    logger.info(f"Get complete: {status_code}")
    return jsonify(result), status_code


@password_bp.route('/update', methods=['POST'])
def update():
    """Update a data entry during an ongoing password change"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Update: Called")
    result, status_code = ServicePassword.update(data)
    logger.info(f"Update complete: {status_code}")
    return jsonify(result), status_code


@password_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the password API"""
    logger.debug("Password health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
