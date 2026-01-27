from dataclasses import dataclass
from domain.common.identifiers import TicketNumber


@dataclass(frozen=True)
class BoardTicket:
    """
    Application command.
    Represents a passenger's intent to board a ticket.
    """
    ticket_number: TicketNumber
