from enum import Enum


class OverrideReason(Enum):
    CAPTAIN_DECISION = "captain_decision"
    GATE_AGENT_DECISION = "gate_agent_decision"
    OPERATIONS_CONTROL = "operations_control"
    SAFETY_EXCEPTION = "safety_exception"
    SYSTEM_FAILURE = "system_failure"
