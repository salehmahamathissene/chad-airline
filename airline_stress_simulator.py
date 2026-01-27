# airline_stress_simulator.py
from datetime import timedelta
from threading import Thread, Lock
from domain.flight.model import Flight, FlightStatus
from domain.flight.events import FlightStatusChanged
from infrastructure.event_repository import EventRepository
from domain.common.time import Clock

# Lock for thread-safe flight operations
flight_lock = Lock()

def process_flight(flight: Flight, clock: Clock, events: EventRepository):
    """
    Processes a single flight for stress simulation.
    Handles delays, status changes, and event recording.
    """
    # Skip cancelled flights
    if flight.status == FlightStatus.CANCELLED:
        return

    try:
        # Example: simulate random delay
        delay = 15  # minutes; replace with your own logic

        with flight_lock:
            old_status = flight.status
            flight.departure_time += timedelta(minutes=delay)
            flight.status = FlightStatus.DELAYED

            # Record flight status change
            events.save(
                FlightStatusChanged(
                    occurred_at=clock.now(),
                    flight_id=flight.flight_id,
                    old_status=old_status,
                    new_status=flight.status
                )
            )

        # Additional operations could go here:
        # boarding, landing, ticket closure, etc.
        # All flight updates should stay within the lock

    except Exception as e:
        print(f"Error processing flight {flight.flight_id.value}: {e}")


def run_stress_simulation(flights, clock: Clock, events: EventRepository):
    """
    Run stress simulation for multiple flights concurrently.
    """
    threads = []

    for flight in flights:
        t = Thread(target=process_flight, args=(flight, clock, events))
        t.start()
        threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()


if __name__ == "__main__":
    # Example usage
    clock = Clock()
    events = EventRepository()

    # Example flights list; replace with real flight objects
    flights = [
        Flight(flight_id=f"FL-{i+1000}", departure_time=clock.now(), status=FlightStatus.SCHEDULED)
        for i in range(10)
    ]

    run_stress_simulation(flights, clock, events)
    print("Stress simulation complete. Total events:", len(events.all()))
