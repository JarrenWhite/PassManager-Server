from typing import Tuple, Dict, Any

from utils import DBUtilsUser, ServiceUtils, SessionManager
from .session_keys import SESSION_KEYS


class ServiceUser():

    @staticmethod
    def register(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        keys = {"new_username", "srp_salt", "srp_verifier", "master_key_salt"}
        ServiceUtils.sanitise_inputs(data, keys)

        return {}, 200


    @staticmethod
    def username(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        return {}, 200


    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        return {}, 200
