# simulations/advanced_ticket_lifecycle_simulator.py

import random
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- Configurable Simulation Parameters ---
FLIGHTS = [f"FL-{1000+i+1}" for i in range(10)]
CLASSES = {
    "economy": {"capacity": 150, "price_range": (100, 200)},
    "business": {"capacity": 50, "price_range": (300, 500)},
    "first": {"capacity": 20, "price_range": (500, 1000)}
}
MONTE_CARLO_RUNS = 500

# --- Storage for results ---
flight_stats = {}

# --- Ticket Simulation per Flight/Class ---
def simulate_flight(flight_id):
    stats = {}
    for cls, info in CLASSES.items():
        revenues = []
        load_factors = []
        denied_boardings = []

        for _ in range(MONTE_CARLO_RUNS):
            issued_tickets = info["capacity"] + random.randint(-5, 10)  # oversell allowed
            prices = [random.uniform(*info["price_range"]) for _ in range(issued_tickets)]
            boarded = min(issued_tickets, info["capacity"])
            denied = max(0, issued_tickets - info["capacity"])
            revenue = sum(prices[:boarded])

            revenues.append(revenue)
            load_factors.append(boarded / info["capacity"] * 100)
            denied_boardings.append(denied)

        stats[cls] = {
            "mean_revenue": np.mean(revenues),
            "revenue_std": np.std(revenues),
            "mean_load": np.mean(load_factors),
            "load_std": np.std(load_factors),
            "avg_denied": np.mean(denied_boardings)
        }
    return stats

# --- Run Simulation for All Flights ---
print("🚀 Running Monte Carlo Ticket Lifecycle Simulation...\n")
for flight_id in FLIGHTS:
    flight_stats[flight_id] = simulate_flight(flight_id)

# --- Display Results ---
for flight_id, stats in flight_stats.items():
    print(f"Flight {flight_id} Summary (Monte Carlo {MONTE_CARLO_RUNS} runs):")
    for cls, data in stats.items():
        print(
            f"  Class {cls}: Mean Revenue=${data['mean_revenue']:.2f}, "
            f"Revenue StdDev=${data['revenue_std']:.2f}, "
            f"Mean Load Factor={data['mean_load']:.2f}%, "
            f"Denied Boarding Avg={data['avg_denied']:.2f}"
        )
    print("-" * 50)

# --- Generate Graphs ---
for flight_id, stats in flight_stats.items():
    fig, ax = plt.subplots()
    classes = list(stats.keys())
    means = [stats[cls]["mean_revenue"] for cls in classes]
    stds = [stats[cls]["revenue_std"] for cls in classes]

    ax.bar(classes, means, yerr=stds, capsize=5, color=["skyblue", "orange", "green"])
    ax.set_title(f"Flight {flight_id} Revenue per Class")
    ax.set_ylabel("Revenue ($)")
    plt.tight_layout()
    plt.savefig(f"ticket_revenue_{flight_id}.png")
    plt.close(fig)

print("\n✅ Simulation Complete! Check generated histograms for insights.")
