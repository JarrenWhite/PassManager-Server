from typing import Tuple, Optional

from sqlalchemy.exc import IntegrityError

from database import DatabaseSetup, User
from .utils_enums import FailureReason


class DBUtilsUser():
    """Utility functions for managing user based database functions"""


    @staticmethod
    def create(
        username_hash: str,
        srp_salt: str,
        srp_verifier: str,
        master_key_salt: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Create a new user and add them to the database"""
        user = User(
            username_hash=username_hash,
            srp_salt=srp_salt,
            srp_verifier=srp_verifier,
            master_key_salt=master_key_salt,
            password_change=False
        )

        try:
            with DatabaseSetup.get_db_session() as session:
                session.add(user)
                return True, None
        except IntegrityError:
            return False, FailureReason.DUPLICATE
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def change_username(
        username_id: int,
        new_username_hash: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Change username for an existing user"""
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == username_id).first()
                if not user:
                    return False, FailureReason.NOT_FOUND
                if user.password_change:
                    return False, FailureReason.PASSWORD_CHANGE
                user.username_hash = new_username_hash
                return True, None
        except IntegrityError:
            return False, FailureReason.DUPLICATE
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def delete(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Delete given user"""
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False, FailureReason.NOT_FOUND
                if user.password_change:
                    return False, FailureReason.PASSWORD_CHANGE
                session.delete(user)
                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return False, FailureReason.UNKNOWN_EXCEPTION
