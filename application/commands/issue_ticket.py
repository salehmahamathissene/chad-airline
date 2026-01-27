from dataclasses import dataclass
from domain.common.identifiers import FlightId, TicketNumber


@dataclass(frozen=True)
class IssueTicket:
    """
    Application command.
    Represents an explicit user intent.
    """
    ticket_number: TicketNumber
    flight_id: FlightId
    passenger_id: str
