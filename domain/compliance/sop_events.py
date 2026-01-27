from dataclasses import dataclass
from domain.common.events import Event


@dataclass(frozen=True)
class SopViolationDetected(Event):
    flight_id: str
    action: str
    actual_delay_minutes: int
    expected_max_minutes: int

TicketBoardingFailed
SopViolationDetected
SystemOverride (Captain)
BoardingDenied
CompensationGranted
