from typing import Tuple, Optional

from logging import getLogger
logger = getLogger("database")

from sqlalchemy.exc import IntegrityError

from enums import FailureReason
from database import DatabaseSetup, User


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
            logger.info(f"Username Hash {username_hash[-4:]} already exists.")
            return False, FailureReason.DUPLICATE
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def change_username(
        user_id: int,
        new_username_hash: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Change username for an existing user"""
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.debug(f"User id: {user_id} not found.")
                    return False, FailureReason.NOT_FOUND
                if user.password_change:
                    logger.debug(f"User: {user.username_hash[-4:]} undergoing password change.")
                    return False, FailureReason.PASSWORD_CHANGE

                user.username_hash = new_username_hash

                return True, None
        except IntegrityError:
            return False, FailureReason.DUPLICATE
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            logger.exception("Unknown database session exception.")
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
                    logger.debug(f"User id: {user_id} not found.")
                    return False, FailureReason.NOT_FOUND
                if user.password_change:
                    logger.debug(f"User: {user.username_hash[-4:]} undergoing password change.")
                    return False, FailureReason.PASSWORD_CHANGE

                session.delete(user)

                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION
