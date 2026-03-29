from typing import Optional
from enum import Enum

from passmanager.common.v0.error_pb2 import (
    ErrorCode,
    Error
)


class FailureReason(Enum):

    def __init__(self, error_code: int, field: Optional[str], description: str):
        self.error_code = error_code
        self.field = field
        self.description = description

    def error_proto(self, field: Optional[str]) -> Error:
        use_field = self.field if self.field is not None else field

        if use_field is None:
            use_field = "unknown"

        return Error(
            field=use_field,
            code=self.error_code, # type: ignore
            description=self.description
        )

    UNSPECIFIED             = (ErrorCode.UNSPECIFIED,   "unknown",  "Unknown error encountered")

    PARAMETERS              = (ErrorCode.RQS00,     "request",  "")
    DECRYPTION              = (ErrorCode.RQS01,     "request",  "")
    PASSWORD_CHANGE         = (ErrorCode.RQS02,     "request",  "")
    TOO_MANY                = (ErrorCode.RQS03,     "request",  "")

    UNKNOWN_EXCEPTION       = (ErrorCode.SVR00,     "server",   "")
    DATABASE_UNINITIALISED  = (ErrorCode.SVR01,     "server",   "")

    USER_EXISTS             = (ErrorCode.OPR00,     "username", "")
    REQUEST_NUMBER          = (ErrorCode.OPR01,     "request",  "")
    INCOMPLETE              = (ErrorCode.OPR02,     "request",  "")
    ENTRY_UPDATED           = (ErrorCode.OPR03,     "server",   "")

    INVALID                 = (ErrorCode.GNR00,     None,       "")
    NOT_FOUND               = (ErrorCode.GNR01,     None,       "")
