from dataclasses import dataclass
from enum import Enum

from domain.common.errors import InvariantViolation


class AuthorityRole(str, Enum):
    SYSTEM = "SYSTEM"
    PASSENGER = "PASSENGER"
    CHECKIN_AGENT = "CHECKIN_AGENT"
    GATE_AGENT = "GATE_AGENT"
    FLIGHT_OPS = "FLIGHT_OPS"
    CAPTAIN = "CAPTAIN"
    SECURITY = "SECURITY"
    FINANCE = "FINANCE"


@dataclass(frozen=True)
class Authority:
    """
    Represents a legally accountable actor.
    """
    actor_id: str
    role: AuthorityRole

    def __post_init__(self):
        if not self.actor_id or not self.actor_id.strip():
            raise InvariantViolation("Authority must have an actor_id")
