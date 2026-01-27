# domain/common/recorded_event.py
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
from typing import Any, Dict, Optional

@dataclass(frozen=True)
class RecordedEvent:
    occurred_at: datetime
    entity_id: str          # e.g., ticket_id
    event_type: str         # e.g., "issued", "paid", "boarded"
    data: Optional[Dict[str, Any]] = field(default_factory=dict)

    def event_id(self) -> str:
        payload = f"{self.entity_id}:{self.event_type}:{self.occurred_at.isoformat()}:{self.data}"
        return hashlib.sha256(payload.encode()).hexdigest()
