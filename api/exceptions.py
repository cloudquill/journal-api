class EntryNotFoundError(Exception):
    """Raised when a journal entry is not found."""
    pass


class UserAlreadyExists(Exception):
    """Raised for already existing usernames"""
    pass


class WeakPassword(Exception):
    """Raised for weak passwords"""
    pass


class IncorrectCredentials(Exception):
    """Raised for incorrect credentials"""
    pass