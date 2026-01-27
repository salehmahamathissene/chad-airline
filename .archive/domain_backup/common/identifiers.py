from dataclasses import dataclass


@dataclass(frozen=True)
class FlightId:
    """
    Immutable identity for a Flight.
    Not a database ID.
    """
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("FlightId value must be non-empty")


@dataclass(frozen=True)
class TicketNumber:
    """
    Immutable, externally visible ticket number.
    """
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("TicketNumber value must be non-empty")
