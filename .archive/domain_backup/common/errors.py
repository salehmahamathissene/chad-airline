class DomainError(Exception):
    """Base class for all domain-level errors."""
    pass


class InvariantViolation(DomainError):
    """Raised when a domain invariant is violated."""
    pass


class InvalidStateTransition(DomainError):
    """Raised when an illegal state transition is attempted."""
    pass


class CapacityExceeded(DomainError):
    """Raised when capacity constraints are exceeded."""
    pass


class FlightUnavailable(DomainError):
    """Raised when an operation is attempted on an unavailable flight."""
    pass
