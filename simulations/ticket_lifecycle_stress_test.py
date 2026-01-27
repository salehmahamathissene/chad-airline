from datetime import datetime, timedelta, timezone
from domain.common.time import Clock
from domain.common.identifiers import FlightId, TicketNumber
from domain.flight.model import Flight
from domain.flight.rules import assert_flight_bookable
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
# Stress Test
# ------------------------------------------------------
def multi_ticket_stress_test(num_tickets: int):
    clock = FixedClock(datetime(2026, 1, 8, 12, 0, tzinfo=timezone.utc))

    # Create a single flight
    flight = Flight(
        flight_id=FlightId("FL-2001"),
        origin="NDJ",
        destination="FNA",
        departure_time=datetime(2026, 1, 8, 14, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2026, 1, 8, 16, 0, tzinfo=timezone.utc),
        aircraft_id="AC-737"
    )

    # Audit log
    audit = []

    for i in range(1, num_tickets + 1):
        ticket_number = TicketNumber(f"TCK-{i:04d}")
        passenger_id = f"PASS-{i:04d}"

        try:
            # Issue
            issue_cmd = IssueTicket(ticket_number, flight.flight_id, passenger_id)
            ticket = IssueTicketService(clock).execute(issue_cmd, flight)
            audit.append(f"Issued {ticket.ticket_number.value}")

            # Pay
            pay_cmd = PayTicket(ticket_number)
            ticket = PayTicketService(clock).execute(ticket, pay_cmd)
            audit.append(f"Paid {ticket.ticket_number.value}")

            # Check-in
            check_in_cmd = CheckInTicket(ticket_number)
            ticket = CheckInService(clock).execute(ticket, check_in_cmd)
            audit.append(f"Checked-in {ticket.ticket_number.value}")

            # Board
            board_cmd = BoardTicket(ticket_number)
            ticket = BoardService(clock).execute(ticket, board_cmd)
            audit.append(f"Boarded {ticket.ticket_number.value}")

            # Close
            close_cmd = CloseTicket(ticket_number)
            ticket = CloseService(clock).execute(ticket, close_cmd)
            audit.append(f"Closed {ticket.ticket_number.value}")

            # Advance clock slightly between tickets
            clock.advance(60)

        except InvariantViolation as e:
            audit.append(f"ERROR {ticket_number.value}: {e}")

    # Print final audit
    print("=== MULTI-TICKET STRESS TEST AUDIT ===")
    for entry in audit:
        print(entry)


if __name__ == "__main__":
    # Stress test 10 tickets (adjust as needed)
    multi_ticket_stress_test(10)
