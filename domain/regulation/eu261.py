from domain.regulation.regulation import Regulation
from domain.regulation.compliance_result import ComplianceResult
from domain.regulation.action import RegulatoryAction

class EU261Cancellation(Regulation):
    regulation_id = "EU261-CANCEL"
    jurisdiction = "EU"
    law_version = "2004-02"
    effective_from = 1072915200  # 2004-01-01

    def applies_to(self, *, action, context) -> bool:
        return (
            action == RegulatoryAction.CANCEL
            and context["departure_airport"].jurisdiction == "EU"
        )

    def evaluate(self, *, action, context, evaluated_at: int) -> ComplianceResult:
        delay_hours = context["delay_hours"]

        if delay_hours < 3:
            return ComplianceResult(
                allowed=True,
                obligations=(),
                prohibitions=(),
                regulation_id=self.regulation_id,
                law_version=self.law_version,
                evaluated_at=evaluated_at,
            )

        return ComplianceResult(
            allowed=True,
            obligations=("PAY_COMPENSATION", "OFFER_REBOOKING"),
            prohibitions=(),
            regulation_id=self.regulation_id,
            law_version=self.law_version,
            evaluated_at=evaluated_at,
        )
