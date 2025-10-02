from typing import Tuple, Optional
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError

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
        except IntegrityError:
            return False, FailureReason.DUPLICATE
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION

    @staticmethod
    def change_username(username_hash: str, new_username_hash: str) -> Tuple[bool, Optional[FailureReason]]:

        try:
            with DatabaseUtils._get_db_session() as session:
                user = session.query(User).filter(User.username_hash == username_hash).first()
                if not user:
                    return True, None
                user.username_hash = new_username_hash
                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return True, None

    """
    TODO - Implement functions:
    delete_user

    start_password_change
    continue_password_change
    complete_password_change
    abort_password_change
    add_password_change_encryption_entry

    start_auth
    complete_auth
    delete_session
    clean_sessions

    create_entry
    edit_entry
    delete_entry
    get_entry
    get_list

    initialise_database
    clean_ephemerals
    clean_sessions
    """
