from dataclasses import dataclass
from domain.common.events import Event
from domain.flight.irrops import IrropsCause


@dataclass(frozen=True)
class IrropsDeclared(Event):
    flight_id: str
    cause: IrropsCause
    declared_by: str        # OCC | captain | ATC
    reference: str | None   # METAR, MEL, ATC notice


@dataclass(frozen=True)
class IrropsCleared(Event):
    flight_id: str
    cleared_by: str
