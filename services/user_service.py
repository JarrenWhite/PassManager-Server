from typing import Dict, Any, Tuple
import logging
logger = logging.getLogger("services")

from utils import Sanitise, Database, FailureReason


def user_register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Register a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_register: Rejected - Incorrect keys.")
        return error, 400

    username = data["username"]
    ok, error = Sanitise.username(username)
    if not ok:
        logger.warning("user_register: Rejected - Username insanitary.")
        return error, 400

    password = data["password"]
    ok, error = Sanitise.password(password)
    if not ok:
        logger.warning("user_register: Rejected - Password insanitary.")
        return error, 400

    # Attempt data entry
    ok, failure_reason = Database.create_user(username, password)
    if ok:
        return {}, 201

    # Failure
    if failure_reason == FailureReason.ALREADY_EXISTS:
        logger.info("user_register: Rejected - Username exists")
        return {"error": "Username already exists"}, 409
    elif failure_reason == FailureReason.SERVER_EXCEPTION:
        logger.error("user_register: Rejected - server exception")
        return {"error": "Unknown error"}, 500
    logger.error("user_register: Rejected - unknown server issue")
    return {"error": "Unknown error"}, 500


def user_auth(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Authorize a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_auth: Rejected - Incorrect keys.")
        return error, 400

    username = data["username"]
    ok, error = Sanitise.username(username)
    if not ok:
        logger.warning("user_auth: Rejected - Username issue.")
        return error, 400

    password = data["password"]
    ok, error = Sanitise.password(password)
    if not ok:
        logger.warning("user_auth: Rejected - Password issue.")
        return error, 400

    # Attempt to get User data
    ok, failure_reason, stored_password_hash = Database.get_user_password_hash(username)
    if ok and stored_password_hash is not None:
        if password == stored_password_hash:
            return {}, 200
        else:
            return {"error": "Incorrect username or password"}, 401

    # Failure
    if failure_reason == FailureReason.NOT_FOUND:
        logger.info("user_auth: Rejected - Username not found")
        return {"error": "Incorrect username or password"}, 401
    elif failure_reason == FailureReason.SERVER_EXCEPTION:
        logger.error("user_auth: Rejected - server exception")
        return {"error": "Unknown error"}, 500
    logger.error("user_auth: Rejected - unknown server issue")
    return {"error": "Unknown error"}, 500


def user_delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Delete a user - business logic"""
    # Sanitise inputs
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_delete: Rejected - Incorrect keys.")
        return error, 400

    username = data["username"]
    ok, error = Sanitise.username(username)
    if not ok:
        logger.warning("user_delete: Rejected - Username issue.")
        return error, 400

    password = data["password"]
    ok, error = Sanitise.password(password)
    if not ok:
        logger.warning("user_delete: Rejected - Password issue.")
        return error, 400

    # Authenticate user
    ok, failure_reason, stored_password_hash = Database.get_user_password_hash(username)
    if not ok or stored_password_hash is None:
        if failure_reason == FailureReason.NOT_FOUND:
            logger.info("user_delete: Rejected - Username not found")
            return {"error": "Incorrect username or password"}, 401
        elif failure_reason == FailureReason.SERVER_EXCEPTION:
            logger.error("user_delete: Rejected - server exception during authentication")
            return {"error": "Unknown error"}, 500
        logger.error("user_delete: Rejected - unknown server issue during authentication")
        return {"error": "Unknown error"}, 500

    # Verify password
    if password != stored_password_hash:
        logger.info("user_delete: Rejected - Incorrect password")
        return {"error": "Incorrect username or password"}, 401

    # Delete User
    ok, failure_reason = Database.delete_user(username)
    if ok:
        logger.info(f"user_delete: User '{username}' deleted successfully")
        return {}, 200

    # Deletion Failure
    if failure_reason == FailureReason.NOT_FOUND:
        logger.error("user_delete: Rejected - Username not found during deletion")
        return {"error": "Unknown error"}, 500
    elif failure_reason == FailureReason.SERVER_EXCEPTION:
        logger.error("user_delete: Rejected - server exception during deletion")
        return {"error": "Unknown error"}, 500
    logger.error("user_delete: Rejected - unknown server issue during deletion")
    return {"error": "Unknown error"}, 500
