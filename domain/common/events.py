from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True, kw_only=True)
class Event:
    """
    Base class for all domain events.
    kw_only=True prevents dataclass default/non-default ordering issues
    when subclass adds required fields.
    """
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def name(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class FlightStatusChanged(Event):
    flight_id: str
    old_status: str
    new_status: str
