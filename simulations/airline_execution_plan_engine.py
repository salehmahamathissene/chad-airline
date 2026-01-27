# simulations/airline_execution_plan_engine.py

import pandas as pd
from pathlib import Path
from datetime import datetime, UTC

LOG_DIR = Path("logs_monte_carlo_dashboard")
INPUT_FILE = LOG_DIR / "airline_board_decisions.csv"
OUTPUT_FILE = LOG_DIR / "airline_execution_plan.csv"


def execution_template(board_decision: str) -> dict:
    """
    Translate board decision into EXECUTION GUIDANCE.
    This does NOT execute actions — it defines governance-level steps.
    """

    if board_decision == "GROUND IMMEDIATELY":
        return {
            "execution_action": "Temporary grounding for safety & cost review",
            "responsible_unit": "Flight Operations + Safety",
            "review_horizon_days": 7,
            "risk_control": "Suspend scheduling, preserve aircraft, notify regulator",
        }

    if board_decision == "RESTRUCTURE":
        return {
            "execution_action": "Cost & route restructuring",
            "responsible_unit": "Strategy + Finance",
            "review_horizon_days": 30,
            "risk_control": "Capacity adjustment, pricing review, fleet reassignment",
        }

    if board_decision == "MAINTAIN":
        return {
            "execution_action": "Continue operations with monitoring",
            "responsible_unit": "Operations Control",
            "review_horizon_days": 90,
            "risk_control": "Monthly KPI + risk review",
        }

    return {
        "execution_action": "No action",
        "responsible_unit": "N/A",
        "review_horizon_days": 0,
        "risk_control": "N/A",
    }


def main():
    print("\n🚀 AIRLINE EXECUTION PLAN ENGINE\n")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing board decision file: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    execution_rows = []

    for _, row in df.iterrows():
        template = execution_template(row["board_decision"])

        execution_rows.append({
            "flight": row["flight"],
            "class": row["class"],
            "board_decision": row["board_decision"],
            "execution_action": template["execution_action"],
            "responsible_unit": template["responsible_unit"],
            "review_horizon_days": template["review_horizon_days"],
            "risk_control": template["risk_control"],
            "generated_at": datetime.now(UTC).isoformat()
        })

    execution_df = pd.DataFrame(execution_rows)

    execution_df.to_csv(OUTPUT_FILE, index=False)

    print(execution_df.head(10))
    print(f"\n✅ EXECUTION PLAN SAVED: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
