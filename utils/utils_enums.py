from enum import Enum, auto


class FailureReason(Enum):
    DATABASE_UNINITIALISED = auto()
    UNKNOWN_EXCEPTION = auto()
    DUPLICATE = auto()
    NOT_FOUND = auto()
    NO_MATCH = auto()
