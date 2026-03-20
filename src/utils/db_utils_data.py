from typing import Tuple, Optional

from logging import getLogger
logger = getLogger("database")

from enums import FailureReason
from database import DatabaseSetup, SecureData, User


class DBUtilsData():
    """Utility functions for managing data based database functions"""

    @staticmethod
    def create(
        user_id: int,
        entry_name: str,
        entry_data: str
    ) -> Tuple[bool, Optional[FailureReason], str]:
        """
        Make a data entry with the given data values

        Returns:
            (str)   The public ID of the created data entry
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.debug("User id: %s not found.", user_id)
                    return False, FailureReason.NOT_FOUND, ""
                if user.password_change:
                    logger.debug("User: %s undergoing password change.", user.username_hash[-4:])
                    return False, FailureReason.PASSWORD_CHANGE, ""

                secure_data = SecureData(
                    user=user,
                    entry_name=entry_name,
                    entry_data=entry_data
                )
                session.add(secure_data)
                session.flush()

                logger.info("Secure Data: %s created.", secure_data.public_id[-4:])
                return True, None, secure_data.public_id
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def edit(
        user_id: int,
        public_id: str,
        entry_name: Optional[bytes],
        entry_data: Optional[bytes]
    ) -> Tuple[bool, Optional[FailureReason]]:
        """
        Adjust a data entry with the given data values, only updating non-null values

        Returns:
            (str)   The public ID of the created data entry
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                secure_data = session.query(SecureData).filter(SecureData.public_id == public_id).first()

                if not secure_data:
                    logger.debug("Secure Data: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.id != user_id:
                    logger.debug("Secure Data: %s does not belong to user.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.password_change:
                    logger.debug("Secure Data: %s undergoing password change.", secure_data.public_id[-4:])
                    return False, FailureReason.PASSWORD_CHANGE

                if entry_name:
                    secure_data.entry_name = entry_name
                if entry_data:
                    secure_data.entry_data = entry_data

                logger.info("Secure Data: %s edited.", public_id[-4:])
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def delete(
        user_id: int,
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Delete the given data entry"""
        try:
            with DatabaseSetup.get_db_session() as session:
                secure_data = session.query(SecureData).filter(SecureData.public_id == public_id).first()

                if not secure_data:
                    logger.debug("Secure Data: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.id != user_id:
                    logger.debug("Secure Data: %s does not belong to user.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.password_change:
                    logger.debug("Secure Data: %s undergoing password change.", secure_data.public_id[-4:])
                    return False, FailureReason.PASSWORD_CHANGE

                session.delete(secure_data)

                logger.info("Secure Data: %s deleted.", public_id[-4:])
                return True, None
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def get_entry(
        user_id: int,
        public_id: str,
        password_change: bool = False
    ) -> Tuple[bool, Optional[FailureReason], bytes, bytes]:
        """
        Make a data entry with the given data values

        Returns:
            (bytes) The encrypted entry name
            (bytes) The encrypted entry data
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                secure_data = session.query(SecureData).filter(SecureData.public_id == public_id).first()

                if not secure_data:
                    logger.debug("Secure Data: %s not found.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, b'', b''
                if secure_data.user.id != user_id:
                    logger.debug("Secure Data: %s does not belong to user.", public_id[-4:])
                    return False, FailureReason.NOT_FOUND, b'', b''
                if secure_data.user.password_change and not password_change:
                    logger.debug("Secure Data: %s undergoing password change.", secure_data.public_id[-4:])
                    return False, FailureReason.PASSWORD_CHANGE, b'', b''

                logger.info("Secure Data: %s requested.", public_id[-4:])
                return True, None, secure_data.entry_name, secure_data.entry_data
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, b'', b''
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, b'', b''


    @staticmethod
    def get_list(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason], dict[str, bytes]]:
        """
        Make a data entry with the given data values

        Returns:
            dict[str, bytes]
                (str)   The encrypted entry public id
                (bytes) The encrypted entry name
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()

                if not user:
                    logger.debug("User id: %s not found.", user_id)
                    return False, FailureReason.NOT_FOUND, {}
                if user.password_change:
                    logger.debug("User: %s undergoing password change.", user.username_hash[-4:])
                    return False, FailureReason.PASSWORD_CHANGE, {}

                all_entries = {data.public_id: data.entry_name for data in user.secure_data}

                logger.info("Secure Data List requested for User: %s.", user.username_hash[-4:])
                return True, None, all_entries
        except RuntimeError:
            logger.warning("Database uninitialised.")
            return False, FailureReason.DATABASE_UNINITIALISED, {}
        except:
            logger.exception("Unknown database session exception.")
            return False, FailureReason.UNKNOWN_EXCEPTION, {}
