from enum import Enum

class RegulatoryAction(Enum):
    ISSUE_TICKET = "ISSUE_TICKET"
    PAY_TICKET = "PAY_TICKET"
    CHECK_IN = "CHECK_IN"
    BOARD = "BOARD"
    CLOSE_FLIGHT = "CLOSE_FLIGHT"
    CANCEL = "CANCEL"
