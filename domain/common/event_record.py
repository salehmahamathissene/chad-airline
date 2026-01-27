from dataclasses import dataclass
from typing import Any, Tuple, Optional
from domain.common.attestation import Attestation
from domain.regulation.compliance_result import ComplianceResult


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    aggregate_id: str
    event_type: str
    payload: Any
    occurred_at: int

    compliance: Tuple[ComplianceResult, ...]
    attestation: Attestation
