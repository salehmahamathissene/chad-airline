from dataclasses import dataclass
from datetime import datetime
from domain.common.events import Event


# -------------------------------------------------
# Ticket Lifecycle Events (Authoritative)
# -------------------------------------------------

@dataclass(frozen=True)
class TicketIssued(Event):
    ticket_id: str
    flight_id: str
    passenger_id: str


@dataclass(frozen=True)
class TicketPaid(Event):
    ticket_id: str


@dataclass(frozen=True)
class TicketCheckedIn(Event):
    ticket_id: str


@dataclass(frozen=True)
class TicketBoarded(Event):
    ticket_id: str


@dataclass(frozen=True)
class TicketClosed(Event):
    ticket_id: str
