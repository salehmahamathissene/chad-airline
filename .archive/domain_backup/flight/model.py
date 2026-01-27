from dataclasses import dataclass
from datetime import datetime, timedelta
from domain.flight.events import FlightCreated, FlightDelayed, FlightDeparted, FlightArrived, FlightCancelled

class FlightStatus:
    SCHEDULED = "scheduled"
    DEPARTED = "departed"
    ARRIVED = "arrived"
    CANCELLED = "cancelled"

@dataclass(frozen=True)
class Flight:
    flight_id: str
    aircraft_id: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    status: str = FlightStatus.SCHEDULED

    def apply_event(self, event):
        if isinstance(event, FlightDelayed):
            object.__setattr__(self, "departure_time", self.departure_time + event.delay)
        elif isinstance(event, FlightDeparted):
            object.__setattr__(self, "status", FlightStatus.DEPARTED)
        elif isinstance(event, FlightArrived):
            object.__setattr__(self, "status", FlightStatus.ARRIVED)
        elif isinstance(event, FlightCancelled):
            object.__setattr__(self, "status", FlightStatus.CANCELLED)
