# simulations/monte_carlo_kpi_dashboard.py

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Config ---
FLIGHTS = [f"FL-{1000+i+1}" for i in range(10)]
CLASSES = {
    "economy": {"capacity": 150, "price_range": (100, 200)},
    "business": {"capacity": 50, "price_range": (300, 500)},
    "first": {"capacity": 20, "price_range": (500, 1000)}
}
MONTE_CARLO_RUNS = 500
LOG_DIR = "logs_monte_carlo_dashboard"
os.makedirs(LOG_DIR, exist_ok=True)

# --- Monte Carlo simulation per flight/class ---
def simulate_class(flight_id, cls, info):
    revenues, load_factors, denied_boardings = [], [], []

    for _ in range(MONTE_CARLO_RUNS):
        issued = info["capacity"] + random.randint(-5, 10)
        prices = [random.uniform(*info["price_range"]) for _ in range(issued)]
        boarded = min(issued, info["capacity"])
        denied = max(0, issued - info["capacity"])
        revenue = sum(prices[:boarded])

        revenues.append(revenue)
        load_factors.append(boarded / info["capacity"] * 100)
        denied_boardings.append(denied)

    # Save logs
    df = pd.DataFrame({
        "revenue": revenues,
        "load": load_factors,
        "denied": denied_boardings
    })
    df.to_csv(f"{LOG_DIR}/{flight_id}_{cls}_simulation.csv", index=False)

    return df

# --- Run simulation for all flights ---
all_data = {}
for flight_id in FLIGHTS:
    all_data[flight_id] = {}
    for cls, info in CLASSES.items():
        all_data[flight_id][cls] = simulate_class(flight_id, cls, info)

# --- Generate summary KPI table ---
summary_rows = []
for flight_id, classes_data in all_data.items():
    for cls, df in classes_data.items():
        summary_rows.append({
            "flight": flight_id,
            "class": cls,
            "mean_revenue": df["revenue"].mean(),
            "revenue_std": df["revenue"].std(),
            "mean_load": df["load"].mean(),
            "load_std": df["load"].std(),
            "avg_denied": df["denied"].mean()
        })
summary_df = pd.DataFrame(summary_rows)
print("\n========== AIRLINE MONTE CARLO KPI DASHBOARD ==========\n")
print(summary_df.to_string(index=False))

# --- Visualization ---
sns.set(style="whitegrid")

# Revenue distributions
for flight_id, classes_data in all_data.items():
    plt.figure(figsize=(10,6))
    for cls, df in classes_data.items():
        sns.kdeplot(df["revenue"], label=cls, fill=True)
    plt.title(f"{flight_id} Revenue Distribution by Class")
    plt.xlabel("Revenue ($)")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{flight_id}_revenue_distribution.png")
    plt.close()

# Load Factor Heatmap
heatmap_data = pd.DataFrame(index=[f for f in FLIGHTS], columns=[c for c in CLASSES])
for flight_id in FLIGHTS:
    for cls in CLASSES:
        heatmap_data.loc[flight_id, cls] = all_data[flight_id][cls]["load"].mean()

plt.figure(figsize=(8,6))
sns.heatmap(heatmap_data.astype(float), annot=True, fmt=".1f", cmap="YlGnBu")
plt.title("Mean Load Factor (%) per Flight/Class")
plt.tight_layout()
plt.savefig("load_factor_heatmap.png")
plt.close()

print("\n✅ Dashboard generated! Check PNG files and CSV logs in 'logs_monte_carlo_dashboard/'")
