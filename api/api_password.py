from flask import Blueprint, jsonify

import logging
logger = logging.getLogger("api")


password_bp = Blueprint('user', __name__, url_prefix='/api/password')


@password_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the password API"""
    logger.debug("Password health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
