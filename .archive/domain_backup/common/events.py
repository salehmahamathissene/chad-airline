from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Event:
    occurred_at: datetime

@dataclass(frozen=True)
class FlightStatusChanged(Event):
    flight_id: str
    old_status: str
    new_status: str

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
