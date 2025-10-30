from datetime import datetime
from typing import Tuple, Optional, List

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
        user.password_change = False

        for ephemeral in user.auth_ephemerals:
            if ephemeral.password_change:
                db_session.delete(ephemeral)
        
        for login_session in user.login_sessions:
            db_session.delete(login_session)


    @staticmethod
    def start(
        user_id: int,
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


    @staticmethod
    def complete(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason], Optional[List[str]]]:
        """
        Complete password change process

        Returns:
            ([str]) [public_id]
        """
        return False, None, None


    @staticmethod
    def abort(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Abort the password change for a user"""
        return False, None


    @staticmethod
    def update(
        public_id: str,
        entry_name: str,
        entry_data: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Add new encrypted entries for """
