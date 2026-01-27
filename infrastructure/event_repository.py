from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from domain.common.identifiers import FlightId, TicketNumber
from domain.ticket.events import (
    TicketIssued,
    TicketPaid,
    TicketCheckedIn,
    TicketBoarded,
    TicketClosed,
)

_EVENT_TYPES = {
    "TicketIssued": TicketIssued,
    "TicketPaid": TicketPaid,
    "TicketCheckedIn": TicketCheckedIn,
    "TicketBoarded": TicketBoarded,
    "TicketClosed": TicketClosed,
}


class EventRepository:
    """
    File-based event repository.

    Writes one JSON line per event:
      out/<run_id>/logs/flight_<FLIGHT_ID>_events.log
    """

    def __init__(self, base_dir: Path | str = Path("./out/default")) -> None:
        self.base_dir = Path(base_dir)
        self.log_dir = self.base_dir / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def save(self, flight_id: str, event) -> None:
        """
        Instance method: save one event into the flight log file.
        """
        if not is_dataclass(event):
            raise TypeError("EventRepository.save expects a dataclass event")

        log_file = self.log_dir / f"flight_{flight_id}_events.log"
        payload = asdict(event)

        # Ensure occurred_at is timezone-aware UTC
        occurred_at = getattr(event, "occurred_at", None)
        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)

        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)

        payload["occurred_at"] = occurred_at.isoformat()

        record = {
            "event_name": getattr(event, "name", event.__class__.__name__),
            "payload": payload,
        }

        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def save_event(self, flight_id: str, event) -> None:
        """
        Backward-compatible alias used by old simulators:
            repo.save_event(...)
        """
        return self.save(flight_id, event)

    def load_stream(self, flight_id: str) -> List[object]:
        """
        Load and re-hydrate events for a flight.
        """
        log_file = self.log_dir / f"flight_{flight_id}_events.log"
        if not log_file.exists():
            return []

        events: List[object] = []
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                record = json.loads(line)
                name = record.get("event_name")
                payload = record.get("payload", {})

                # parse occurred_at
                if "occurred_at" in payload:
                    occurred_at = datetime.fromisoformat(payload["occurred_at"])
                    if occurred_at.tzinfo is None:
                        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
                    payload["occurred_at"] = occurred_at

                # convert identifiers back
                if "flight_id" in payload and isinstance(payload["flight_id"], dict):
                    payload["flight_id"] = FlightId(payload["flight_id"]["value"])
                elif "flight_id" in payload and isinstance(payload["flight_id"], str):
                    payload["flight_id"] = FlightId(payload["flight_id"])

                if "ticket_number" in payload and isinstance(payload["ticket_number"], dict):
                    payload["ticket_number"] = TicketNumber(payload["ticket_number"]["value"])
                elif "ticket_number" in payload and isinstance(payload["ticket_number"], str):
                    payload["ticket_number"] = TicketNumber(payload["ticket_number"])

                cls = _EVENT_TYPES.get(name)
                if cls is None:
                    # unknown event type - ignore safely
                    continue

                try:
                    events.append(cls(**payload))
                except TypeError:
                    # payload mismatch - ignore safely
                    continue

        return events
