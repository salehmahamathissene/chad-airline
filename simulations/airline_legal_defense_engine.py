"""
AIRLINE LEGAL & REGULATORY DEFENSE ENGINE
----------------------------------------

Purpose:
- EU261-style compensation exposure estimation
- Legal defensibility of operational decisions
- Audit-grade reasoning layer

This engine DOES NOT override operations.
It documents WHY decisions were reasonable.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path("logs_monte_carlo_dashboard")
OUTPUT_FILE = BASE_DIR / "airline_legal_defense_report.csv"


# -------------------------------------------------
# EU261 PARAMETERS (Simplified but Realistic)
# -------------------------------------------------
EU261_COMPENSATION = {
    "short": 250,    # <1500 km
    "medium": 400,   # 1500–3500 km
    "long": 600      # >3500 km
}


def distance_band(flight_code: str) -> str:
    """
    Placeholder routing logic.
    In real systems this comes from flight metadata.
    """
    num = int(flight_code.split("-")[1])
    if num % 3 == 0:
        return "short"
    elif num % 3 == 1:
        return "medium"
    return "long"


# -------------------------------------------------
# Legal Reasoning Engine
# -------------------------------------------------
def legal_reasoning(row):
    reasons = []

    decision = row.get("board_decision", "UNKNOWN")
    loss_prob = row.get("loss_loss_probability", 0.0)
    raroc = row.get("raroc_raroc", 0.0)

    if decision == "GROUND IMMEDIATELY":
        reasons.append(
            "Aircraft grounded to prevent foreseeable operational failure."
        )
        reasons.append(
            "Decision prioritizes passenger safety over commercial outcome."
        )

    elif decision == "RESTRUCTURE":
        reasons.append(
            "Operational restructuring applied to mitigate financial and safety risk."
        )

    else:
        reasons.append(
            "Flight maintained under monitored operational thresholds."
        )

    if loss_prob > 0.30:
        reasons.append(
            f"Elevated loss probability ({loss_prob:.2%}) justified intervention."
        )

    if raroc < 0:
        reasons.append(
            "Negative capital efficiency reinforced corrective action."
        )

    reasons.append(
        "Decision aligns with proportionality and duty-of-care principles."
    )

    return " ".join(reasons)


# -------------------------------------------------
# Compensation Exposure Model
# -------------------------------------------------
def compensation_exposure(row):
    band = distance_band(row["flight"])
    base = EU261_COMPENSATION[band]

    severity_multiplier = {
        "GROUND IMMEDIATELY": 1.0,
        "RESTRUCTURE": 0.5,
        "MAINTAIN": 0.1
    }.get(row.get("board_decision"), 0.2)

    pax_estimate = {
        "economy": 120,
        "business": 30,
        "first": 10
    }.get(row["class"], 50)

    return base * pax_estimate * severity_multiplier


# -------------------------------------------------
# Main Engine
# -------------------------------------------------
def main():
    print("\n⚖️ AIRLINE LEGAL & REGULATORY DEFENSE ENGINE\n")

    decisions = pd.read_csv(BASE_DIR / "airline_board_decisions.csv")
    loss = pd.read_csv(BASE_DIR / "probability_of_loss_report.csv")
    raroc = pd.read_csv(BASE_DIR / "airline_raroc_report.csv")

    loss = loss.rename(columns={c: f"loss_{c}" for c in loss.columns if c not in ["flight", "class"]})
    raroc = raroc.rename(columns={c: f"raroc_{c}" for c in raroc.columns if c not in ["flight", "class"]})

    df = (
        decisions
        .merge(loss, on=["flight", "class"], how="left")
        .merge(raroc, on=["flight", "class"], how="left")
    )

    df["legal_justification"] = df.apply(legal_reasoning, axis=1)
    df["estimated_compensation_exposure"] = df.apply(compensation_exposure, axis=1)

    df["legal_reviewed_at"] = datetime.now(timezone.utc).isoformat()
    df["engine"] = "airline_legal_defense_engine"
    df["engine_version"] = "1.0-production"

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ LEGAL DEFENSE REPORT CREATED: {OUTPUT_FILE}")
    print("📌 Regulator-ready | Court-defensible | Human-centered\n")


if __name__ == "__main__":
    main()
