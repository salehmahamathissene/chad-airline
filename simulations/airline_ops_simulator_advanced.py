# tests/airline_ops_simulator_advanced.py
from datetime import timedelta
from threading import Thread, Lock
from domain.flight.model import Flight, FlightStatus
from domain.flight.events import FlightStatusChanged
from domain.ticket.model import Ticket
from domain.ticket.events import TicketIssued, TicketPaid
from infrastructure.event_repository import EventRepository
from domain.common.time import Clock

# Thread-safe lock for flight updates
flight_lock = Lock()

def process_flight(flight: Flight, tickets_per_flight: int, clock: Clock, events: EventRepository):
    """
    Processes a single flight in advanced simulation.
    Includes ticket issuance, payment, and flight status changes.
    """
    # Skip cancelled flights
    if flight.status == FlightStatus.CANCELLED:
        return

    try:
        # Change flight status safely
        with flight_lock:
            old_status = flight.status
            flight.status = FlightStatus.SCHEDULED
            events.save(
                FlightStatusChanged(
                    occurred_at=clock.now(),
                    flight_id=flight.flight_id,
                    old_status=old_status,
                    new_status=flight.status
                )
            )

        # Issue and pay tickets
        for i in range(1, tickets_per_flight + 1):
            ticket_id = f"{flight.flight_id}-T{i:04d}"
            passenger_id = f"PASS-{flight.flight_id}-{i:04d}"

            # Issue ticket
            ticket = Ticket(ticket_id=ticket_id, flight_id=flight.flight_id, passenger_id=passenger_id)
            events.save(TicketIssued(occurred_at=clock.now(), ticket_id=ticket.ticket_id, flight_id=flight.flight_id, passenger_id=passenger_id))

            # Pay ticket
            events.save(TicketPaid(occurred_at=clock.now(), ticket_id=ticket.ticket_id))

    except Exception as e:
        print(f"Error processing flight {flight.flight_id.value}: {e}")


def run_advanced_simulation(flights, tickets_per_flight: int = 500):
    """
    Run the full advanced airline operations simulation.
    """
    clock = Clock()
    events = EventRepository()
    threads = []

    for flight in flights:
        t = Thread(target=process_flight, args=(flight, tickets_per_flight, clock, events))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"Advanced simulation finished. Total events: {len(events.all())}")


if __name__ == "__main__":
    # Example flights for the simulation
    clock = Clock()
    flights = [
        Flight(flight_id=f"FL-{i+1000}", departure_time=clock.now(), status=FlightStatus.SCHEDULED)
        for i in range(10)
    ]

    run_advanced_simulation(flights)
