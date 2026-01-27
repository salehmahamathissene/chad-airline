from dataclasses import dataclass


@dataclass(frozen=True)
class SopExpectation:
    action: str
    max_delay_minutes: int

BOARDING_CLOSE = SopExpectation(
    action="boarding_close",
    max_delay_minutes=15
)
