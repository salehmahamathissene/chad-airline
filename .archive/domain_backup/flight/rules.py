from domain.common.errors import FlightUnavailable
from domain.flight.model import Flight, FlightStatus


def assert_flight_bookable(flight: Flight) -> None:
    """
    A flight is bookable only if it is not cancelled.
    """
    if flight.status == FlightStatus.CANCELLED:
        raise FlightUnavailable(
            "Cannot issue tickets for a cancelled flight"
        )
