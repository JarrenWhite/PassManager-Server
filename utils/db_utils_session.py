from datetime import datetime
from typing import Tuple, Optional

from database import DatabaseSetup, LoginSession
from .utils_enums import FailureReason


class DBUtilsSession():
    """Utility functions for managing session based database functions"""


    @staticmethod
    def get_details(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, str, int]:
        """
        Get the session details for the given session id
        return:     (str, str, int) -> (username_hash, session_key, request_count)
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.public_id == public_id).first()

                if login_session is None:
                    return False, FailureReason.NOT_FOUND, "", "", 0
                if login_session.expiry_time and login_session.expiry_time < datetime.now():
                    session.delete(login_session)
                    return False, FailureReason.NOT_FOUND, "", "", 0
                if login_session.maximum_requests is not None and login_session.maximum_requests <= login_session.request_count:
                    session.delete(login_session)
                    return False, FailureReason.NOT_FOUND, "", "", 0

                return (
                    True, None,
                    login_session.user.username_hash,
                    login_session.session_key,
                    login_session.request_count
                )
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", "", 0
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION,"", "", 0
