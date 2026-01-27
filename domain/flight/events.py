# domain/flight/events.py
from dataclasses import dataclass
from datetime import datetime
from domain.flight.enums import FlightStatus

# --- Flight Events ---

@dataclass
class FlightCreated:
    occurred_at: datetime
    flight_id: str
    departure_time: datetime
    arrival_time: datetime

@dataclass
class FlightCancelled:
    occurred_at: datetime
    flight_id: str
    reason: str | None = None

@dataclass
class FlightDelayed:
    occurred_at: datetime
    flight_id: str
    delay_minutes: int

@dataclass
class FlightDeparted:
    occurred_at: datetime
    flight_id: str

@dataclass
class FlightArrived:
    occurred_at: datetime
    flight_id: str

@dataclass
class FlightStatusChanged:
    occurred_at: datetime
    flight_id: str
    old_status: FlightStatus
    new_status: FlightStatus

# --- Ticket Events for reference ---
# (optional but often needed in simulators)
@dataclass
class TicketIssued:
    occurred_at: datetime
    ticket_id: str
    flight_id: str
    passenger_id: str

@dataclass
class TicketPaid:
    occurred_at: datetime
    ticket_id: str

@dataclass
class TicketCheckedIn:
    occurred_at: datetime
    ticket_id: str

@dataclass
class TicketBoarded:
    occurred_at: datetime
    ticket_id: str

@dataclass
class TicketClosed:
    occurred_at: datetime
    ticket_id: str
