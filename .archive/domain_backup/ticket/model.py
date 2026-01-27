from domain.common.event_record import EventRecord
from dataclasses import dataclass
from datetime import datetime

from domain.common.errors import InvariantViolation
from domain.common.identifiers import FlightId, TicketNumber
from domain.common.time import Clock
from domain.ticket.states import TICKET_STATES


@dataclass
class Ticket:
    """
    Pure domain Ticket entity.
    Represents a legal contract between passenger and airline.
    """
    ticket_number: TicketNumber
    flight_id: FlightId
    passenger_id: str
    state: str
    issued_at: datetime
    last_state_change_at: datetime

    @classmethod
    def issue(
        cls,
        ticket_number: TicketNumber,
        flight_id: FlightId,
        passenger_id: str,
        clock: Clock,
    ) -> "Ticket":
        now = clock.now()

        if now.tzinfo is None:
            raise InvariantViolation(
                "Ticket issue time must be timezone-aware"
            )

        if not passenger_id or not passenger_id.strip():
            raise InvariantViolation(
                "Passenger identity must be provided"
            )

        return cls(
            ticket_number=ticket_number,
            flight_id=flight_id,
            passenger_id=passenger_id,
            state="ISSUED",
            issued_at=now,
            last_state_change_at=now,
        )

    def _transition(self, to_state: str, clock: Clock) -> None:
        TICKET_STATES.assert_transition(self.state, to_state)

        now = clock.now()
        if now.tzinfo is None:
            raise InvariantViolation(
                "State transition time must be timezone-aware"
            )

        self.state = to_state
        self.last_state_change_at = now

    def mark_paid(self, clock: Clock) -> None:
        self._transition("PAID", clock)

    def check_in(self, clock: Clock) -> None:
        self._transition("CHECKED_IN", clock)

    def board(self, clock: Clock) -> None:
        self._transition("BOARDED", clock)

    def close(self, clock: Clock) -> None:
        self._transition("CLOSED", clock)

@classmethod
def rehydrate(cls, events: list[EventRecord]) -> "Ticket":
    if not events:
        raise ValueError("Cannot rehydrate Ticket without events")

    ticket = cls._empty()
    for event in events:
        ticket._apply(event)

    return ticket

def _apply(self, event: EventRecord) -> None:
    if event.event_type == "TicketIssued":
        self._apply_issued(event)
    elif event.event_type == "TicketPaid":
        self._apply_paid(event)
    elif event.event_type == "TicketCheckedIn":
        self._apply_checked_in(event)
    elif event.event_type == "TicketBoarded":
        self._apply_boarded(event)
    elif event.event_type == "TicketClosed":
        self._apply_closed(event)
    else:
        raise RuntimeError(f"Unknown event: {event.event_type}")

def __init__(self):
    self._version: int = 0

def _apply(self, event: EventRecord) -> None:
    if event.version != self._version + 1:
        raise RuntimeError(
            f"Version mismatch: expected {self._version + 1}, got {event.version}"
        )

    self._version = event.version

    # then apply state change
