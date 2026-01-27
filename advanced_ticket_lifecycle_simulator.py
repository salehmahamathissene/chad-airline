import random
import csv
from dataclasses import dataclass
from datetime import datetime
import hashlib
from statistics import mean, stdev

# ----------------------------
# Event recording (immutable)
# ----------------------------
@dataclass(frozen=True)
class RecordedEvent:
    occurred_at: datetime
    name: str
    details: dict

    def event_id(self) -> str:
        payload = f"{self.name}:{self.occurred_at.isoformat()}:{self.details}"
        return hashlib.sha256(payload.encode()).hexdigest()

# ----------------------------
# Ticket model
# ----------------------------
class Ticket:
    STATES = ["issued", "paid", "checked_in", "boarded", "closed"]

    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        self.state = None
        self.price = 0
        self.events = []

    def record_event(self, name, **details):
        event = RecordedEvent(datetime.now(), name, details)
        self.events.append(event)
        self.state = name

    def issue(self, price):
        self.price = price
        self.record_event("issued", price=price)

    def pay(self):
        self.record_event("paid")

    def check_in(self):
        self.record_event("checked_in")

    def board(self, no_show_prob=0.05):
        if random.random() > no_show_prob:
            self.record_event("boarded")
            return True
        else:
            return False

    def close(self):
        self.record_event("closed")

# ----------------------------
# Flight simulation
# ----------------------------
class Flight:
    def __init__(self, flight_id, capacity=5):
        self.flight_id = flight_id
        self.capacity = capacity
        self.tickets = []

    def sell_ticket(self, price):
        ticket = Ticket(f"{self.flight_id}_T{len(self.tickets)+1}")
        ticket.issue(price)
        ticket.pay()
        ticket.check_in()
        self.tickets.append(ticket)

    def simulate_boarding(self, no_show_prob=0.05):
        boarded = 0
        for ticket in self.tickets:
            if ticket.board(no_show_prob):
                boarded += 1
            ticket.close()
        return boarded

# ----------------------------
# Monte Carlo simulation
# ----------------------------
def simulate_flight(flight_id, capacity=5, base_price=200, no_show_prob=0.05, simulations=100):
    revenues = []
    load_factors = []

    for _ in range(simulations):
        flight = Flight(flight_id, capacity)
        # Sell tickets
        for _ in range(capacity):
            price = random.uniform(base_price * 0.8, base_price * 1.2)  # dynamic pricing ±20%
            flight.sell_ticket(price)
        boarded = flight.simulate_boarding(no_show_prob)
        revenue = sum(ticket.price for ticket in flight.tickets)
        load_factor = (boarded / capacity) * 100
        revenues.append(revenue)
        load_factors.append(load_factor)

    return {
        "flight": flight_id,
        "mean_revenue": mean(revenues),
        "revenue_std": stdev(revenues),
        "mean_load_factor": mean(load_factors),
        "load_factor_std": stdev(load_factors)
    }

# ----------------------------
# Run simulation for multiple flights
# ----------------------------
def run_simulation():
    flight_ids = [f"FL-100{i}" for i in range(1, 6)]
    results = []

    print("🚀 Running Monte Carlo Ticket Lifecycle Simulation...\n")
    for flight_id in flight_ids:
        result = simulate_flight(flight_id, capacity=5, base_price=200, no_show_prob=0.05, simulations=100)
        results.append(result)

        print(f"Flight {flight_id} Summary:")
        print(f"  Mean Revenue       : ${result['mean_revenue']:.2f}")
        print(f"  Revenue Std Dev    : ${result['revenue_std']:.2f}")
        print(f"  Mean Load Factor   : {result['mean_load_factor']:.2f}%")
        print(f"  Load Factor StdDev : {result['load_factor_std']:.2f}%")
        print("-" * 50)

    save_simulation_results(results)
    print("\n✅ Simulation Complete! Results saved to 'simulation_results.csv'.")

# ----------------------------
# Export results
# ----------------------------
def save_simulation_results(flight_results, filename="simulation_results.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=flight_results[0].keys())
        writer.writeheader()
        for row in flight_results:
            writer.writerow(row)

# ----------------------------
# Entry point
# ----------------------------
if __name__ == "__main__":
    run_simulation()
