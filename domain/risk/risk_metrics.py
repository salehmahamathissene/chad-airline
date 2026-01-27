from dataclasses import dataclass

@dataclass(frozen=True)
class RiskMetrics:
    boarding_conversion_rate: float   # boarded / issued
    denied_boarding_rate: float        # denied / issued
    payment_failure_rate: float        # unpaid / issued
    delay_probability: float           # derived from events
