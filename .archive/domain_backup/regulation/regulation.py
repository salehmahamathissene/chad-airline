from abc import ABC, abstractmethod
from domain.regulation.compliance_result import ComplianceResult
from domain.regulation.action import RegulatoryAction

class Regulation(ABC):
    regulation_id: str
    jurisdiction: str
    law_version: str
    effective_from: int

    @abstractmethod
    def applies_to(self, *, action, context) -> bool:
        ...

    @abstractmethod
    def evaluate(self, *, action, context, evaluated_at: int) -> ComplianceResult:
        ...
