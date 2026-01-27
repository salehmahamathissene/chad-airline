from dataclasses import dataclass

@dataclass(frozen=True)
class FinancialExposure:
    eu261_compensation_eur: float
    denied_boarding_cost_eur: float
    reputational_risk_score: float


@dataclass(frozen=True)
class RiskExposure:
    financial: FinancialExposure
    regulatory_breach_probability: float
