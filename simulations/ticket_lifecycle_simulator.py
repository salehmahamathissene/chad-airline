# simulations/ticket_lifecycle_simulator.py
import random
from domain.ticket.model import Ticket
from infrastructure.event_repository import EventRepository

TICKETS_PER_FLIGHT = 5
FLIGHTS = [f"flight_FL-{1000 + i}" for i in range(1, 11)]

def simulate_ticket_lifecycle(flight_id: str):
    tickets = []
    for i in range(1, TICKETS_PER_FLIGHT + 1):
        ticket_id = f"{flight_id}_T{i}"
        ticket = Ticket(ticket_id=ticket_id, flight_id=flight_id)
        ticket.issue(price=random.uniform(100, 500))
        ticket.pay(amount=random.uniform(100, 500))
        ticket.check_in()
        ticket.board()
        ticket.close()
        tickets.append(ticket)

        # Save events to logs
        for event in ticket.events:
            repo = EventRepository()
            repo.save_event(flight_id, event)

    return tickets

def run_simulation():
    for flight_id in FLIGHTS:
        simulate_ticket_lifecycle(flight_id)

if __name__ == "__main__":
    run_simulation()
    print("✅ Ticket lifecycle simulation completed.")
