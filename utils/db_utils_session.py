from datetime import datetime
from typing import Tuple, Optional

from sqlalchemy.orm import Session

from database import DatabaseSetup, LoginSession, User
from .utils_enums import FailureReason
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
            if login_session.password_change:
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
    ) -> Tuple[bool, Optional[FailureReason], int, int, str, int, bool]:
        """
        Get the session details for the given session id

        Returns:
            (int)   user_id
            (int)   session_id
            (str)   session_key
            (int)   request_count
            (bool)  password_change
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.public_id == public_id).first()

                if login_session is None:
                    return False, FailureReason.NOT_FOUND, 0, 0, "", 0, False
                if DBUtilsSession._check_expiry(session, login_session):
                    return False, FailureReason.NOT_FOUND, 0, 0, "", 0, False

                return (
                    True, None,
                    login_session.user.id,
                    login_session.id,
                    login_session.session_key,
                    login_session.request_count,
                    login_session.password_change
                )
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, 0, 0, "", 0, False
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, 0, 0, "", 0, False


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
                    return False, FailureReason.NOT_FOUND, ""
                if DBUtilsSession._check_expiry(session, login_session):
                    return False, FailureReason.NOT_FOUND, ""

                login_session.request_count += 1
                return True, None, login_session.session_key
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def delete(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Delete given login session"""
        try:
            with DatabaseSetup.get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.public_id == public_id).first()

                if not login_session:
                    return False, FailureReason.NOT_FOUND
                if DBUtilsSession._check_expiry(session, login_session):
                    return False, FailureReason.NOT_FOUND
                if login_session.password_change:
                    return False, FailureReason.PASSWORD_CHANGE

                session.delete(login_session)
                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
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
                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
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

                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return False, FailureReason.UNKNOWN_EXCEPTION
