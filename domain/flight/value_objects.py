from dataclasses import dataclass


@dataclass(frozen=True)
class FlightId:
    value: str

    def __str__(self) -> str:
        return self.value
