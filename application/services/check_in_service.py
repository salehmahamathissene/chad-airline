from application.commands.check_in_ticket import CheckInTicket
from domain.common.time import Clock
from domain.ticket.model import Ticket


class CheckInService:
    """
    Application Service for checking in a ticket.
    Orchestrates domain rules and state transitions.
    """

    def __init__(self, clock: Clock):
        self._clock = clock

    def execute(self, ticket: Ticket, command: CheckInTicket) -> Ticket:
        """
        Executes the CheckInTicket command.
        """
        if ticket.state != "PAID":
            raise ValueError("Only paid tickets can be checked in")

        ticket.check_in(self._clock)
        return ticket
