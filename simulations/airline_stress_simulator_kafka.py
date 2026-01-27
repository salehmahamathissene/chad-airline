# tests/airline_stress_simulator_kafka.py
import threading
import random
from datetime import datetime, timedelta, timezone
from domain.common.time import Clock
from domain.common.identifiers import FlightId, TicketNumber
from domain.flight.model import Flight, FlightStatus
from application.commands.issue_ticket import IssueTicket
from application.services.issue_ticket_service import IssueTicketService
from infrastructure.kafka_event_store import KafkaEventStore
from domain.common.events import TicketIssued, FlightStatusChanged

def flight_worker(flight: Flight, tickets_per_flight: int, clock: Clock, event_store: KafkaEventStore):
    for t in range(1, tickets_per_flight + 1):
        ticket_number = TicketNumber(f"{flight.flight_id.value}-T{t:04d}")
        passenger_id = f"PASS-{flight.flight_id.value}-{t:04d}"

        # Random flight status update
        if random.random() < 0.05:
            flight.status = FlightStatus.CANCELLED
            event_store.publish("flight_events", FlightStatusChanged(clock.now(), flight.flight_id, flight.status.value))

        issue_cmd = IssueTicket(ticket_number, flight.flight_id, passenger_id)
        ticket = IssueTicketService(clock).execute(issue_cmd, flight)
        event_store.publish("ticket_events", TicketIssued(clock.now(), ticket_number, flight.flight_id, passenger_id))

def simulate(num_flights=10, tickets_per_flight=500):
    base_clock = ClockStub(datetime(2026, 1, 8, 6, 0, tzinfo=timezone.utc))
    event_store = KafkaEventStore()

    flights = [
        Flight(
            flight_id=FlightId(f"FL-{1000+i}"),
            origin="NDJ",
            destination="FNA",
            departure_time=datetime(2026,1,8,8+i,0,tzinfo=timezone.utc),
            arrival_time=datetime(2026,1,8,10+i,0,tzinfo=timezone.utc),
            aircraft_id=f"AC-7{i}7"
        ) for i in range(num_flights)
    ]

    threads = []
    for flight in flights:
        t = threading.Thread(target=flight_worker, args=(flight, tickets_per_flight, base_clock, event_store))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("✅ Professional multi-threaded simulation complete. Events published to Kafka.")
