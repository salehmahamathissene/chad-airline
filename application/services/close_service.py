from application.commands.close_ticket import CloseTicket
from domain.common.time import Clock
from domain.ticket.model import Ticket


class CloseService:
    """
    Application Service for closing a ticket.
    Finalizes the ticket lifecycle.
    """

    def __init__(self, clock: Clock):
        self._clock = clock

    def execute(self, ticket: Ticket, command: CloseTicket) -> Ticket:
        """
        Executes the CloseTicket command.
        """
        if ticket.state != "BOARDED":
            raise ValueError("Only boarded tickets can be closed")

        ticket.close(self._clock)
        return ticket
