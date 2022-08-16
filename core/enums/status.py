from enum import Enum


class StatusOrder(Enum):
    NEW = "1"
    IN_WORK = "2"
    WAITING = "3"
    FAILED = "4"
    COMPLETED = "5"
