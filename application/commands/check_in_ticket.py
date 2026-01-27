from dataclasses import dataclass
from domain.common.identifiers import TicketNumber


@dataclass(frozen=True)
class CheckInTicket:
    """
    Application command.
    Represents a passenger's intent to check in for a ticket.
    """
    ticket_number: TicketNumber
