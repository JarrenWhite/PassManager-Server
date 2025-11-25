from flask import Blueprint, jsonify

import logging
logger = logging.getLogger("api")


user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    logger.debug("user health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
