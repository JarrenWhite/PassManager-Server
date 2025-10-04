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
        ephemeral_salt: str,
        ephemeral_b: str,
        expiry_time: datetime
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
                    ephemeral_salt=ephemeral_salt,
                    ephemeral_b=ephemeral_b,
                    expiry_time=expiry_time
                )
                session.add(auth_ephemeral)
                session.flush()

                return True, None, auth_ephemeral.public_id, user.srp_salt
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, "", ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, "", ""


    @staticmethod
    def session_get_ephemeral_details(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, str]:
        """
        Get the ephemeral details for the given ephemeral id
        return:     (str, str)      -> (ephemeral_salt, ephemeral_bytes)
        """
        try:
            with DatabaseUtils._get_db_session() as session:
                auth_ephemeral = session.query(AuthEphemeral).filter(AuthEphemeral.public_id == public_id).first()

                if auth_ephemeral is None:
                    return False, FailureReason.NOT_FOUND, "", ""
                if auth_ephemeral.expiry_time < datetime.now():
                    session.delete(auth_ephemeral)
                    return False, FailureReason.NOT_FOUND, "", ""

                return True, None, auth_ephemeral.ephemeral_salt, auth_ephemeral.ephemeral_b
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
                    last_used=datetime.now(),
                    maximum_requests=maximum_requests,
                    expiry_time=expiry_time
                )
                session.add(login_session)
                session.flush()

                session.delete(auth_ephemeral)

                return True, None, login_session.public_id
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def session_get_session_details(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, int]:
        """
        Get the session details for the given session id
        return:     (str, int)      -> (session_key, request_count)
        """
        try:
            with DatabaseUtils._get_db_session() as session:
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


    """
    TODO - Implement functions:
        User
    create
    change_username
    delete

        Auth
    start_auth
    get_ephemeral_details
    complete_auth
    start_auth_password
    complete_auth_password
    clean_ephemerals

        Session
    get_session_details
    increment_request_count
    delete_session
    clean_sessions
    clean_all_sessions

        Password
    complete_password_change
    abort_password_change
    add_password_change_encryption_entry

        Data
    create_entry
    edit_entry
    delete_entry
    get_entry
    get_list
    """
