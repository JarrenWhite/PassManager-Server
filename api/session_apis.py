from flask import Blueprint, jsonify, request
from services.session_service import session_create, session_auth, session_delete, session_delete_all

session_bp = Blueprint('session', __name__, url_prefix='/api/session')

@session_bp.route('/create', methods=['POST'])
def session_create_endpoint():
    """Create a session for a user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = session_create(data)
    return jsonify(result), status_code

@session_bp.route('/auth', methods=['POST'])
def session_auth_endpoint():
    """Get a user from a session"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = session_auth(data)
    return jsonify(result), status_code

@session_bp.route('/delete', methods=['POST'])
def session_delete_endpoint():
    """Delete a given session"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = session_delete(data)
    return jsonify(result), status_code

@session_bp.route('/clean', methods=['POST'])
def session_delete_all_endpoint():
    """Delete all sessions for a given user"""
    if request.is_json:
        data = request.get_json() or {}
    else:
        data = dict(request.form) or {}

    result, status_code = session_delete_all(data)
    return jsonify(result), status_code

@session_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the session API"""
    return jsonify({
        'status': 'healthy',
        'service': 'session-api'
    }), 201
