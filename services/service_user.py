from typing import Tuple, Dict, Any


class ServiceUser():

    @staticmethod
    def user_register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def user_username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def user_delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
