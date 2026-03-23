from enum import Enum

from passmanager.common.v0.error_pb2 import (
    ErrorCode,
    Error
)


class ServiceError(Enum):

    def __init__(self, error_code: int, description: str):
        self.error_code = error_code
        self.description = description

    def error_proto(self, field: str) -> Error:
        return Error(
            field=field,
            code=self.error_code, # type: ignore
            description=self.description
        )

    FIELD_INVALID       = (ErrorCode.GNR00,   "Field is invalid")
    FIELD_MISSING       = (ErrorCode.GNR01,   "Field is missing")
