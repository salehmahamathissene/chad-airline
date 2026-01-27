from dataclasses import dataclass
from domain.common.events import Event
from domain.ticket.denied_boarding import DeniedBoardingReason


@dataclass(frozen=True)
class BoardingDenied(Event):
    ticket_number: str
    flight_id: str
    reason: DeniedBoardingReason
    decided_by: str      # gate_agent_id
    notes: str | None
