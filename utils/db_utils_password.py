from datetime import datetime
from typing import Tuple, Optional

from sqlalchemy.orm import Session

from database import User
from .utils_enums import FailureReason


class DBUtilsPassword():
    """Utility functions for managing password change based database functions"""

    @staticmethod
    def clean_password_change(
        db_session: Session,
        user: User
    ):
        """Remove all partial password change entries, ephemerals and login sessions"""
        pass

    @staticmethod
    def start(
        username_hash: str,
        eph_private_b: str,
        eph_public_b: str,
        expiry_time: datetime,
        srp_salt: str,
        srp_verifier: str,
        master_key_salt: str
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Begin password auth ephemeral session for the user

        Returns:
            (str)   public_id
        """
        return False, None, ""
