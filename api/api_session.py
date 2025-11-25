from flask import Blueprint, jsonify

import logging
logger = logging.getLogger("api")


session_bp = Blueprint('user', __name__, url_prefix='/api/session')


@session_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    logger.debug("Session health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
