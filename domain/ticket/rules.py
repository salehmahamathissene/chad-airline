from domain.common.errors import InvariantViolation
from domain.flight.model import Flight
from domain.flight.rules import assert_flight_bookable
from domain.ticket.model import Ticket


def assert_ticket_issuable(ticket: Ticket, flight: Flight) -> None:
    """
    Cross-aggregate invariant.
    A ticket may only exist if its flight is bookable.
    """
    if ticket.flight_id != flight.flight_id:
        raise InvariantViolation(
            "Ticket flight_id does not match Flight identity"
        )

    assert_flight_bookable(flight)
