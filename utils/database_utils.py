from datetime import timedelta
from typing import Optional, List, Tuple
from contextlib import contextmanager
import logging
logger = logging.getLogger("database")

from database import init_db, get_session_local, User, LoginSession, SecureData
from sqlalchemy import select

class DatabaseUtils:
    database_initialised = False

    @staticmethod
    @contextmanager
    def get_db_session():
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
        if not DatabaseUtils.database_initialised:
            init_db()
            DatabaseUtils.database_initialised = True
            return True
        else:
            return False

    @staticmethod
    def create_user(username: str, password_hash: str) -> bool:
        """Create a new user with the given username and password hash"""
        try:
            with DatabaseUtils.get_db_session() as session:
                # Check if user already exists
                existing_user = session.scalar(select(User).where(User.username == username))
                if existing_user:
                    logger.debug(f"User '{username}' already exists.")
                    return False
                
                # Create new user
                new_user = User(username=username, password_hash=password_hash)
                session.add(new_user)
                
                logger.info(f"User '{username}' created successfully.")
                return True
                
        except Exception as e:
            logger.error(f"Error creating user '{username}': {e}")
            return False

    @staticmethod
    def get_user_password_hash(username: str) -> Optional[str]:
        """Find and return the user's password hash. Returns None if not found"""
        try:
            with DatabaseUtils.get_db_session() as session:
                user = session.scalar(select(User).where(User.username == username))
                return user.password_hash if user else None
                
        except Exception as e:
            logger.error(f"Error retrieving user '{username}': {e}")
            return None

    @staticmethod
    def delete_user(username: str) -> bool:
        """Delete the requested user. Returns False if not found"""
        try:
            with DatabaseUtils.get_db_session() as session:
                # Find user in question
                user = session.scalar(select(User).where(User.username == username))
                if not user:
                    logger.warning(f"User '{username}' could not be found to be deleted.")
                    return False
            
                # Delete the user
                session.delete(user)
                session.commit()
            
                logger.info(f"User '{username}' deleted successfully.")
                return True
            
        except Exception as e:
            logger.error(f"Error deleting user '{username}': {e}")
            return False

    @staticmethod
    def create_session(username: str, token: str, duration_till_expiry: timedelta) -> bool:
        """Create a session for the given user"""
        pass

    @staticmethod
    def check_session_token(token: str) -> Optional[str]:
        """Check if a session token is valid, and if so returning the Username."""
        pass

    @staticmethod
    def delete_session(token: str) -> bool:
        """Delete the given session"""
        pass

    @staticmethod
    def delete_all_sessions(username: str) -> bool:
        """Delete all sessions for the given user"""
        pass

    @staticmethod
    def clean_sessions():
        """Remove all sessions with past expiry dates"""
        pass

    @staticmethod
    def create_secure_data(username: str,
                           entry_name: str,
                           website_enc: str,
                           username_enc: str,
                           password_enc: str,
                           notes_enc: str) -> bool:
        """Create an instance of secure data"""
        pass

    @staticmethod
    def edit_secure_data(entry_public_id: str,
                         entry_name: Optional[str],
                         website_enc: Optional[str],
                         username_enc: Optional[str],
                         password_enc: Optional[str],
                         notes_enc: Optional[str]) -> bool:
        """Edit an existing instance of secure data"""
        pass

    @staticmethod
    def delete_secure_data(entry_public_id: str):
        """Delete given secure data entry"""
        pass

    @staticmethod
    def get_secure_entries_list(username: str) -> List[Tuple[str, str]]:
        """Get names and public ids for all secure entries for a given user"""
        pass

    @staticmethod
    def get_secure_entry_data(public_entry_id: str) -> Optional[Tuple[str, str, str, str, str]]:
        """Get the content of a given secure data entry, if it exists"""
        pass
