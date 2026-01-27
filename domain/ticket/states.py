# domain/ticket/states.py

from enum import Enum

class TicketState(Enum):
    ISSUED = "issued"
    PAID = "paid"
    CHECKED_IN = "checked_in"
    BOARDED = "boarded"
    CLOSED = "closed"
