from typing import Tuple, Dict, Any

from utils import DBUtilsUser

class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        DBUtilsUser.create(data["username_hash"], data["srp_salt"], data["srp_verifier"], data["master_key_salt"])
        return {}, 200

    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
