from dataclasses import dataclass
from domain.common.identifiers import TicketNumber


@dataclass(frozen=True)
class CloseTicket:
    """
    Application command.
    Represents intent to close a ticket after boarding.
    """
    ticket_number: TicketNumber
