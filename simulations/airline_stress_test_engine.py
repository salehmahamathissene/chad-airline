#!/usr/bin/env python3
import os
import pandas as pd

BASE_DIR = "logs_monte_carlo_dashboard"

RAROC_FILE = os.path.join(BASE_DIR, "airline_raroc_report.csv")
LOSS_FILE = os.path.join(BASE_DIR, "probability_of_loss_report.csv")
OUT_FILE = os.path.join(BASE_DIR, "airline_stress_test_report.csv")


def main() -> None:
    os.makedirs(BASE_DIR, exist_ok=True)

    # If inputs missing -> still write valid CSV so board engine never crashes
    if (not os.path.exists(RAROC_FILE)) or os.stat(RAROC_FILE).st_size < 10:
        pd.DataFrame(columns=["flight", "class", "stress_multiplier", "stressed_raroc", "survival"]).to_csv(
            OUT_FILE, index=False
        )
        print(f"✅ Stress report saved to {OUT_FILE} (empty: missing raroc report)")
        return

    raroc_df = pd.read_csv(RAROC_FILE)

    # loss is optional, but improves survival labeling
    if os.path.exists(LOSS_FILE) and os.stat(LOSS_FILE).st_size >= 10:
        loss_df = pd.read_csv(LOSS_FILE)[["flight", "class", "probability_of_loss"]]
        df = raroc_df.merge(loss_df, on=["flight", "class"], how="left")
        df["probability_of_loss"] = df["probability_of_loss"].fillna(0.0)
    else:
        df = raroc_df.copy()
        df["probability_of_loss"] = 0.0

    if "RAROC" not in df.columns:
        df["RAROC"] = 0.0

    # Deterministic stress multiplier
    stress_multiplier = 0.85  # stress reduces performance
    df["stress_multiplier"] = stress_multiplier
    df["stressed_raroc"] = df["RAROC"] * stress_multiplier

    # Deterministic survival rule (works with your board logic)
    # Survive if stressed raroc >= 1.0 and probability_of_loss <= 0.07
    df["survival"] = "SURVIVES"
    df.loc[(df["stressed_raroc"] < 1.0) | (df["probability_of_loss"] > 0.07), "survival"] = "FAILS"

    out = df[["flight", "class", "stress_multiplier", "stressed_raroc", "survival"]].copy()
    out.to_csv(OUT_FILE, index=False)

    print(f"✅ Stress report saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
