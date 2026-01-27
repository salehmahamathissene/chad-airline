import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import csv
from domain.ticket.model import Ticket
from infrastructure.event_repository import save_event  # if you use it

# -----------------------
# Simulation Parameters
# -----------------------
NUM_FLIGHTS = 10
SEATS_PER_FLIGHT = 100
TICKETS_PER_FLIGHT = 80  # simulate 80 passengers per flight
TICKET_PRICE_RANGE = (100, 500)  # min and max ticket price
NO_SHOW_PROB = 0.05  # probability of no-show
CANCEL_PROB = 0.03   # probability of cancellation

flights_data = {}

# -----------------------
# Simulate Ticket Lifecycle
# -----------------------
def simulate_ticket_lifecycle(flight_id):
    tickets = []
    for i in range(TICKETS_PER_FLIGHT):
        ticket = Ticket(flight_id=flight_id, passenger_id=i+1)
        price = random.uniform(*TICKET_PRICE_RANGE)
        ticket.issue(price=price)

        # Pay ticket
        ticket.pay()

        # Randomly cancel
        if random.random() < CANCEL_PROB:
            ticket.cancel()
        else:
            # Check-in
            ticket.check_in()

            # Randomly no-show
            if random.random() < NO_SHOW_PROB:
                ticket.no_show()
            else:
                # Board and close
                ticket.board()
                ticket.close()

        tickets.append(ticket)
    flights_data[flight_id] = tickets


# -----------------------
# Compute Statistics
# -----------------------
def compute_kpis():
    report = {}
    for flight_id, tickets in flights_data.items():
        total = len(tickets)
        issued = sum(1 for t in tickets if t.state >= "issued")
        paid = sum(1 for t in tickets if t.state >= "paid")
        checked_in = sum(1 for t in tickets if t.state >= "checked_in")
        boarded = sum(1 for t in tickets if t.state >= "boarded")
        closed = sum(1 for t in tickets if t.state == "closed")
        no_show = sum(1 for t in tickets if getattr(t, "no_show_flag", False))
        revenue = sum(t.price for t in tickets if t.state >= "paid")

        load_factor = (boarded / SEATS_PER_FLIGHT) * 100
        completion_rate = (closed / total) * 100
        no_show_rate = (no_show / total) * 100

        report[flight_id] = {
            "Tickets issued": issued,
            "Tickets paid": paid,
            "Checked-in": checked_in,
            "Boarded": boarded,
            "Closed": closed,
            "Revenue": revenue,
            "Load factor": load_factor,
            "Completion rate": completion_rate,
            "No-show rate": no_show_rate,
        }
    return report


# -----------------------
# Generate Graphs
# -----------------------
def plot_kpis(report):
    flights = list(report.keys())
    load_factors = [report[f]["Load factor"] for f in flights]
    revenues = [report[f]["Revenue"] for f in flights]

    plt.figure(figsize=(10,5))
    plt.bar(flights, load_factors, color='green')
    plt.ylabel("Load Factor (%)")
    plt.title("Flight Load Factor")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("load_factor_per_flight.png")
    plt.close()

    plt.figure(figsize=(10,5))
    plt.bar(flights, revenues, color='blue')
    plt.ylabel("Revenue ($)")
    plt.title("Flight Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("revenue_per_flight.png")
    plt.close()


# -----------------------
# Save CSV Report
# -----------------------
def save_csv_report(report):
    with open("kpi_report.csv", "w", newline="") as csvfile:
        fieldnames = ["Flight", "Tickets issued", "Tickets paid", "Checked-in",
                      "Boarded", "Closed", "Revenue", "Load factor", 
                      "Completion rate", "No-show rate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for flight, data in report.items():
            row = {"Flight": flight}
            row.update(data)
            writer.writerow(row)


# -----------------------
# Run Simulation
# -----------------------
def run_simulation():
    for flight_id in [f"FL-{1000+i}" for i in range(1, NUM_FLIGHTS+1)]:
        simulate_ticket_lifecycle(flight_id)

    report = compute_kpis()
    save_csv_report(report)
    plot_kpis(report)

    print("✅ Ticket lifecycle simulation completed.")
    for flight, data in report.items():
        print(f"\nFlight {flight}")
        for key, value in data.items():
            if isinstance(value, float):
                print(f"  {key:<15}: {value:.2f}")
            else:
                print(f"  {key:<15}: {value}")


if __name__ == "__main__":
    run_simulation()
