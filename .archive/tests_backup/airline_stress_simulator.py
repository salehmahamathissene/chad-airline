from datetime import datetime, timedelta, timezone
import random
import threading
from typing import List

from domain.common.time import Clock
from domain.common.identifiers import FlightId, TicketNumber
from domain.common.events import (
    Event, TicketIssued, TicketPaid, TicketCheckedIn,
    TicketBoarded, TicketClosed, FlightStatusChanged
)
from infrastructure.event_repository import EventRepository
from domain.flight.model import Flight, FlightStatus
from application.commands.issue_ticket import IssueTicket
from application.services.issue_ticket_service import IssueTicketService
from application.commands.pay_ticket import PayTicket
from application.services.pay_ticket_service import PayTicketService
from application.commands.check_in_ticket import CheckInTicket
from application.services.check_in_service import CheckInService
from application.commands.board_ticket import BoardTicket
from application.services.board_service import BoardService
from application.commands.close_ticket import CloseTicket
from application.services.close_service import CloseService
from domain.common.errors import InvariantViolation


# ------------------------------------------------------
# Thread-safe Event Repository
# ------------------------------------------------------
class ThreadSafeEventRepository(EventRepository):
    def __init__(self):
        super().__init__()
        self._lock = threading.Lock()

    def save(self, event: Event):
        with self._lock:
            super().save(event)

    def all_events(self) -> List[Event]:
        with self._lock:
            return super().all_events()


# ------------------------------------------------------
# Deterministic per-thread clock
# ------------------------------------------------------
class ThreadClock(Clock):
    def __init__(self, start_time: datetime):
        self._current = start_time

    def now(self) -> datetime:
        return self._current

    def advance(self, seconds: int):
        self._current += timedelta(seconds=seconds)


# ------------------------------------------------------
# Flight processor for multi-threaded simulation
# ------------------------------------------------------
def process_flight(flight: Flight, tickets_per_flight: int, clock: Clock, events: ThreadSafeEventRepository):
    for t in range(1, tickets_per_flight + 1):
        ticket_number = TicketNumber(f"{flight.flight_id.value}-T{t:04d}")
        passenger_id = f"PASS-{flight.flight_id.value}-{t:04d}"

        try:
            # Random cancellation / delay
            if random.random() < 0.05:
                flight.status = FlightStatus.CANCELLED
                events.save(FlightStatusChanged(clock.now(), flight.flight_id, flight.status.value))
            elif random.random() < 0.15:
                delay = random.randint(10, 120)
                flight.departure_time += timedelta(minutes=delay)
                flight.arrival_time += timedelta(minutes=delay)
                flight.status = FlightStatus.DELAYED
                events.save(FlightStatusChanged(clock.now(), flight.flight_id, flight.status.value))

            # Issue ticket
            issue_cmd = IssueTicket(ticket_number, flight.flight_id, passenger_id)
            ticket = IssueTicketService(clock).execute(issue_cmd, flight)
            events.save(TicketIssued(clock.now(), ticket_number, flight.flight_id, passenger_id))

            # Random skip payment 5%
            if random.random() < 0.05:
                continue

            # Pay ticket
            pay_cmd = PayTicket(ticket_number)
            ticket = PayTicketService(clock).execute(ticket, pay_cmd)
            events.save(TicketPaid(clock.now(), ticket_number))

            # Random skip check-in 2%
            if random.random() < 0.02:
                continue

            # Check-in
            check_in_cmd = CheckInTicket(ticket_number)
            ticket = CheckInService(clock).execute(ticket, check_in_cmd)
            events.save(TicketCheckedIn(clock.now(), ticket_number))

            # Random skip boarding 2%
            if random.random() < 0.02:
                continue

            # Board
            board_cmd = BoardTicket(ticket_number)
            ticket = BoardService(clock).execute(ticket, board_cmd)
            events.save(TicketBoarded(clock.now(), ticket_number))

            # Close
            close_cmd = CloseTicket(ticket_number)
            ticket = CloseService(clock).execute(ticket, close_cmd)
            events.save(TicketClosed(clock.now(), ticket_number))

            # Advance clock slightly
            clock.advance(30)

        except InvariantViolation as e:
            print(f"ERROR {ticket_number.value}: {e}")


# ------------------------------------------------------
# Main multi-threaded airline simulation
# ------------------------------------------------------
def simulate_stress_airline(num_flights: int = 10, tickets_per_flight: int = 500):
    base_clock = ThreadClock(datetime(2026, 1, 8, 6, 0, tzinfo=timezone.utc))
    events = ThreadSafeEventRepository()

    flights = []

    # Create flights
    for i in range(1, num_flights + 1):
        departure = datetime(2026, 1, 8, 8 + i, 0, tzinfo=timezone.utc)
        arrival = departure + timedelta(hours=2)
        flight = Flight(
            flight_id=FlightId(f"FL-{1000 + i}"),
            origin="NDJ",
            destination="FNA",
            departure_time=departure,
            arrival_time=arrival,
            aircraft_id=f"AC-7{i}7"
        )
        flights.append(flight)

    threads = []
    for flight in flights:
        # Each flight runs in its own thread with independent clock
        flight_clock = ThreadClock(base_clock.now())
        t = threading.Thread(target=process_flight, args=(flight, tickets_per_flight, flight_clock, events))
        t.start()
        threads.append(t)

    # Wait for all flights to complete
    for t in threads:
        t.join()

    # Replay full audit
    print(f"=== STRESS AIRLINE SIMULATION: {num_flights} flights, {tickets_per_flight} tickets each ===")
    all_events = events.all_events()
    print(f"Total events generated: {len(all_events)}")
    # Optionally, print first 50 events for sanity
    for evt in all_events[:50]:
        print(evt)


if __name__ == "__main__":
    simulate_stress_airline(num_flights=10, tickets_per_flight=500)
