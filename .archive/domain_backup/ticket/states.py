from domain.common.state_machine import StateMachine

TICKET_STATES = StateMachine(
    transitions={
        "ISSUED": {"PAID"},
        "PAID": {"CHECKED_IN"},
        "CHECKED_IN": {"BOARDED"},
        "BOARDED": {"CLOSED"},
        "CLOSED": set(),
    }
)
