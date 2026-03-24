from typing import Tuple, Optional

from enums import ServiceError


class ServiceUtils():


    @staticmethod
    def sanitise_username(
        input: bytes
    ) -> Tuple[bool, Optional[ServiceError]]:
        return True, None


    @staticmethod
    def sanitise_srp_salt(
        input: bytes
    ) -> Tuple[bool, Optional[ServiceError]]:
        return True, None


    @staticmethod
    def sanitise_srp_verifier(
        input: bytes
    ) -> Tuple[bool, Optional[ServiceError]]:
        return True, None


    @staticmethod
    def sanitise_master_key_salt(
        input: bytes
    ) -> Tuple[bool, Optional[ServiceError]]:
        return True, None
