from enum import Enum


class IrropsCause(Enum):
    WEATHER = "weather"
    TECHNICAL = "technical"
    CREW = "crew"
    ATC = "air_traffic_control"
    SECURITY = "security"
    AIRPORT = "airport"
    UNKNOWN = "unknown"
