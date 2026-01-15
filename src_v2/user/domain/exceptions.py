class DomainError(Exception):
    """Base class for domain-level exceptions."""
    pass


class BalanceZeroError(DomainError):
    """Raised when a balance reaches zero but zero is considered invalid."""
    pass


class NegativeBalanceError(DomainError):
    """Raised when a balance becomes negative."""
    pass


class UserNotFoundError(DomainError):
    """Raised when a requested user cannot be found in the repository."""
    pass
