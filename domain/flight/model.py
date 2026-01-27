from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from domain.common.identifiers import FlightId
from .enums import FlightStatus


@dataclass()
class Flight:
    flight_id: FlightId
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    aircraft_id: str
    status: FlightStatus = FlightStatus.SCHEDULED

    def delay(self, minutes: int) -> "Flight":
        return replace(
            self,
            departure_time=self.departure_time + timedelta(minutes=minutes),
            arrival_time=self.arrival_time + timedelta(minutes=minutes),
        )

    def cancel(self) -> "Flight":
        if self.status == FlightStatus.CANCELLED:
            return self
        return replace(self, status=FlightStatus.CANCELLED)

def apply_irrops_declared(self, event):
    self.irrops_active = True
    self.irrops_cause = event.cause
