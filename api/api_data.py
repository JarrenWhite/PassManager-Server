from flask import Blueprint, jsonify, request

import logging
logger = logging.getLogger("api")

from services import ServiceData


data_bp = Blueprint('data', __name__, url_prefix='/api/data')


@data_bp.route('/create', methods=['POST'])
def create():
    """Create a secure data entry"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Create: Called")
    result, status_code = ServiceData.create(data)
    logger.info(f"Create complete: {status_code}")
    return jsonify(result), status_code


@data_bp.route('/edit', methods=['POST'])
def edit():
    """Edit a secure data entry"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Edit: Called")
    result, status_code = ServiceData.edit(data)
    logger.info(f"Edit complete: {status_code}")
    return jsonify(result), status_code


@data_bp.route('/delete', methods=['POST'])
def delete():
    """Delete a secure data entry"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Delete: Called")
    result, status_code = ServiceData.delete(data)
    logger.info(f"Delete complete: {status_code}")
    return jsonify(result), status_code


@data_bp.route('/get', methods=['POST'])
def get():
    """Get the contents of a secure data entry"""

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    logger.debug("Get: Called")
    result, status_code = ServiceData.get(data)
    logger.info(f"Get complete: {status_code}")
    return jsonify(result), status_code


@data_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the data API"""
    logger.debug("Data health check received")
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 200
