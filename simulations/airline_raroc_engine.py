import pandas as pd

INPUT_CSV = "logs_monte_carlo_dashboard/airline_risk_report.csv"
OUTPUT_CSV = "logs_monte_carlo_dashboard/airline_raroc_report.csv"

def compute_raroc(row):
    expected_loss = row["CVaR_95"]
    economic_capital = max(row["mean_revenue"] - row["VaR_95"], 1)
    return (row["mean_revenue"] - expected_loss) / economic_capital

def main():
    print("\n🏦 AIRLINE RAROC ENGINE\n")

    df = pd.read_csv(INPUT_CSV)

    df["RAROC"] = df.apply(compute_raroc, axis=1)

    df["decision"] = df["RAROC"].apply(
        lambda x: "EXPAND" if x > 2.0 else "MAINTAIN" if x > 1.2 else "EXIT"
    )

    df = df.sort_values("RAROC", ascending=False)

    print(df[["flight", "class", "RAROC", "decision"]])

    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n✅ RAROC report saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
