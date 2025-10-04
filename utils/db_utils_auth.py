from datetime import datetime
from typing import Tuple, Optional
from contextlib import contextmanager

from database import DatabaseSetup, User, AuthEphemeral, LoginSession
from .utils_enums import FailureReason


class DBUtilsAuth():
    """Utility functions for managing auth based database functions"""


    @staticmethod
    def start(
        username_hash: str,
        ephemeral_salt: str,
        ephemeral_b: str,
        expiry_time: datetime
    ) -> Tuple[bool, Optional[FailureReason], str, str]:
        """
        Begin auth ephemeral session for the user
        return:     (str, str)      -> (public_id, srp_salt)
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.username_hash == username_hash).first()
                if user is None:
                    return False, FailureReason.NOT_FOUND, "", ""

                auth_ephemeral = AuthEphemeral(
                    user=user,
                    ephemeral_salt=ephemeral_salt,
                    ephemeral_b=ephemeral_b,
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
        username_hash: str,
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, str]:
        """
        Get the ephemeral details for the given ephemeral id
        return:     (str, str)      -> (ephemeral_salt, ephemeral_bytes)
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    return False, FailureReason.NOT_FOUND, "", ""
                if auth_ephemeral.expiry_time < datetime.now():
                    session.delete(auth_ephemeral)
                    return False, FailureReason.NOT_FOUND, "", ""
                if auth_ephemeral.user.username_hash is not username_hash:
                    return False, FailureReason.NO_MATCH, "", ""

                return True, None, auth_ephemeral.ephemeral_salt, auth_ephemeral.ephemeral_b
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, "", ""


    @staticmethod
    def complete(
        public_id: str,
        session_key: str,
        maximum_requests: Optional[int],
        expiry_time: Optional[datetime]
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Complete login session creation
        return:     str             -> public_id
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    return False, FailureReason.NOT_FOUND, ""

                login_session = LoginSession(
                    user=auth_ephemeral.user,
                    session_key=session_key,
                    request_count=0,
                    last_used=datetime.now(),
                    maximum_requests=maximum_requests,
                    expiry_time=expiry_time,
                    password_change=False
                )
                session.add(login_session)
                session.flush()

                session.delete(auth_ephemeral)

                return True, None, login_session.public_id
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, ""
