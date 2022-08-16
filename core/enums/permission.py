from enum import Enum

NOT_ALLOW = "999"


class PermissionEnum(Enum):
    ADMIN = "001"
    READERWRITER = "002"
    READER = "003"
    NOT_ALLOW = "999"
