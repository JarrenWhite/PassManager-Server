from datetime import datetime
from typing import Tuple, Optional
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError

from database import DatabaseSetup, User, AuthEphemeral, LoginSession
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
    def user_create(
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
    def user_change_username(
        username_hash: str,
        new_username_hash: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Change username for an existing user"""
        try:
            with DatabaseUtils._get_db_session() as session:
                user = session.query(User).filter(User.username_hash == username_hash).first()
                if not user:
                    return False, FailureReason.NOT_FOUND
                user.username_hash = new_username_hash
                return True, None
        except IntegrityError:
            return False, FailureReason.DUPLICATE
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def user_delete(
        username_hash: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Delete given user"""
        try:
            with DatabaseUtils._get_db_session() as session:
                user = session.query(User).filter(User.username_hash == username_hash).first()
                if not user:
                    return False, FailureReason.NOT_FOUND
                session.delete(user)
                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except Exception:
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def session_start_auth(
        username_hash: str,
        ephemeral_b: str,
        expires_at: datetime
    ) -> Tuple[bool, Optional[FailureReason], str, str]:
        """
        Begin auth ephemeral session for the user
        return:     (str, str)      -> (public_id, srp_salt)
        """
        try:
            with DatabaseUtils._get_db_session() as session:
                user = session.query(User).filter(User.username_hash == username_hash).first()
                if user is None:
                    return False, FailureReason.NOT_FOUND, "", ""

                auth_ephemeral = AuthEphemeral(
                    user=user,
                    ephemeral_b=ephemeral_b,
                    expires_at=expires_at
                )
                session.add(auth_ephemeral)
                session.flush()

                return True, None, auth_ephemeral.public_id, user.srp_salt
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, "", ""


    @staticmethod
    def session_complete_auth(
        public_id: str,
        session_key: str,
        maximum_requests: Optional[int],
        expiry_time: Optional[datetime]
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Complete login session creation
        return:     str             -> public_id
        """
        try:
            with DatabaseUtils._get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    return False, FailureReason.NOT_FOUND, ""

                login_session = LoginSession(
                    user=auth_ephemeral.user,
                    session_key=session_key,
                    request_count=0,
                    last_used=datetime.now()
                )
                session.add(login_session)
                session.flush()

                session.delete(auth_ephemeral)

                return True, None, login_session.public_id
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    """
    TODO - Implement functions:
    start_password_change
    continue_password_change
    complete_password_change
    abort_password_change
    add_password_change_encryption_entry

    get_ephemeral_details
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
