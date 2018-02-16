from enum import Enum, auto


class Status(Enum):
    Received = auto()
    Processing = auto()
    Payment_Complete = auto()
    Shipping = auto()
    Completed = auto()
    Cancelled = auto()
