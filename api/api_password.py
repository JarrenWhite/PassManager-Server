from flask import Blueprint, jsonify

import logging
logger = logging.getLogger("api")


password_bp = Blueprint('user', __name__, url_prefix='/password/user')


@password_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    logger.debug("password health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
