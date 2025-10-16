from typing import Tuple, Optional

from .utils_enums import FailureReason


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
        return False, None, ""


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
        return False, None


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
