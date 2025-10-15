from datetime import datetime
from typing import Tuple, Optional

from sqlalchemy.orm import Session

from database import DatabaseSetup, User, AuthEphemeral, LoginSession
from .utils_enums import FailureReason
from .db_utils_password import DBUtilsPassword


class DBUtilsAuth():
    """Utility functions for managing auth based database functions"""

    @staticmethod
    def _check_expiry(
        db_session: Session,
        auth_ephemeral: AuthEphemeral
    ) -> bool:
        """
        Checks if an auth ephemeral is expired, and cleans up appropriately

        Returns:
            (bool)  True if expired & being deleted, false otherwise
        """
        is_expired = False

        if (
            auth_ephemeral.expiry_time and
            auth_ephemeral.expiry_time < datetime.now()
        ):
            is_expired = True

        if is_expired:
            if auth_ephemeral.password_change:
                DBUtilsPassword.clean_password_change(
                    db_session=db_session,
                    user=auth_ephemeral.user
                )
            else:
                db_session.delete(auth_ephemeral)

        return is_expired


    @staticmethod
    def start(
        username_hash: str,
        eph_private_b: str,
        eph_public_b: str,
        expiry_time: datetime
    ) -> Tuple[bool, Optional[FailureReason], str, str]:
        """
        Begin auth ephemeral session for the user

        Returns:
            (str)   public_id
            (str)   srp_salt
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.username_hash == username_hash).first()
                if user is None:
                    return False, FailureReason.NOT_FOUND, "", ""

                auth_ephemeral = AuthEphemeral(
                    user=user,
                    eph_private_b=eph_private_b,
                    eph_public_b=eph_public_b,
                    expiry_time=expiry_time,
                    password_change=False
                )
                session.add(auth_ephemeral)
                session.flush()

                return True, None, auth_ephemeral.public_id, user.srp_salt
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, "", ""


    @staticmethod
    def get_details(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, int, str, str]:
        """
        Get the ephemeral details for the given ephemeral id

        Returns:
            (str)   username_hash
            (int)   user_id
            (str)   eph_private_b
            (str)   eph_public_b
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    return False, FailureReason.NOT_FOUND, "", 0, "", ""
                if DBUtilsAuth._check_expiry(session, auth_ephemeral):
                    return False, FailureReason.NOT_FOUND, "", 0, "", ""

                return (True, None,
                    auth_ephemeral.user.username_hash,
                    auth_ephemeral.user.id,
                    auth_ephemeral.eph_private_b,
                    auth_ephemeral.eph_public_b
                )
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", 0, "", ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, "", 0, "", ""


    @staticmethod
    def complete(
        public_id: str,
        session_key: str,
        maximum_requests: Optional[int],
        expiry_time: Optional[datetime]
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Complete login session creation

        Returns:
            (str)   public_id
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    return False, FailureReason.NOT_FOUND, ""
                if DBUtilsAuth._check_expiry(session, auth_ephemeral):
                    return False, FailureReason.NOT_FOUND, ""

                login_session = LoginSession(
                    user=auth_ephemeral.user,
                    session_key=session_key,
                    request_count=0,
                    last_used=datetime.now(),
                    maximum_requests=maximum_requests,
                    expiry_time=expiry_time,
                    password_change=auth_ephemeral.password_change
                )
                session.add(login_session)
                session.flush()

                session.delete(auth_ephemeral)

                return True, None, login_session.public_id
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def clean_all(
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Remove all expired Auth Ephemerals from the database"""
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemerals = session.query(AuthEphemeral)
                for auth_ephemeral in auth_ephemerals:
                    _ = DBUtilsAuth._check_expiry(session, auth_ephemeral)

                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return False, FailureReason.UNKNOWN_EXCEPTION
