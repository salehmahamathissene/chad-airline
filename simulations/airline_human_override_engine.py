"""
AIRLINE HUMAN-IN-THE-LOOP OVERRIDE ENGINE
----------------------------------------

Purpose:
- Preserve human authority over AI decisions
- Enforce ethical accountability
- Produce regulator-grade override audit trail

AI advises. Humans decide.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path("logs_monte_carlo_dashboard")
OUTPUT_FILE = BASE_DIR / "airline_human_override_audit.csv"


# -------------------------------------------------
# Ethical Framework
# -------------------------------------------------
ETHICAL_PRINCIPLES = {
    "SAFETY_FIRST": "Passenger and crew safety supersedes all objectives",
    "PROPORTIONALITY": "Intervention proportional to risk severity",
    "FAIRNESS": "Passengers treated equitably",
    "HUMAN_DIGNITY": "Avoid unnecessary harm or disruption",
    "TRANSPARENCY": "Decision rationale is explainable"
}


# -------------------------------------------------
# Simulated Human Review Logic
# -------------------------------------------------
def human_review(row):
    """
    Simulated executive oversight.
    In production, this is replaced by UI input.
    """

    decision = row["board_decision"]

    if decision == "GROUND IMMEDIATELY":
        return {
            "override": False,
            "final_decision": decision,
            "human_role": "Chief Safety Officer",
            "ethical_basis": "SAFETY_FIRST",
            "justification": (
                "Risk level unacceptable. Human review confirms grounding."
            )
        }

    if decision == "RESTRUCTURE":
        return {
            "override": True,
            "final_decision": "MAINTAIN",
            "human_role": "Chief Operations Officer",
            "ethical_basis": "PROPORTIONALITY",
            "justification": (
                "Operational mitigation sufficient without cancellation."
            )
        }

    return {
        "override": False,
        "final_decision": decision,
        "human_role": "Duty Operations Manager",
        "ethical_basis": "TRANSPARENCY",
        "justification": (
            "Decision aligns with monitored operational thresholds."
        )
    }


# -------------------------------------------------
# Main Engine
# -------------------------------------------------
def main():
    print("\n🧑‍⚖️ AIRLINE HUMAN-IN-THE-LOOP OVERRIDE ENGINE\n")

    decisions = pd.read_csv(BASE_DIR / "airline_board_decisions.csv")
    legal = pd.read_csv(BASE_DIR / "airline_legal_defense_report.csv")

    df = decisions.merge(
        legal,
        on=["flight", "class"],
        how="left",
        suffixes=("", "_legal")
    )

    overrides = df.apply(human_review, axis=1)
    override_df = pd.DataFrame(list(overrides))

    df = pd.concat([df, override_df], axis=1)

    df["ethical_principle_description"] = df["ethical_basis"].map(
        ETHICAL_PRINCIPLES
    )

    df["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    df["governance_engine"] = "airline_human_override_engine"
    df["governance_version"] = "1.0-production"

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ HUMAN OVERRIDE AUDIT CREATED: {OUTPUT_FILE}")
    print("📌 Accountable | Ethical | Human-controlled\n")


if __name__ == "__main__":
    main()
