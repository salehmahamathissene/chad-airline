from application.commands.pay_ticket import PayTicket
from domain.common.time import Clock
from domain.ticket.model import Ticket


class PayTicketService:
    """
    Application Service for paying a ticket.
    Orchestrates domain rules and entities.
    """

    def __init__(self, clock: Clock):
        self._clock = clock

    def execute(self, ticket: Ticket, command: PayTicket) -> Ticket:
        """
        Executes the PayTicket command.
        """
        if ticket.state != "ISSUED":
            raise ValueError("Only issued tickets can be paid")

        ticket.mark_paid(self._clock)
        return ticket
