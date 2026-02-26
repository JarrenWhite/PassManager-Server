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
    def create(request: DataCreateRequest) -> DataCreateResponse:
        return DataCreateResponse()

    @staticmethod
    def edit(request: DataEditRequest) -> DataEditResponse:
        return DataEditResponse()

    @staticmethod
    def delete(request: DataDeleteRequest) -> DataDeleteResponse:
        return DataDeleteResponse()

    @staticmethod
    def get(request: DataGetRequest) -> DataGetResponse:
        return DataGetResponse()

    @staticmethod
    def list(request: DataListRequest) -> DataListResponse:
        return DataListResponse()
