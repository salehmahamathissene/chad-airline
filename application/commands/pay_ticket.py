from dataclasses import dataclass
from domain.common.identifiers import TicketNumber


@dataclass(frozen=True)
class PayTicket:
    """
    Application command.
    Represents a passenger's intent to pay for a ticket.
    """
    ticket_number: TicketNumber
