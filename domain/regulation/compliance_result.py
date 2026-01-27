from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class ComplianceResult:
    allowed: bool
    obligations: Tuple[str, ...]   # e.g. compensation, rebooking
    prohibitions: Tuple[str, ...]  # explicit blockers
    regulation_id: str
    law_version: str
    evaluated_at: int  # epoch seconds (passed in, never read)
