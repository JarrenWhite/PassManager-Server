from typing import Tuple, Dict, Any

from logging import getLogger
logger = getLogger("service")

from utils import DBUtilsSession, DBUtilsUser, FailureReason


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Delete a user account.

        Security Requirements:
        - Must use a fresh session (request_count == 0)
        - Must use a password-change session (password_change == True)
        """
        # Extract session_id from request
        session_id = data.get('session_id')
        if not session_id:
            logger.warning("Delete User: Missing session_id")
            return {
                "success": False,
                "errors": [{
                    "field": "session_id",
                    "error_code": "gnr00",
                    "error": "session_id invalid"
                }]
            }, 400

        # Get session details
        (
            success, failure_reason,
            user_id, username_hash,
            db_session_id, session_key,
            request_count, password_change
        ) = DBUtilsSession.get_details(session_id)

        if not success:
            logger.warning(f"Delete User: Session not found or invalid: {failure_reason}")
            return {
                "success": False,
                "errors": [{
                    "field": "session_id",
                    "error_code": "gnr01",
                    "error": "session_id not found"
                }]
            }, 404

        # Check that request_count is 0 (fresh session)
        if request_count != 0:
            logger.warning(f"Delete User: Session not fresh (request_count={request_count})")
            return {
                "success": False,
                "errors": [{
                    "field": "request_number",
                    "error_code": "ltd01",
                    "error": "Request number must be 0 for this request type"
                }]
            }, 400

        # Check that this is a password-change session
        if not password_change:
            logger.warning("Delete User: Session is not a password-change session")
            return {
                "success": False,
                "errors": [{
                    "field": "session_id",
                    "error_code": "ltd03",
                    "error": "Account deletion requires a password-change session"
                }]
            }, 412

        # Proceed with user deletion
        success, failure_reason = DBUtilsUser.delete(user_id)

        if not success:
            logger.error(f"Delete User: Failed to delete user: {failure_reason}")
            if failure_reason == FailureReason.NOT_FOUND:
                return {
                    "success": False,
                    "errors": [{
                        "field": "username",
                        "error_code": "gnr01",
                        "error": "username not found"
                    }]
                }, 404
            elif failure_reason == FailureReason.PASSWORD_CHANGE:
                return {
                    "success": False,
                    "errors": [{
                        "field": "request",
                        "error_code": "rqs02",
                        "error": "Password change in progress"
                    }]
                }, 403
            else:
                return {
                    "success": False,
                    "errors": [{
                        "field": "server",
                        "error_code": "svr00",
                        "error": "Server encountered an unexpected error"
                    }]
                }, 500

        logger.info(f"Delete User: Successfully deleted user {username_hash[-4:]}")
        return {
            "success": True
        }, 200
