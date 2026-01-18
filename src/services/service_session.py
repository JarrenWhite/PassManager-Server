from typing import Tuple, Dict, Any

from utils import DBUtilsSession, ServiceUtils, SessionManager


class ServiceSession():

    @staticmethod
    def start(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:

        keys = {"username"}
        sanitised, errors, http_code = ServiceUtils.sanitise_inputs(data, keys)
        if not sanitised:
            return {"success": False, "errors": errors}, http_code

        return {}, 200

    @staticmethod
    def auth(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def delete(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200

    @staticmethod
    def clean(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        return {}, 200
