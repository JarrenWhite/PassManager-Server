from google.protobuf.message import DecodeError
from passmanager.common.v0.secure_pb2 import (
    SecureRequest,
    SecureResponse
)
from passmanager.data.v0.data_payloads_pb2 import (
    DataCreateRequest,
    DataCreateResponse,
    DataEditRequest,
    DataEditResponse,
    DataDeleteRequest,
    DataDeleteResponse,
    DataGetRequest,
    DataGetResponse,
    DataListRequest,
    DataListResponse
)
from passmanager.common.v0.error_pb2 import (
    Failure
)

from utils import ServiceUtils, SessionManager, DBUtilsData
from enums import FailureReason


# TODO - Placeholder class. Requires completion.

class DataHandler:

    @staticmethod
    def create(secure_request: SecureRequest) -> SecureResponse:
        error_list = []

        # Open secure session
        open_session = SessionManager.open_session(
            request=secure_request,
            password_session=True,
            first_request=True
        )
        status, decrypted_bytes, user_id, failure_reason = open_session
        if not status:
            assert failure_reason
            error_list.append(failure_reason.error_proto())

            failure = Failure(
                error_list=error_list
            )
            return SecureResponse(
                success=False,
                failure_data=failure
            )

        return SecureResponse()

    @staticmethod
    def edit(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def delete(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def get(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def list(secure_request: SecureRequest) -> SecureResponse:
        return SecureResponse()
