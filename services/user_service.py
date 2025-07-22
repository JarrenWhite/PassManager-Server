from typing import Dict, Any, Tuple
import logging
logger = logging.getLogger("services")

from utils import Sanitise


def user_register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Register a user - business logic"""
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_register: Rejected - Incorrect keys.")
        return error, 400

    ok, error = Sanitise.username(data["username"])
    if not ok:
        logger.warning("user_register: Rejected - Username issue.")
        return error, 400

    ok, error = Sanitise.password(data["password"])
    if not ok:
        logger.warning("user_register: Rejected - Password issue.")
        return error, 400

    return {}, 201

def user_auth(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Authorize a user - business logic"""
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_auth: Rejected - Incorrect keys.")
        return error, 400

    ok, error = Sanitise.username(data["username"])
    if not ok:
        logger.warning("user_auth: Rejected - Username issue.")
        return error, 400

    ok, error = Sanitise.password(data["password"])
    if not ok:
        logger.warning("user_auth: Rejected - Password issue.")
        return error, 400

    return {}, 201

def user_delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Delete a user - business logic"""
    required_keys = {"username", "password"}
    ok, error = Sanitise.keys(data, required_keys)
    if not ok:
        logger.warning("user_delete: Rejected - Incorrect keys.")
        return error, 400

    ok, error = Sanitise.username(data["username"])
    if not ok:
        logger.warning("user_delete: Rejected - Username issue.")
        return error, 400

    ok, error = Sanitise.password(data["password"])
    if not ok:
        logger.warning("user_delete: Rejected - Password issue.")
        return error, 400

    return {}, 201
