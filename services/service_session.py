from typing import Tuple, Dict, Any


class ServiceSession():

    @staticmethod
    def start(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
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
