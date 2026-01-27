"""
AIRLINE DECISION EXPLAINABILITY ENGINE
-------------------------------------

Enterprise-grade explainability layer.
- Zero mutation
- Schema-adaptive
- Regulator safe
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path("logs_monte_carlo_dashboard")
OUTPUT_FILE = BASE_DIR / "airline_decision_explainability_report.csv"


# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------
def normalize_columns(df, prefix, protected=("flight", "class", "decision")):
    return df.rename(
        columns={
            c: f"{prefix}_{c}"
            for c in df.columns
            if c not in protected
        }
    )


def safe(row, key, default=0.0):
    return row[key] if key in row and pd.notna(row[key]) else default


# -------------------------------------------------------------------
# Explainability Logic (Schema-Adaptive)
# -------------------------------------------------------------------
def explain_decision(row):
    explanations = []

    # -----------------------------
    # Revenue Signal (Adaptive)
    # -----------------------------
    revenue_signal = None
    for candidate in [
        "rev_expected_revenue",
        "rev_mean_revenue",
        "rev_total_revenue",
    ]:
        if candidate in row:
            revenue_signal = safe(row, candidate)
            break

    if revenue_signal is not None:
        if revenue_signal > 0:
            explanations.append(
                f"Revenue signal ({revenue_signal:.2f}) supports continuation."
            )
        else:
            explanations.append(
                f"Negative revenue signal ({revenue_signal:.2f}) raises concern."
            )
    else:
        explanations.append(
            "Revenue signal unavailable; decision relies on risk controls."
        )

    # -----------------------------
    # Loss Probability
    # -----------------------------
    loss_prob = safe(row, "loss_loss_probability")
    if loss_prob > 0.30:
        explanations.append(
            f"Loss probability {loss_prob:.2%} exceeds airline risk appetite."
        )
    else:
        explanations.append(
            f"Loss probability {loss_prob:.2%} within acceptable bounds."
        )

    # -----------------------------
    # RAROC / Capital Efficiency
    # -----------------------------
    raroc = safe(row, "raroc_raroc")
    if raroc >= 0.15:
        explanations.append(
            f"RAROC {raroc:.2%} exceeds capital hurdle rate."
        )
    elif raroc > 0:
        explanations.append(
            f"RAROC {raroc:.2%} marginal but positive."
        )
    else:
        explanations.append(
            f"RAROC {raroc:.2%} indicates capital inefficiency."
        )

    # -----------------------------
    # Final Alignment
    # -----------------------------
    explanations.append(
        f"Final board decision: {row.get('decision', 'UNSPECIFIED')}."
    )

    return " ".join(explanations)


# -------------------------------------------------------------------
# Main Engine
# -------------------------------------------------------------------
def main():
    print("\n🧾 AIRLINE DECISION EXPLAINABILITY ENGINE\n")

    decisions = pd.read_csv(BASE_DIR / "airline_board_decisions.csv")
    revenue = pd.read_csv(BASE_DIR / "airline_execution_plan.csv")
    loss = pd.read_csv(BASE_DIR / "probability_of_loss_report.csv")
    raroc = pd.read_csv(BASE_DIR / "airline_raroc_report.csv")

    revenue = normalize_columns(revenue, "rev")
    loss = normalize_columns(loss, "loss")
    raroc = normalize_columns(raroc, "raroc")

    df = (
        decisions
        .merge(revenue, on=["flight", "class"], how="left")
        .merge(loss, on=["flight", "class"], how="left")
        .merge(raroc, on=["flight", "class"], how="left")
    )

    df["explanation"] = df.apply(explain_decision, axis=1)

    df["explained_at"] = datetime.now(timezone.utc).isoformat()
    df["engine"] = "airline_decision_explainability_engine"
    df["engine_version"] = "1.1-production"

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ EXPLAINABILITY REPORT CREATED: {OUTPUT_FILE}")
    print("📌 Schema-adaptive, audit-safe, regulator-ready\n")


if __name__ == "__main__":
    main()
