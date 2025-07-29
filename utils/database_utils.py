from datetime import timedelta, datetime
from typing import Optional, List, Tuple, Dict
from contextlib import contextmanager
import logging
logger = logging.getLogger("database")

from database import init_db, get_session_local, User, LoginSession, SecureData, Registration
from sqlalchemy import select

from .utils_enums import FailureReason


class Database:
    _database_initialised = False

    @staticmethod
    @contextmanager
    def _get_db_session():
        """Context manager for database sessions to ensure proper cleanup"""
        session = get_session_local()()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def init_database() -> bool:
        if not Database._database_initialised:
            init_db()
            Database._database_initialised = True
            return True
        else:
            return False

    @staticmethod
    def create_user(username: str, secret_key_hash: str, secret_key_enc: str) -> Tuple[bool, Optional[FailureReason]]:
        """Create a new user with the given username and secret key hash"""
        try:
            with Database._get_db_session() as session:
                # Check if user already exists
                existing_user = session.scalar(select(User).where(User.username == username))
                if existing_user:
                    logger.debug(f"create_user: User '{username}' already exists.")
                    return False, FailureReason.ALREADY_EXISTS

                # Create new user
                new_user = User(username=username, secret_key_hash=secret_key_hash, secret_key_enc=secret_key_enc)
                session.add(new_user)

                logger.info(f"create_user: User '{username}' created successfully.")
                return True, None

        except Exception as e:
            logger.error(f"create_user: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def get_user_secret_key_enc(username: str) -> Tuple[bool, Optional[FailureReason], Optional[str]]:
        """Find and return the user's secret key enc"""
        try:
            with Database._get_db_session() as session:
                user = session.scalar(select(User).where(User.username == username))
                if user:
                    return True, None, user.secret_key_enc
                else:
                    return False, FailureReason.USERNAME_NOT_FOUND, None

        except Exception as e:
            logger.error(f"get_user_secret_key_enc: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def get_user_secret_key_hash(username: str) -> Tuple[bool, Optional[FailureReason], Optional[str]]:
        """Find and return the user's secret key hash"""
        try:
            with Database._get_db_session() as session:
                user = session.scalar(select(User).where(User.username == username))
                if user:
                    return True, None, user.secret_key_hash
                else:
                    return False, FailureReason.USERNAME_NOT_FOUND, None

        except Exception as e:
            logger.error(f"get_user_secret_key_hash: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def delete_user(username: str) -> Tuple[bool, Optional[FailureReason]]:
        """Delete the requested user"""
        try:
            with Database._get_db_session() as session:
                # Find user in question
                user = session.scalar(select(User).where(User.username == username))
                if not user:
                    logger.warning(f"delete_user: User '{username}' could not be found.")
                    return False, FailureReason.USERNAME_NOT_FOUND
                session.delete(user)

                logger.info(f"delete_user: User '{username}' deleted successfully.")
                return True, None

        except Exception as e:
            logger.error(f"delete_user: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def create_session(username: str, token: str, duration_till_expiry: timedelta) -> Tuple[bool, Optional[FailureReason]]:
        """Create a session for the given user"""
        try:
            with Database._get_db_session() as session:
                # Find user in question
                user = session.scalar(select(User).where(User.username == username))
                if not user:
                    logger.warning(f"create_session: User '{username}' could not be found.")
                    return False, FailureReason.USERNAME_NOT_FOUND

                # Create login session
                expiry = datetime.now() + duration_till_expiry
                new_login_session = LoginSession(user=user, token=token, expiry=expiry)

                session.add(new_login_session)
                logger.info(f"create_session: User '{username}' login session created.")
                return True, None

        except Exception as e:
            logger.error(f"create_session: Error '{username}': {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def check_session_token(token: str) -> Tuple[bool, Optional[FailureReason], Optional[str]]:
        """Check if a session token is valid, and if so returning the Username."""
        try:
            with Database._get_db_session() as session:
                # Find token in question
                login_session = session.scalar(select(LoginSession).where(LoginSession.token == token))
                if not login_session:
                    logger.warning(f"check_session_token: Token '{token[:-4]}' could not be found.")
                    return False, FailureReason.SESSION_NOT_FOUND, None

                if login_session.expiry < datetime.now():
                    logger.warning(f"check_session_token: Token '{token[:-4]}' has expired.")
                    session.delete(login_session)
                    return False, FailureReason.SESSION_NOT_FOUND, None

                user = login_session.user
                if user:
                    return True, None, user.username
                else:
                    logger.error(f"check_session_token: Token '{token[:-4]}' does not have user relationship.")
                    return False, FailureReason.SERVER_EXCEPTION, None

        except Exception as e:
            logger.error(f"check_session_token: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def delete_session(token: str) -> Tuple[bool, Optional[FailureReason]]:
        """Delete the given session"""
        try:
            with Database._get_db_session() as session:
                # Find token in question
                login_session = session.scalar(select(LoginSession).where(LoginSession.token == token))
                if not login_session:
                    logger.warning(f"delete_session: Token '{token[:-4]}' could not be found.")
                    return False, FailureReason.SESSION_NOT_FOUND

                session.delete(login_session)
                logger.info(f"delete_session: Token '{token[:-4]}' deleted successfully.")
                return True, None

        except Exception as e:
            logger.error(f"delete_session: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def delete_all_sessions(username: str) -> Tuple[bool, Optional[FailureReason]]:
        """Delete all sessions for the given user"""
        try:
            with Database._get_db_session() as session:
                # Find user in question
                user = session.scalar(select(User).where(User.username == username))
                if not user:
                    logger.warning(f"delete_all_sessions: User '{username}' could not be found.")
                    return False, FailureReason.USERNAME_NOT_FOUND

                all_login_sessions = user.login_sessions
                for login_session in all_login_sessions:
                    session.delete(login_session)
                logger.info(f"delete_all_sessions: All login sessions for '{username}' deleted.")
                return True, None

        except Exception as e:
            logger.error(f"delete_all_sessions: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def clean_sessions() -> Tuple[bool, Optional[FailureReason]]:
        """Remove all sessions with past expiry dates"""
        try:
            with Database._get_db_session() as session:
                current_time = datetime.now()
                expired_sessions = session.scalars(
                    select(LoginSession).where(LoginSession.expiry < current_time)
                ).all()

                for session_obj in expired_sessions:
                    session.delete(session_obj)

                logger.info(f"clean_sessions: Deleted {len(expired_sessions)} sessions.")
                return True, None

        except Exception as e:
            logger.error(f"clean_sessions: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def create_secure_data(username: str,
                           entry_name: str,
                           website_enc: str,
                           username_enc: str,
                           password_enc: str,
                           notes_enc: str) -> Tuple[bool, Optional[FailureReason]]:
        """Create an instance of secure data"""
        try:
            with Database._get_db_session() as session:
                # Find user in question
                user = session.scalar(select(User).where(User.username == username))
                if not user:
                    logger.warning(f"create_secure_data: User '{username}' could not be found.")
                    return False, FailureReason.USERNAME_NOT_FOUND

                # Create secure data
                new_secure_data = SecureData(user=user,
                                             entry_name=entry_name,
                                             website=website_enc,
                                             username=username_enc,
                                             password=password_enc,
                                             notes=notes_enc)

                session.add(new_secure_data)
                logger.info(f"create_secure_data: Secure data '{new_secure_data.public_id}' created successfully.")
                return True, None

        except Exception as e:
            logger.error(f"create_secure_data: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def edit_secure_data(entry_public_id: str,
                         entry_name: Optional[str],
                         website_enc: Optional[str],
                         username_enc: Optional[str],
                         password_enc: Optional[str],
                         notes_enc: Optional[str]) -> Tuple[bool, Optional[FailureReason]]:
        """Edit an existing instance of secure data"""
        try:
            with Database._get_db_session() as session:
                # Find secure data in question
                secure_data = session.scalar(select(SecureData).where(SecureData.public_id == entry_public_id))
                if not secure_data:
                    logger.warning(f"edit_secure_data: User '{entry_public_id}' could not be found.")
                    return False, FailureReason.ENTRY_NOT_FOUND

                # Edit secure data
                if entry_name:
                    secure_data.entry_name = entry_name
                if website_enc:
                    secure_data.website = website_enc
                if username_enc:
                    secure_data.username = username_enc
                if password_enc:
                    secure_data.password = password_enc
                if notes_enc:
                    secure_data.notes = notes_enc

                logger.info(f"edit_secure_data: Secure data '{entry_public_id}' edited successfully.")
                return True, None

        except Exception as e:
            logger.error(f"edit_secure_data: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def delete_secure_data(entry_public_id: str) -> Tuple[bool, Optional[FailureReason]]:
        """Delete the given secure data entry"""
        try:
            with Database._get_db_session() as session:
                # Find secure data in question
                secure_data = session.scalar(select(SecureData).where(SecureData.public_id == entry_public_id))
                if not secure_data:
                    logger.warning(f"delete_secure_data: Secure Data '{entry_public_id}' could not be found.")
                    return False, FailureReason.ENTRY_NOT_FOUND

                session.delete(secure_data)
                logger.info(f"delete_secure_data: Secure Data '{entry_public_id}' deleted successfully.")
                return True, None

        except Exception as e:
            logger.error(f"delete_secure_data: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def get_secure_entries_list(username: str) -> Tuple[bool, Optional[FailureReason], Optional[List[Tuple[Optional[str], str]]]]:
        """Get names and public ids for all secure entries for a given user, returns [(name, public_id)]"""
        try:
            with Database._get_db_session() as session:
                # Find user in question
                user = session.scalar(select(User).where(User.username == username))
                if not user:
                    logger.warning(f"get_secure_entries_list: User '{username}' could not be found.")
                    return False, FailureReason.USERNAME_NOT_FOUND, None

                # Collate secure data
                return True, None, [(data_entry.entry_name, data_entry.public_id) for data_entry in user.secure_data]

        except Exception as e:
            logger.error(f"get_secure_entries_list: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def get_secure_entry_data(entry_public_id: str) -> Tuple[bool, Optional[FailureReason], Optional[Dict[str, Optional[str]]]]:
        """Get the content of a given secure data entry, if it exists"""
        try:
            with Database._get_db_session() as session:
                # Find secure data in question
                secure_data = session.scalar(select(SecureData).where(SecureData.public_id == entry_public_id))
                if not secure_data:
                    logger.warning(f"get_secure_entry_data: Secure Data '{entry_public_id}' could not be found.")
                    return False, FailureReason.ENTRY_NOT_FOUND, None

                return True, None, {
                    "public_id" : secure_data.public_id,
                    "entry_name" : secure_data.entry_name,
                    "website" : secure_data.website,
                    "username" : secure_data.username,
                    "password" : secure_data.password,
                    "notes" : secure_data.notes
                }

        except Exception as e:
            logger.error(f"get_secure_entry_data: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def create_registeration(secret_key: str, duration_till_expiry: timedelta) -> Tuple[bool, Optional[FailureReason], Optional[str]]:
        """Create a registration with the given secret_key hash and expiry"""
        try:
            with Database._get_db_session() as session:
                # Create new registration
                expiry = datetime.now() + duration_till_expiry
                new_registration = Registration(secret_key=secret_key, expiry=expiry)
                session.add(new_registration)
                session.flush()

                logger.info(f"create_registeration: Secret key registration '{secret_key}' created successfully.")
                return True, None, new_registration.public_id

        except Exception as e:
            logger.error(f"create_registeration: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def fetch_registeration(registration_public_id: str) -> Tuple[bool, Optional[FailureReason], Optional[str]]:
        """Get secret key hash for given public ID"""
        try:
            with Database._get_db_session() as session:
                # Find registration in question
                registration = session.scalar(select(Registration).where(Registration.public_id == registration_public_id))
                if not registration:
                    logger.warning(f"fetch_registeration: Registration '{registration_public_id}' could not be found.")
                    return False, FailureReason.REGISTRATION_NOT_FOUND, None

                if registration.expiry < datetime.now():
                    logger.warning(f"fetch_registeration: Registration '{registration_public_id}' has expired.")
                    session.delete(registration)
                    return False, FailureReason.REGISTRATION_NOT_FOUND, None

                return True, None, registration.secret_key

        except Exception as e:
            logger.error(f"fetch_registeration: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION, None

    @staticmethod
    def delete_registeration(registration_public_id: str) -> Tuple[bool, Optional[FailureReason]]:
        """Delete registration for given public ID"""
        try:
            with Database._get_db_session() as session:
                # Find registration in question
                registration = session.scalar(select(Registration).where(Registration.public_id == registration_public_id))
                if not registration:
                    logger.warning(f"delete_registeration: Registration '{registration_public_id}' could not be found.")
                    return False, FailureReason.REGISTRATION_NOT_FOUND
                session.delete(registration)

                logger.info(f"delete_registeration: Registration {registration_public_id} deleted.")
                return True, None

        except Exception as e:
            logger.error(f"delete_registeration: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION

    @staticmethod
    def clean_registrations():
        """Remove all registrations with past expiry dates"""
        try:
            with Database._get_db_session() as session:
                current_time = datetime.now()
                expired_registrations = session.scalars(
                    select(Registration).where(Registration.expiry < current_time)
                ).all()

                for session_obj in expired_registrations:
                    session.delete(session_obj)

                logger.info(f"clean_registrations: Deleted {len(expired_registrations)} registrations.")
                return True, None

        except Exception as e:
            logger.error(f"clean_registrations: Error - {e}")
            return False, FailureReason.SERVER_EXCEPTION
