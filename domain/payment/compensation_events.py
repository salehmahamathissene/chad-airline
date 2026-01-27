from dataclasses import dataclass
from domain.common.events import Event


@dataclass(frozen=True)
class CompensationGranted(Event):
    ticket_number: str
    amount: int
    currency: str
    regulation: str   # "EU261"
