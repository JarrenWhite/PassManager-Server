from typing import Tuple, Optional

from .utils_enums import FailureReason
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
            (str)  The public ID of the created data entry
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False, FailureReason.NOT_FOUND, ""
                if user.password_change:
                    return False, FailureReason.PASSWORD_CHANGE, ""

                secure_data = SecureData(
                    user=user,
                    entry_name=entry_name,
                    entry_data=entry_data
                )
                session.add(secure_data)
                session.flush()

                return True, None, secure_data.public_id
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED, ""
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION, ""


    @staticmethod
    def edit(
        public_id: str,
        entry_name: Optional[str],
        entry_data: Optional[str]
    ) -> Tuple[bool, Optional[FailureReason]]:
        """
        Adjust a data entry with the given data values, only updating non-null values

        Returns:
            (str)  The public ID of the created data entry
        """
        try:
            with DatabaseSetup.get_db_session() as session:
                secure_data = session.query(SecureData).filter(SecureData.public_id == public_id).first()
                if not secure_data:
                    return False, FailureReason.NOT_FOUND
                if secure_data.user.password_change:
                    return False, FailureReason.PASSWORD_CHANGE

                if entry_name:
                    secure_data.entry_name = entry_name
                if entry_data:
                    secure_data.entry_data = entry_data

                return True, None
        except RuntimeError:
            return False, FailureReason.DATABASE_UNINITIALISED
        except:
            return False, FailureReason.UNKNOWN_EXCEPTION


    @staticmethod
    def delete(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason]]:
        """Delete the given data entry"""
        return False, None


    @staticmethod
    def get_entry(
        public_id: str
    ) -> Tuple[bool, Optional[FailureReason], str, str]:
        """
        Make a data entry with the given data values

        Returns:
            (str)  The encrypted entry name
            (str)  The encrypted entry data
        """
        return False, None, "", ""


    @staticmethod
    def get_list(
        user_id: int
    ) -> Tuple[bool, Optional[FailureReason], dict[str, str]]:
        """
        Make a data entry with the given data values

        Returns:
            (str)  The encrypted entry name
            (str)  The encrypted entry data
        """
        return False, None, {}
