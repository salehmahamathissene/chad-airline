from typing import Dict, Set

from domain.common.errors import InvalidStateTransition


class StateMachine:
    """
    Explicit state machine with allowed transitions.
    Prevents illegal or implicit state changes.
    """

    def __init__(self, transitions: Dict[str, Set[str]]):
        self._transitions = transitions

    def can_transition(self, from_state: str, to_state: str) -> bool:
        return to_state in self._transitions.get(from_state, set())

    def assert_transition(self, from_state: str, to_state: str) -> None:
        if not self.can_transition(from_state, to_state):
            raise InvalidStateTransition(
                f"Illegal transition: {from_state} → {to_state}"
            )
