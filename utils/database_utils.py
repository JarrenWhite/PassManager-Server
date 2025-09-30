from typing import Tuple, Optional
from contextlib import contextmanager

from database import DatabaseSetup, User

from .utils_enums import FailureReason


class DatabaseUtils:
    """Utility functions for interacting with the database layer."""


    @staticmethod
    def create_user(username_hash: str, srp_salt: str, srp_verifier: str, master_key_salt: str) -> Tuple[bool, Optional[FailureReason]]:
        """Create a new user and add them to the database"""
        session_maker = DatabaseSetup.get_session()
        session = session_maker()

        user = User(
            username_hash=username_hash,
            srp_salt=srp_salt,
            srp_verifier=srp_verifier,
            master_key_salt=master_key_salt,
        )
        session.add(user)
        session.commit()
        session.close()

        return True, None
