from application.commands.board_ticket import BoardTicket
from domain.common.time import Clock
from domain.ticket.model import Ticket


class BoardService:
    """
    Application Service for boarding a ticket.
    Orchestrates domain rules and state transitions.
    """

    def __init__(self, clock: Clock):
        self._clock = clock

    def execute(self, ticket: Ticket, command: BoardTicket) -> Ticket:
        """
        Executes the BoardTicket command.
        """
        if ticket.state != "CHECKED_IN":
            raise ValueError("Only checked-in tickets can be boarded")

        ticket.board(self._clock)
        return ticket
