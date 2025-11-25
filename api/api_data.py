from flask import Blueprint, jsonify

import logging
logger = logging.getLogger("api")


data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@data_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the data API"""
    logger.debug("data health_check: Received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
