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


# TODO - Placeholder class. Requires completion.

class DataHandler:

    @staticmethod
    def create(request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def edit(request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def delete(request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def get(request: SecureRequest) -> SecureResponse:
        return SecureResponse()

    @staticmethod
    def list(request: SecureRequest) -> SecureResponse:
        return SecureResponse()
