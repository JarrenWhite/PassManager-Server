from typing import Tuple, Optional
from contextlib import contextmanager

from database import DatabaseSetup, User
from .utils_enums import FailureReason


class DatabaseUtils:
    """Utility functions for interacting with the database layer."""

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
    def create_user(username_hash: str, srp_salt: str, srp_verifier: str, master_key_salt: str) -> Tuple[bool, Optional[FailureReason]]:
        """Create a new user and add them to the database"""
        user = User(
            username_hash=username_hash,
            srp_salt=srp_salt,
            srp_verifier=srp_verifier,
            master_key_salt=master_key_salt,
        )

        try:
            with DatabaseUtils._get_db_session() as session:
                session.add(user)
                return True, None
        except:
            return False, FailureReason.DUPLICATE
