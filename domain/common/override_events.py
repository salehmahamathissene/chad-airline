from dataclasses import dataclass
from domain.common.events import Event
from domain.common.override import OverrideReason


@dataclass(frozen=True)
class SystemOverride(Event):
    aggregate_id: str        # ticket_id / flight_id
    overridden_event: str    # e.g. "TicketBoarded"
    reason: OverrideReason
    authorized_by: str       # staff_id
    justification: str
