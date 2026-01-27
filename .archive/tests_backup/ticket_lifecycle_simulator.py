from datetime import datetime, timezone
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

# ------------------------------------------------------
# Deterministic Clock Implementation
# ------------------------------------------------------
class FixedClock(Clock):
    def __init__(self, start_time: datetime):
        self._current = start_time

    def now(self) -> datetime:
        return self._current

    def advance(self, delta_seconds: int):
        self._current = self._current + timedelta(seconds=delta_seconds)

# ------------------------------------------------------
# Simulation
# ------------------------------------------------------
def simulate_ticket_lifecycle():
    # Initialize clock
    clock = FixedClock(datetime(2026, 1, 8, 12, 0, tzinfo=timezone.utc))

    # Create a flight
    flight = Flight(
        flight_id=FlightId("FL-1001"),
        origin="NDJ",
        destination="FNA",
        departure_time=datetime(2026, 1, 8, 14, 0, tzinfo=timezone.utc),
        arrival_time=datetime(2026, 1, 8, 16, 0, tzinfo=timezone.utc),
        aircraft_id="AC-737"
    )

    # Audit log
    audit = []

    # Issue ticket
    issue_cmd = IssueTicket(
        ticket_number=TicketNumber("TCK-0001"),
        flight_id=flight.flight_id,
        passenger_id="PASS-1234"
    )
    issue_service = IssueTicketService(clock)
    ticket = issue_service.execute(issue_cmd, flight)
    audit.append(f"Issued: {ticket.ticket_number.value} at {ticket.issued_at.isoformat()}")

    # Pay ticket
    pay_cmd = PayTicket(ticket_number=ticket.ticket_number)
    pay_service = PayTicketService(clock)
    ticket = pay_service.execute(ticket, pay_cmd)
    audit.append(f"Paid: {ticket.ticket_number.value} at {ticket.last_state_change_at.isoformat()}")

    # Check-in
    check_in_cmd = CheckInTicket(ticket_number=ticket.ticket_number)
    check_in_service = CheckInService(clock)
    ticket = check_in_service.execute(ticket, check_in_cmd)
    audit.append(f"Checked-in: {ticket.ticket_number.value} at {ticket.last_state_change_at.isoformat()}")

    # Board
    board_cmd = BoardTicket(ticket_number=ticket.ticket_number)
    board_service = BoardService(clock)
    ticket = board_service.execute(ticket, board_cmd)
    audit.append(f"Boarded: {ticket.ticket_number.value} at {ticket.last_state_change_at.isoformat()}")

    # Close
    close_cmd = CloseTicket(ticket_number=ticket.ticket_number)
    close_service = CloseService(clock)
    ticket = close_service.execute(ticket, close_cmd)
    audit.append(f"Closed: {ticket.ticket_number.value} at {ticket.last_state_change_at.isoformat()}")

    # Print audit log
    print("=== TICKET LIFECYCLE AUDIT ===")
    for entry in audit:
        print(entry)

# Run simulation if executed as main
if __name__ == "__main__":
    simulate_ticket_lifecycle()
