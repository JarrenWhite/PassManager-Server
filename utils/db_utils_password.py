from sqlalchemy.orm import Session
from database import User

class DBUtilsPassword():
    """Utility functions for managing password change based database functions"""

    @staticmethod
    def clean_password_change(
        db_session: Session,
        user: User
    ):
        """Remove all partial password change entries, ephemerals and login sessions"""
        pass
