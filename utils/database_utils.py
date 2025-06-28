import logging
logger = logging.getLogger("database")

from database import init_db, get_session_local, User

class DatabaseUtils:
    database_initialised = False

    @staticmethod
    def init_database():
        if not DatabaseUtils.database_initialised:
            init_db()
            DatabaseUtils.database_initialised = True
        else:
            return

    @staticmethod
    def create_user(username: str, password_hash: str):
        """Create a new user with the given username and password hash"""
        session = get_session_local()()

        try:
            # Check if user already exists
            existing_user = session.query(User).filter(User.username == username).first()
            if existing_user:
                logger.info(f"User '{username}' already exists!")
                return False
            
            # Create new user
            new_user = User(username=username, password_hash=password_hash)

            session.add(new_user)
            session.commit()
            logger.info(f"User '{username}' created successfully!")
            return True
        
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            session.rollback()
            return False

        finally:
            session.close()
