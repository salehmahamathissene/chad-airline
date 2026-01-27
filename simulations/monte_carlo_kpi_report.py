# simulations/monte_carlo_kpi_report.py

import random
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# --- Config ---
FLIGHTS = [f"FL-{1000+i+1}" for i in range(10)]
CLASSES = {
    "economy": {"capacity": 150, "price_range": (100, 200)},
    "business": {"capacity": 50, "price_range": (300, 500)},
    "first": {"capacity": 20, "price_range": (500, 1000)}
}
MONTE_CARLO_RUNS = 500
LOG_DIR = "logs_monte_carlo"
os.makedirs(LOG_DIR, exist_ok=True)

# --- Run simulation for one flight/class ---
def simulate_class(flight_id, cls, info):
    revenues = []
    load_factors = []
    denied_boardings = []

    for _ in range(MONTE_CARLO_RUNS):
        issued_tickets = info["capacity"] + random.randint(-5, 10)
        prices = [random.uniform(*info["price_range"]) for _ in range(issued_tickets)]
        boarded = min(issued_tickets, info["capacity"])
        denied = max(0, issued_tickets - info["capacity"])
        revenue = sum(prices[:boarded])

        revenues.append(revenue)
        load_factors.append(boarded / info["capacity"] * 100)
        denied_boardings.append(denied)

    # Log for reproducibility
    with open(f"{LOG_DIR}/{flight_id}_{cls}_simulation.log", "w") as f:
        for r, l, d in zip(revenues, load_factors, denied_boardings):
            f.write(f"{r:.2f},{l:.2f},{d}\n")

    return {
        "mean_revenue": np.mean(revenues),
        "revenue_std": np.std(revenues),
        "mean_load": np.mean(load_factors),
        "load_std": np.std(load_factors),
        "avg_denied": np.mean(denied_boardings)
    }

# --- Run simulation for all flights ---
flight_stats = {}
print("🚀 Running Advanced Monte Carlo Ticket Lifecycle KPI Simulation...\n")
for flight_id in FLIGHTS:
    flight_stats[flight_id] = {}
    for cls, info in CLASSES.items():
        flight_stats[flight_id][cls] = simulate_class(flight_id, cls, info)

# --- Generate KPI Report ---
print("========== AIRLINE MONTE CARLO KPI REPORT ==========\n")
for flight_id, stats in flight_stats.items():
    print(f"Flight {flight_id}:")
    for cls, data in stats.items():
        print(
            f"  Class {cls:8}: "
            f"Mean Revenue=${data['mean_revenue']:8.2f}, "
            f"Revenue StdDev=${data['revenue_std']:7.2f}, "
            f"Mean Load={data['mean_load']:6.2f}%, "
            f"Load StdDev={data['load_std']:5.2f}%, "
            f"Denied Avg={data['avg_denied']:4.2f}"
        )
    print("-" * 60)

# --- Generate Graphs ---
for flight_id, stats in flight_stats.items():
    fig, ax = plt.subplots()
    classes = list(stats.keys())
    means = [stats[cls]["mean_revenue"] for cls in classes]
    stds = [stats[cls]["revenue_std"] for cls in classes]

    ax.bar(classes, means, yerr=stds, capsize=5, color=["skyblue", "orange", "green"])
    ax.set_title(f"{flight_id} Revenue per Class (Monte Carlo)")
    ax.set_ylabel("Revenue ($)")
    plt.tight_layout()
    plt.savefig(f"{flight_id}_monte_carlo_revenue.png")
    plt.close(fig)

print("\n✅ Monte Carlo KPI Simulation Complete! Logs and charts generated.")
