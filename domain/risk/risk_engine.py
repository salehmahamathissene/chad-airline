from typing import List
from domain.common.recorded_event import RecordedEvent
from domain.risk.risk_metrics import RiskMetrics
from domain.risk.exposure import RiskExposure, FinancialExposure


class RiskEngine:
    """
    Read-only decision engine.
    Consumes past events, emits NOTHING.
    """

    def evaluate(self, events: List[RecordedEvent]) -> RiskExposure:
        issued = len([e for e in events if e.name == "TicketIssued"])
        boarded = len([e for e in events if e.name == "TicketBoarded"])
        denied = len([e for e in events if e.name == "DeniedBoarding"])
        unpaid = len([e for e in events if e.name == "TicketIssued"]) - \
                 len([e for e in events if e.name == "TicketPaid"])

        if issued == 0:
            return self._zero_risk()

        metrics = RiskMetrics(
            boarding_conversion_rate=boarded / issued,
            denied_boarding_rate=denied / issued,
            payment_failure_rate=unpaid / issued,
            delay_probability=self._estimate_delay_probability(events)
        )

        return self._calculate_exposure(metrics)

    def _calculate_exposure(self, metrics: RiskMetrics) -> RiskExposure:
        eu261 = 600 * metrics.delay_probability * 20  # €600 * estimated pax
        denied_cost = 400 * metrics.denied_boarding_rate * 10

        financial = FinancialExposure(
            eu261_compensation_eur=eu261,
            denied_boarding_cost_eur=denied_cost,
            reputational_risk_score=metrics.denied_boarding_rate * 10
        )

        regulatory_risk = (
            metrics.delay_probability * 0.6 +
            metrics.denied_boarding_rate * 0.4
        )

        return RiskExposure(
            financial=financial,
            regulatory_breach_probability=regulatory_risk
        )

    def _estimate_delay_probability(self, events: List[RecordedEvent]) -> float:
        disruptions = [e for e in events if "Delay" in e.name or "Irrops" in e.name]
        return min(1.0, len(disruptions) * 0.15)

    def _zero_risk(self) -> RiskExposure:
        return RiskExposure(
            financial=FinancialExposure(0.0, 0.0, 0.0),
            regulatory_breach_probability=0.0
        )
