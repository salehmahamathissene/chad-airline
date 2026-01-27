# kpi_report.py
import json
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

LOG_DIR = Path("./logs")
FLIGHTS = [f"flight_FL-{1000 + i}" for i in range(1, 11)]
TICKET_STATES = ["created", "issued", "paid", "checked-in", "boarded", "closed"]

def load_events(flight_id: str):
    """Load all events for a flight from its log file."""
    log_file = LOG_DIR / f"{flight_id}_events.log"
    events = []
    if log_file.exists():
        with log_file.open() as f:
            for line in f:
                try:
                    events.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return events

def calculate_kpi(flight_id: str):
    events = load_events(flight_id)
    tickets = defaultdict(lambda: {"states": set(), "closed": False})
    illegal_transitions = 0

    for event in events:
        ticket_id = event["ticket_id"]
        state_map = {
            "issued": "issued",
            "paid": "paid",
            "checked_in": "checked-in",
            "boarded": "boarded",
            "closed": "closed",
        }

        state = state_map.get(event["event_type"])
        if state:
            # Check illegal transitions
            current_states = tickets[ticket_id]["states"]
            if state == "paid" and "issued" not in current_states:
                illegal_transitions += 1
            if state == "checked-in" and "paid" not in current_states:
                illegal_transitions += 1
            if state == "boarded" and "checked-in" not in current_states:
                illegal_transitions += 1
            if state == "closed" and "boarded" not in current_states:
                illegal_transitions += 1

            current_states.add(state)
            if state == "closed":
                tickets[ticket_id]["closed"] = True

    total_tickets = len(tickets)
    issued = sum(1 for t in tickets.values() if "issued" in t["states"])
    paid = sum(1 for t in tickets.values() if "paid" in t["states"])
    checked_in = sum(1 for t in tickets.values() if "checked-in" in t["states"])
    boarded = sum(1 for t in tickets.values() if "boarded" in t["states"])
    closed = sum(1 for t in tickets.values() if t["closed"])

    load_factor = (boarded / total_tickets * 100) if total_tickets else 0
    completion_rate = (closed / total_tickets * 100) if total_tickets else 0
    no_show_rate = ((boarded - closed) / total_tickets * 100) if total_tickets else 0

    return {
        "tickets_issued": issued,
        "tickets_paid": paid,
        "checked_in": checked_in,
        "boarded": boarded,
        "closed": closed,
        "load_factor": load_factor,
        "completion_rate": completion_rate,
        "no_show_rate": no_show_rate,
        "illegal_transitions": illegal_transitions,
        "total_tickets": total_tickets
    }

def print_kpi_report():
    print("\n========== AIRLINE KPI REPORT ==========\n")
    total_illegal = 0
    total_tickets_overall = 0
    total_closed_overall = 0

    for flight_id in FLIGHTS:
        kpi = calculate_kpi(flight_id)
        total_illegal += kpi["illegal_transitions"]
        total_tickets_overall += kpi["total_tickets"]
        total_closed_overall += kpi["closed"]

        print(f"Flight {flight_id}")
        print(f"  Tickets issued     : {kpi['tickets_issued']}")
        print(f"  Tickets paid       : {kpi['tickets_paid']}")
        print(f"  Checked-in         : {kpi['checked_in']}")
        print(f"  Boarded            : {kpi['boarded']}")
        print(f"  Closed             : {kpi['closed']}")
        print(f"  Load factor        : {kpi['load_factor']:.1f}%")
        print(f"  Completion rate    : {kpi['completion_rate']:.1f}%")
        print(f"  No-show rate       : {kpi['no_show_rate']:.1f}%")
        print(f"  Illegal transitions: {kpi['illegal_transitions']}")
        print("-" * 40)

    if total_tickets_overall:
        labels = ["Closed Tickets", "Open Tickets"]
        sizes = [total_closed_overall, total_tickets_overall - total_closed_overall]
        plt.figure(figsize=(5,5))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=["green", "red"])
        plt.title("Ticket Completion Overview")
        plt.show()
    else:
        print("\nNo tickets issued yet — skipping transition integrity pie chart.")

if __name__ == "__main__":
    print_kpi_report()
