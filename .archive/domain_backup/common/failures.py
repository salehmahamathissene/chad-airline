from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

from domain.common.errors import InvariantViolation


@dataclass(frozen=True)
class DomainFailure:
    """
    Immutable record of a failed domain attempt.
    Required for audit & forensic analysis.
    """
    reason: str
    occurred_at: datetime
    authority: str
    context: Dict[str, Any]

    def __post_init__(self):
        if self.occurred_at.tzinfo is None:
            raise InvariantViolation(
                "Failure time must be timezone-aware"
            )

        if not self.reason:
            raise InvariantViolation(
                "Failure must have a reason"
            )
