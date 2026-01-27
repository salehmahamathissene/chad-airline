import pandas as pd
from pathlib import Path

INPUT_FILE = Path("logs_monte_carlo_dashboard/airline_raroc_report.csv")
OUTPUT_FILE = Path("logs_monte_carlo_dashboard/airline_capital_allocation.csv")

TOTAL_CAPITAL = 100_000_000  # example: $100M strategic capital


def main():
    print("\n💰 AIRLINE CAPITAL ALLOCATION ENGINE\n")

    df = pd.read_csv(INPUT_FILE)

    df["allocation_weight"] = df["RAROC"] / df["RAROC"].sum()
    df["allocated_capital"] = df["allocation_weight"] * TOTAL_CAPITAL

    df["capital_decision"] = df["decision"].map({
        "MAINTAIN": "DEPLOY CAPITAL",
        "EXIT": "WITHDRAW CAPITAL"
    })

    df = df.sort_values("allocated_capital", ascending=False)

    print(df[["flight", "class", "RAROC", "allocated_capital", "capital_decision"]])

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ CAPITAL ALLOCATION SAVED: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
