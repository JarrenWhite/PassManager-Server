from flask import Blueprint, jsonify

import logging
logger = logging.getLogger("api")


session_bp = Blueprint('user', __name__, url_prefix='/session/user')


@session_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    logger.debug("session health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
