# domain/ticket/model.py
from datetime import datetime
from typing import List
from domain.common.recorded_event import RecordedEvent

class Ticket:
    def __init__(self, ticket_id: str, flight_id: str):
        self.ticket_id = ticket_id
        self.flight_id = flight_id
        self.state = "created"
        self.events: List[RecordedEvent] = []

    def record_event(self, event_type: str, **data):
        event = RecordedEvent(
            occurred_at=datetime.utcnow(),
            entity_id=self.ticket_id,
            event_type=event_type,
            data=data
        )
        self.events.append(event)

    # Ticket lifecycle methods
    def issue(self, price: float):
        self.state = "issued"
        self.record_event("issued", price=price)

    def pay(self, amount: float):
        self.state = "paid"
        self.record_event("paid", amount=amount)

    def check_in(self):
        self.state = "checked-in"
        self.record_event("checked_in")

    def board(self):
        self.state = "boarded"
        self.record_event("boarded")

    def close(self):
        self.state = "closed"
        self.record_event("closed")
