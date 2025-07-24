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

    # Data entry failure
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
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_auth: Rejected - Incorrect keys.")
        return error, 400

    username = data["username"]
    ok, error = Sanitise.username(username)
    if not ok:
        logger.warning("user_register: Rejected - Username issue.")
        return error, 400

    password = data["password"]
    ok, error = Sanitise.password(password)
    if not ok:
        logger.warning("user_register: Rejected - Password issue.")
        return error, 400

    return {}, 201


def user_delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Delete a user - business logic"""
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_delete: Rejected - Incorrect keys.")
        return error, 400

    username = data["username"]
    ok, error = Sanitise.username(username)
    if not ok:
        logger.warning("user_register: Rejected - Username issue.")
        return error, 400

    password = data["password"]
    ok, error = Sanitise.password(password)
    if not ok:
        logger.warning("user_register: Rejected - Password issue.")
        return error, 400

    return {}, 201
