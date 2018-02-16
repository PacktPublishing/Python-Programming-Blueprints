from enum import Enum, auto


class NotificationType(Enum):
    ORDER_RECEIVED = auto()
    ORDER_SHIPPED = auto()