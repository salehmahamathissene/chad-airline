from dataclasses import dataclass


@dataclass(frozen=True)
class Eu261Compensation:
    amount_eur: int
    currency: str = "EUR"
