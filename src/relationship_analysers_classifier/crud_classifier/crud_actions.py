from enum import Enum

class CrudAction(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_string(cls, value: str) -> "CrudAction":
        """Return the matching CrudAction based on input text."""
        if not value:
            return cls.UNKNOWN
        value = value.strip().lower()
        for action in cls:
            if action.value == value:
                return action
        return cls.UNKNOWN