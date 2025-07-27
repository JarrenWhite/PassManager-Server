from typing import Dict, Any, Tuple
import secrets
import hashlib
from datetime import timedelta
import logging
logger = logging.getLogger("services")

from utils import Service, Database


def begin_user_registration() -> Tuple[Dict[str, Any], int]:
    """Get secret key to create user - business logic"""
    # Create secret key
    secret_key = secrets.token_bytes(32)
    hashed_secret_key = hashlib.sha256(secret_key).hexdigest()
    expiry_time = timedelta(minutes=5)
    ok, failure_reason, public_id = Database.create_registeration(hashed_secret_key, expiry_time)

    # Failure
    if not ok:
        assert failure_reason
        return Service.handle_failure(failure_reason, "begin_user_registration")

    # Secret key prepared
    assert public_id is not None
    return {"registration_id": public_id, "secret_key": secret_key}, 201

def complete_user_registration(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Register a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "password"}
    ok, error = Service.sanitise_inputs(data, required_keys, "complete_user_registration")
    if not ok:
        return error, 400

    # Attempt data entry
    username = data["username"]
    password = data["password"]
    ok, failure_reason = Database.create_user(username, password)

    # Failure
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "complete_user_registration")

    # User created
    return {}, 201


def user_auth(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Authorize a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "password"}
    ok, error = Service.sanitise_inputs(data, required_keys, "user_auth")
    if not ok:
        return error, 400

    # Attempt to get User data
    username = data["username"]
    password = data["password"]
    ok, failure_reason, stored_password_hash = Database.get_user_password_hash(username)

    # Failure
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "user_auth")

    # Success
    if password == stored_password_hash:
        return {}, 200
    else:
        return {"error": "Incorrect username or password"}, 401


def user_delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Delete a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "password"}
    ok, error = Service.sanitise_inputs(data, required_keys, "user_delete")
    if not ok:
        return error, 400

    # Authenticate user
    username = data["username"]
    password = data["password"]
    ok, failure_reason, stored_password_hash = Database.get_user_password_hash(username)

    # Failure on Auth
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "user_delete (auth)")

    # Verify password
    if password != stored_password_hash:
        logger.info("user_delete: Rejected - Incorrect password")
        return {"error": "Incorrect username or password"}, 401

    # Delete User
    ok, failure_reason = Database.delete_user(username)

    # Failure on delete
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "user_delete (deletion)")

    # Success
    logger.info(f"user_delete: User '{username}' deleted successfully")
    return {}, 200
