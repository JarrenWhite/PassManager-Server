from datetime import datetime
from typing import Tuple, Optional

from logging import getLogger
logger = getLogger("database")

from sqlalchemy.orm import Session

from enums import FailureReason
from database import DatabaseSetup, LoginSession, User
from .db_utils_password import DBUtilsPassword


class DBUtilsSession():
    """Utility functions for managing session based database functions"""

    @staticmethod
    def _check_expiry(
        db_session: Session,
        login_session: LoginSession
    ) -> bool:
        """
        Checks if a login session is expired, and cleans up appropriately

        Returns:
            (bool)  True if expired & being deleted, false otherwise
        """
        is_expired = False

        if (
            login_session.expiry_time and
            login_session.expiry_time < datetime.now()
        ):
            is_expired = True

        if (
            login_session.maximum_requests is not None and
            login_session.maximum_requests <= login_session.request_count
        ):
            is_expired = True

        if is_expired:
            logger.debug(f"Login Session: {login_session.public_id[-4:]} has expired.")
            if login_session.password_change:
                logger.debug("Password Login Session being passed for cleaning.")
                DBUtilsPassword.clean_password_change(
                    db_session=db_session,
                    user=login_session.user
                )
            else:
                db_session.delete(login_session)

        return is_expired


    @staticmethod
    def get_details(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], int, str, int, str, int, bool]:
        """
        Get the session details for the given session id

        Returns:
            (int)   user_id
            (str)   username_hash
            (int)   session_id
            (str)   session_key
            (int)   request_count
            (bool)  password_change
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.public_id == public_id).first()

                if login_session is None:
                    logger.debug(f"Login Session: {public_id[-4:]} not found.")
                    return False, FailureReason.NOT_FOUND, 0, "", 0, "", 0, False
                if DBUtilsSession._check_expiry(session, login_session):
                    logger.debug(f"Login Session: {public_id[-4:]} expired.")
                    return False, FailureReason.NOT_FOUND, 0, "", 0, "", 0, False

                logger.debug(f"Login Session: {public_id[-4:]} requested.")
                return (
                    True, None,
                    login_session.user.id,
                    login_session.user.username_hash,
                    login_session.id,
                    login_session.session_key,
                    login_session.request_count,
                    login_session.password_change
                )
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, 0, "", 0, "", 0, False
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, 0,"", 0, "", 0, False


    @staticmethod
    def log_use(
        session_id: int
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Log the use of a login session

        Returns:
            (str)   session_key
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.id == session_id).first()

                if login_session is None:
                    logger.debug(f"Login Session id: {session_id} not found.")
                    return False, FailureReason.NOT_FOUND, ""
                if DBUtilsSession._check_expiry(session, login_session):
                    logger.debug(f"Login Session: {login_session.public_id[-4:]} expired.")
                    return False, FailureReason.NOT_FOUND, ""

                login_session.request_count += 1

                logger.debug(f"Login Session: {login_session.public_id[-4:]} request count incremented.")
                return True, None, login_session.session_key
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def delete(
        user_id: int,
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Delete given login session"""
        try:
            with DatabaseSetup.get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.public_id == public_id).first()

                if not login_session:
                    logger.debug(f"Login Session: {public_id[-4:]} not found.")
                    return False, FailureReason.NOT_FOUND
                if DBUtilsSession._check_expiry(session, login_session):
                    logger.debug(f"Login Session: {public_id[-4:]} expired.")
                    return False, FailureReason.NOT_FOUND
                if login_session.user.id != user_id:
                    logger.debug(f"Login Session: {public_id[-4:]} does not belong to user.")
                    return False, FailureReason.NOT_FOUND
                if login_session.password_change:
                    logger.debug(f"Login Session: {public_id[-4:]} is password change type.")
                    return False, FailureReason.PASSWORD_CHANGE

                session.delete(login_session)

                logger.debug(f"Login Session: {public_id[-4:]} deleted.")
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def clean_user(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Remove all Login Sessions for the user"""
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    return False, FailureReason.NOT_FOUND

                for auth_ephemeral in user.auth_ephemerals:
                    if auth_ephemeral.password_change:
                        DBUtilsPassword.clean_password_change(session, auth_ephemeral.user)
                    else:
                        session.delete(auth_ephemeral)
                for login_session in user.login_sessions:
                    if login_session.password_change:
                        DBUtilsPassword.clean_password_change(session, login_session.user)
                    else:
                        session.delete(login_session)

                logger.debug(f"Login Sessions cleaned for User: {user.username_hash[-4:]}.")
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def clean_all(
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Remove all expired Login Sessions from the database"""
        try:
            with DatabaseSetup.get_db_session() as session:
                login_sessions = session.query(LoginSession)
                for login_session in login_sessions:
                    _ = DBUtilsSession._check_expiry(session, login_session)

                logger.debug("Login Sessions cleaned.")
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION
