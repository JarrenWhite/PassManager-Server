from flask import Blueprint, jsonify, request
from services.data_service import data_create, data_edit, data_delete, data_get, data_get_all

data_bp = Blueprint('data', __name__, url_prefix='/api/data')

@data_bp.route('/create', methods=['POST'])
def data_create_endpoint():
    """Create data entry for given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = data_create(data)
    return jsonify(result), status_code

@data_bp.route('/edit', methods=['POST'])
def data_edit_endpoint():
    """Edit given data entry for given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = data_edit(data)
    return jsonify(result), status_code

@data_bp.route('/delete', methods=['POST'])
def data_delete_endpoint():
    """Delete given data entry for given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = data_delete(data)
    return jsonify(result), status_code

@data_bp.route('/entry', methods=['POST'])
def data_get_endpoint():
    """Get given data entry for given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = data_get(data)
    return jsonify(result), status_code

@data_bp.route('/list', methods=['POST'])
def data_get_all_endpoint():
    """Get list of data entries for given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = data_get_all(data)
    return jsonify(result), status_code

@data_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    return jsonify({
        'status': 'healthy',
        'service': 'data-api'
    }), 201
