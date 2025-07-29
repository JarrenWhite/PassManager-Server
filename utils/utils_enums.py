from enum import Enum, auto


class FailureReason(Enum):
    SERVER_EXCEPTION = auto()
    ALREADY_EXISTS = auto()
    USERNAME_NOT_FOUND = auto()
    SESSION_NOT_FOUND = auto()
    ENTRY_NOT_FOUND = auto()
    REGISTRATION_NOT_FOUND = auto()
