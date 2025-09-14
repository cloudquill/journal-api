class EntryNotFoundError(Exception):
    """Raised when a journal entry is not found."""
    pass


class JournalError(Exception):
    """Raised for general journal-related errors."""
    pass