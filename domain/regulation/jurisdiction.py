from dataclasses import dataclass

@dataclass(frozen=True)
class Jurisdiction:
    code: str        # e.g. "EU", "RW", "INTL"
    authority: str   # e.g. "EASA", "RCAA", "ICAO"
