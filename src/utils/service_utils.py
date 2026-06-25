from typing import Optional

from enums import FailureReason


class ServiceUtils():

    @staticmethod
    def sanitise_username_hash(
        input: bytes
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_srp_salt(
        input: bytes
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_srp_verifier(
        input: bytes
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_master_key_salt(
        input: bytes
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_entry_name(
        input: bytes
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_entry_data(
        input: bytes
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_public_id(
        input: str
    ) -> Optional[FailureReason]:
        return None


    @staticmethod
    def sanitise_eph_val_a(
        input: bytes
    )-> Optional[FailureReason]:
      return None


    @staticmethod
    def sanitise_proof_val_m1(
        input: bytes
    )-> Optional[FailureReason]:
      return None


    @staticmethod
    def sanitise_request_count(
        input: int
    )-> Optional[FailureReason]:
      return None


    @staticmethod
    def sanitise_expiry_time(
        input: int
    )-> Optional[FailureReason]:
      return None
