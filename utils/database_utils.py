from datetime import timedelta
from typing import Optional, List, Tuple
import logging
logger = logging.getLogger("database")

from sqlalchemy import select

from database import init_db, get_session_local, User, LoginSession, SecureData

class DatabaseUtils:
    database_initialised = False

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
        session = get_session_local()()

        try:
            # Check if user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                logger.debug(f"User '{username}' already exists.")
                return False
            
            # Create new user
            new_user = User(username=username, password_hash=password_hash)

            session.add(new_user)
            session.commit()
            logger.info(f"User '{username}' created successfully.")
            return True
        
        except Exception as e:
            logger.error(f"Error creating user: {e}.")
            session.rollback()
            return False

        finally:
            session.close()

    @staticmethod
    def get_user(username: str) -> Optional(User):
        """Find and return the user. Returns False if not found"""
        session = get_session_local()()
        
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return user.password_hash
            return
            
        except Exception as e:
            logger.error(f"Error retrieving user '{username}': {e}")
            return
            
        finally:
            session.close()

    @staticmethod
    def delete_user(username: str) -> bool:
        """Delete the requested user. Returns False if not found"""
        session = get_session_local()()

        try:
            # Find user in question
            user = session.query(User).filter_by(username=username).first()
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
            session.rollback()
            return False
            
        finally:
            session.close()

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
    def edit_secure_data(secure_data_id: int,
                         entry_name: str,
                         website_enc: str,
                         username_enc: str,
                         password_enc: str,
                         notes_enc: str) -> bool:
        """Edit an existing instance of secure data"""
        pass

    @staticmethod
    def get_all_secure_entries(username: str) -> List[str]:
        """Get names and ids for all secure entries for a given user"""
        pass

    @staticmethod
    def get_details_for_secure_entry(id: int) -> Tuple[]:
        pass
