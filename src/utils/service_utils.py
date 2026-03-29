from typing import Optional

from enums import ServiceError, FailureReason


class ServiceUtils():


    @staticmethod
    def handle_failure_reason(
        failure_reason: FailureReason,
        field: Optional[str]
    ) -> ServiceError:
        return ServiceError.UNSPECIFIED


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
