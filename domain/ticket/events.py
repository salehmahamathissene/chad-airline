from __future__ import annotations

from dataclasses import dataclass
from domain.common.events import Event
from domain.common.identifiers import FlightId, TicketNumber


@dataclass(frozen=True)
class TicketIssued(Event):
    ticket_number: TicketNumber
    flight_id: FlightId


@dataclass(frozen=True)
class TicketPaid(Event):
    ticket_number: TicketNumber


@dataclass(frozen=True)
class TicketCheckedIn(Event):
    ticket_number: TicketNumber


@dataclass(frozen=True)
class TicketBoarded(Event):
    ticket_number: TicketNumber


@dataclass(frozen=True)
class TicketClosed(Event):
    ticket_number: TicketNumber
