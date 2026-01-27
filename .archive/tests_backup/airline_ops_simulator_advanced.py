from datetime import datetime, timedelta, timezone
import random

from domain.common.time import Clock
from domain.common.identifiers import FlightId, TicketNumber
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
# Deterministic Clock
# ------------------------------------------------------
class FixedClock(Clock):
    def __init__(self, start_time: datetime):
        self._current = start_time

    def now(self) -> datetime:
        return self._current

    def advance(self, seconds: int):
        self._current += timedelta(seconds=seconds)


# ------------------------------------------------------
# Advanced Airline Operations Simulator
# ------------------------------------------------------
def simulate_airline_operations_advanced(
    num_flights: int = 3, tickets_per_flight: int = 5
):
    clock = FixedClock(datetime(2026, 1, 8, 6, 0, tzinfo=timezone.utc))
    audit = []

    flights = []

    # Create multiple flights with random schedules
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
        audit.append(f"Created flight {flight.flight_id.value} {departure.isoformat()} -> {arrival.isoformat()}")

    # Process tickets for each flight
    for flight in flights:
        for t in range(1, tickets_per_flight + 1):
            ticket_number = TicketNumber(f"{flight.flight_id.value}-T{t:03d}")
            passenger_id = f"PASS-{flight.flight_id.value}-{t:03d}"

            try:
                # Random flight cancellation (10%)
                if random.random() < 0.1:
                    flight.status = FlightStatus.CANCELLED
                    audit.append(f"Flight {flight.flight_id.value} CANCELLED")

                # Random delay (20%) — advance departure/arrival
                if random.random() < 0.2 and flight.status != FlightStatus.CANCELLED:
                    delay = random.randint(10, 60)  # minutes
                    flight.departure_time += timedelta(minutes=delay)
                    flight.arrival_time += timedelta(minutes=delay)
                    flight.status = FlightStatus.DELAYED
                    audit.append(f"Flight {flight.flight_id.value} DELAYED by {delay} mins")

                # Issue ticket
                issue_cmd = IssueTicket(ticket_number, flight.flight_id, passenger_id)
                ticket = IssueTicketService(clock).execute(issue_cmd, flight)
                audit.append(f"Issued ticket {ticket.ticket_number.value}")

                # Randomly skip payment for 10% tickets
                if random.random() < 0.1:
                    audit.append(f"Ticket {ticket.ticket_number.value} SKIPPED PAYMENT")
                    continue  # Skip remaining steps for this ticket

                # Pay ticket
                pay_cmd = PayTicket(ticket_number)
                ticket = PayTicketService(clock).execute(ticket, pay_cmd)
                audit.append(f"Paid ticket {ticket.ticket_number.value}")

                # Randomly skip check-in for 5% tickets
                if random.random() < 0.05:
                    audit.append(f"Ticket {ticket.ticket_number.value} SKIPPED CHECK-IN")
                    continue

                # Check-in
                check_in_cmd = CheckInTicket(ticket_number)
                ticket = CheckInService(clock).execute(ticket, check_in_cmd)
                audit.append(f"Checked-in ticket {ticket.ticket_number.value}")

                # Randomly skip boarding for 5% tickets
                if random.random() < 0.05:
                    audit.append(f"Ticket {ticket.ticket_number.value} SKIPPED BOARDING")
                    continue

                # Board
                board_cmd = BoardTicket(ticket_number)
                ticket = BoardService(clock).execute(ticket, board_cmd)
                audit.append(f"Boarded ticket {ticket.ticket_number.value}")

                # Close
                close_cmd = CloseTicket(ticket_number)
                ticket = CloseService(clock).execute(ticket, close_cmd)
                audit.append(f"Closed ticket {ticket.ticket_number.value}")

                # Advance clock slightly between tickets
                clock.advance(60)

            except InvariantViolation as e:
                audit.append(f"ERROR {ticket_number.value}: {e}")

    # Print full audit log
    print("=== ADVANCED AIRLINE OPERATIONS AUDIT ===")
    for entry in audit:
        print(entry)


if __name__ == "__main__":
    simulate_airline_operations_advanced(num_flights=3, tickets_per_flight=10)
