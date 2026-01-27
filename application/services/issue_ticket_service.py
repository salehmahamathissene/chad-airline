from application.commands.issue_ticket import IssueTicket
from domain.common.time import Clock
from domain.ticket.model import Ticket
from domain.ticket.rules import assert_ticket_issuable
from domain.flight.model import Flight


class IssueTicketService:
    """
    Application Service for issuing a ticket.
    Orchestrates domain rules and entities.
    """

    def __init__(self, clock: Clock):
        self._clock = clock

    def execute(self, command: IssueTicket, flight: Flight) -> Ticket:
        """
        Executes the IssueTicket command.
        """
        # Create ticket instance (domain truth)
        ticket = Ticket.issue(
            ticket_number=command.ticket_number,
            flight_id=command.flight_id,
            passenger_id=command.passenger_id,
            clock=self._clock,
        )

        # Cross-aggregate rule: flight must be bookable
        assert_ticket_issuable(ticket, flight)

        return ticket
