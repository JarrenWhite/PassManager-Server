from datetime import datetime
from typing import Tuple, Optional
from contextlib import contextmanager

from database import DatabaseSetup, LoginSession
from .utils_enums import FailureReason


class DBUtilsSession():
    """Utility functions for managing session based database functions"""


    @staticmethod
    @contextmanager
    def _get_db_session():
        session = DatabaseSetup.get_session()()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


    @staticmethod
    def get_session_details(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, int]:
        """
        Get the session details for the given session id
        return:     (str, int)      -> (session_key, request_count)
        """
        try:
            with DBUtilsSession._get_db_session() as session:
                login_session = session.query(LoginSession).filter(LoginSession.public_id == public_id).first()

                if login_session is None:
                    return False, FailureReason.NOT_FOUND, "", 0
                if login_session.expiry_time and login_session.expiry_time < datetime.now():
                    session.delete(login_session)
                    return False, FailureReason.NOT_FOUND, "", 0
                if login_session.maximum_requests is not None and login_session.maximum_requests <= login_session.request_count:
                    session.delete(login_session)
                    return False, FailureReason.NOT_FOUND, "", 0

                return True, None, login_session.session_key, login_session.request_count
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", 0
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, "", 0
