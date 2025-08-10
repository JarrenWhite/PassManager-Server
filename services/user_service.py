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
    ok, failure_reason, public_id = Database.create_registration(hashed_secret_key, expiry_time)

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
    required_keys = {"registration_id", "secret_key_plain", "secret_key_enc", "username"}
    ok, error = Service.sanitise_inputs(data, required_keys, "complete_user_registration")
    if not ok:
        return error, 400

    registration_id = data["registration_id"]
    secret_key_plain = data["secret_key_plain"]
    secret_key_enc = data["secret_key_enc"]
    username = data["username"]

    # Fetch hashed secret key
    ok, failure_reason, secret_key_hash = Database.fetch_registration(registration_id)
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "complete_user_registration")
    assert secret_key_hash is not None

    # Check that received plain key links to stored hash
    if hashlib.sha256(secret_key_plain).hexdigest() != secret_key_hash:
        logger.warning("complete_user_registration: Rejected - Secret key hashes do not align.")
        return {"error": "The received key does not match the stored one for this ID"}, 400

    # Attempt data entry
    ok, failure_reason = Database.create_user(username, secret_key_hash, secret_key_enc)
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "complete_user_registration")

    # Delete registration entry
    ok, failure_reason = Database.delete_registration(registration_id)
    if not ok:
        logger.error(f"complete_user_registration: Failed to delete registration {registration_id} after user creation.")

    # User created
    return {}, 201


def get_user_key(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Return the encrypted secret key for a user - business logic"""
    # Sanitise inputs
    required_keys = {"username"}
    ok, error = Service.sanitise_inputs(data, required_keys, "get_user_key")
    if not ok:
        return error, 400

    # Attempt to get User data
    username = data["username"]
    ok, failure_reason, secret_key_enc = Database.get_user_secret_key_enc(username)
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "get_user_key")

    # Success
    return {"secret_key": secret_key_enc}, 200


def user_delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Delete a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "secret_key_plain"}
    ok, error = Service.sanitise_inputs(data, required_keys, "user_delete")
    if not ok:
        return error, 400

    secret_key_plain = data["secret_key_plain"]
    username = data["username"]

    # Authenticate user
    ok, failure_reason, secret_key_hash = Database.get_user_secret_key_hash(username)
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "user_delete (auth)")

    # Check that received plain key links to stored hash
    if hashlib.sha256(secret_key_plain).hexdigest() != secret_key_hash:
        logger.warning("complete_user_registration: Rejected - Secret key hashes do not align.")
        return {"error": "The received key does not match the stored one for this ID"}, 400

    # Delete user
    ok, failure_reason = Database.delete_user(username)
    if not ok:
        assert failure_reason is not None
        return Service.handle_failure(failure_reason, "user_delete (delete)")

    # Success
    logger.info(f"user_delete: User '{username}' deleted successfully")
    return {}, 200
