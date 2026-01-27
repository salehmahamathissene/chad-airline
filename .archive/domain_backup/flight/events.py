from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True)
class FlightCreated:
    flight_id: str
    aircraft_id: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime

@dataclass(frozen=True)
class FlightDelayed:
    flight_id: str
    delay: timedelta

@dataclass(frozen=True)
class FlightDeparted:
    flight_id: str
    occurred_at: datetime

@dataclass(frozen=True)
class FlightArrived:
    flight_id: str
    occurred_at: datetime

@dataclass(frozen=True)
class FlightCancelled:
    flight_id: str
    occurred_at: datetime
