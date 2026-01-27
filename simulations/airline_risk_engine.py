import os
import numpy as np
import pandas as pd

LOG_DIR = "logs_monte_carlo_dashboard"
OUTPUT_DIR = "logs_monte_carlo_dashboard"
CONFIDENCE_LEVEL = 0.95


def compute_risk_metrics(values: np.ndarray):
    values = np.asarray(values, dtype=float)

    mean = float(np.mean(values))
    std = float(np.std(values))

    lower = float(np.percentile(values, (1 - CONFIDENCE_LEVEL) / 2 * 100))
    upper = float(np.percentile(values, (1 + CONFIDENCE_LEVEL) / 2 * 100))

    var = float(np.percentile(values, (1 - CONFIDENCE_LEVEL) * 100))
    tail = values[values <= var]
    cvar = float(np.mean(tail)) if tail.size > 0 else var

    return {
        "mean_revenue": mean,
        "revenue_std": std,
        "ci_lower_95": lower,
        "ci_upper_95": upper,
        "VaR_95": var,
        "CVaR_95": cvar,
    }


def parse_metadata(filename: str):
    """
    Expected format:
      FL-1001_economy_simulation.csv
    """
    base = filename.replace(".csv", "")
    parts = base.split("_")
    flight = parts[0] if len(parts) > 0 else "UNKNOWN"
    cabin_class = parts[1] if len(parts) > 1 else "UNKNOWN"
    return flight, cabin_class


def main():
    print("\n📉 AIRLINE RISK & CONFIDENCE ENGINE\n")

    # Ensure directories exist (prevents FileNotFoundError)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    records = []

    # Scan simulation outputs created by monte_carlo_kpi_dashboard.py
    for file in sorted(os.listdir(LOG_DIR)):
        # IMPORTANT: only process the per-flight simulation files, not summary reports
        if not (file.endswith(".csv") and file.endswith("_simulation.csv")):
            continue

        flight, cabin_class = parse_metadata(file)
        path = os.path.join(LOG_DIR, file)

        try:
            df = pd.read_csv(path)
        except Exception:
            continue

        # REQUIRED: revenue column must exist
        if "revenue" not in df.columns:
            continue

        values = df["revenue"].dropna().values
        if len(values) == 0:
            continue

        metrics = compute_risk_metrics(values)

        records.append(
            {
                "flight": flight,
                "class": cabin_class,
                **metrics,
            }
        )

    # Build result_df safely EVEN IF no records
    if records:
        result_df = pd.DataFrame(records)
    else:
        result_df = pd.DataFrame(
            columns=[
                "flight",
                "class",
                "mean_revenue",
                "revenue_std",
                "ci_lower_95",
                "ci_upper_95",
                "VaR_95",
                "CVaR_95",
            ]
        )

    # Define out_path BEFORE using it
    out_path = os.path.join(OUTPUT_DIR, "airline_risk_report.csv")
    result_df.to_csv(out_path, index=False)

    # Print small preview (safe)
    if not result_df.empty:
        print(result_df.round(2).head(20))
    else:
        print(result_df)

    print(f"\n✅ Risk report saved to {out_path}")


if __name__ == "__main__":
    main()
