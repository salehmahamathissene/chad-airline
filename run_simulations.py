import threading
import random
import time
from datetime import datetime
from datetime import datetime, timezone
from domain.common.identifiers import FlightId, TicketNumber
from infrastructure.event_repository import EventRepository

from domain.ticket.events import (
    TicketIssued,
    TicketPaid,
    TicketCheckedIn,
    TicketBoarded,
    TicketClosed,
)

# -------------------------------
# CONFIG
# -------------------------------

FLIGHT_COUNT = 10
TICKETS_PER_FLIGHT = 5


# -------------------------------
# SIMULATION LOGIC (UNCHANGED)
# -------------------------------

def process_flight(flight_id: FlightId):
    repo = EventRepository()

    print(f"Created flight {flight_id.value} from CityX to CityY")

    for _ in range(TICKETS_PER_FLIGHT):
        ticket = TicketNumber.new()
        now = datetime.now(timezone.utc)

        repo.save(
            flight_id.value,
            TicketIssued(
                occurred_at=datetime.now(timezone.utc),
                ticket_number=ticket,
                flight_id=flight_id,
            ),
        )

        repo.save(
            flight_id.value,
            TicketPaid(
                occurred_at=datetime.now(timezone.utc),
                ticket_number=ticket,
            ),
        )

        repo.save(
            flight_id.value,
            TicketCheckedIn(
                occurred_at=datetime.now(timezone.utc),
                ticket_number=ticket,
            ),
        )

        repo.save(
            flight_id.value,
            TicketBoarded(
                occurred_at=datetime.now(timezone.utc),
                ticket_number=ticket,
            ),
        )

        repo.save(
            flight_id.value,
            TicketClosed(
                occurred_at=datetime.now(timezone.utc),
                ticket_number=ticket,
            ),
        )

        print(f"Processed ticket {ticket} for flight {flight_id.value}")
        time.sleep(random.uniform(0.1, 0.3))


# -------------------------------
# POST-SIMULATION ANALYSIS
# -------------------------------

def print_flight_summary(flight_id: FlightId):
    repo = EventRepository()
    events = repo.load_stream(flight_id.value)

    print("\n=== FLIGHT EVENT SUMMARY ===")
    print(f"Flight: {flight_id.value}")
    print(f"Total events: {len(events)}")

    issued = len([e for e in events if e.name == "TicketIssued"])
    boarded = len([e for e in events if e.name == "TicketBoarded"])
    closed = len([e for e in events if e.name == "TicketClosed"])

    print(f"Tickets issued : {issued}")
    print(f"Tickets boarded: {boarded}")
    print(f"Tickets closed : {closed}")
    print("============================\n")


# -------------------------------
# MAIN ENTRYPOINT
# -------------------------------

def main():
    threads = []
    flight_ids: list[FlightId] = []

    for i in range(1, FLIGHT_COUNT + 1):
        flight_id = FlightId(f"FL-{1000 + i}")
        flight_ids.append(flight_id)

        t = threading.Thread(
            target=process_flight,
            args=(flight_id,),
            daemon=True,
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n=== ALL SIMULATORS FINISHED ===\n")

    # 🔎 Read-only analysis (NO side effects)
    for flight_id in flight_ids:
        print_flight_summary(flight_id)


if __name__ == "__main__":
    main()
