from typing import Tuple, Optional

from enums import ServiceError


class ServiceUtils():


    @staticmethod
    def sanitise_username(
        input: bytes
    ) -> Optional[ServiceError]:
        return None


    @staticmethod
    def sanitise_srp_salt(
        input: bytes
    ) -> Optional[ServiceError]:
        return None


    @staticmethod
    def sanitise_srp_verifier(
        input: bytes
    ) -> Optional[ServiceError]:
        return None


    @staticmethod
    def sanitise_master_key_salt(
        input: bytes
    ) -> Optional[ServiceError]:
        return None
