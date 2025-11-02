from enum import Enum, auto


class FailureReason(Enum):
    DATABASE_UNINITIALISED = auto()
    UNKNOWN_EXCEPTION = auto()
    DUPLICATE = auto()
    NOT_FOUND = auto()
    PASSWORD_CHANGE = auto()
    INCOMPLETE = auto()
