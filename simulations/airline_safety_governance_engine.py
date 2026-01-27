"""
AIRLINE SAFETY GOVERNANCE & ETHICS ENGINE
========================================

Purpose:
- Define hard ethical & legal boundaries
- Enforce when automation must STOP
- Preserve human authority

ABSOLUTE RULES:
- This engine NEVER makes decisions
- It only defines limits
- It is immutable policy, not optimization
"""

from pathlib import Path
from datetime import datetime, UTC
import json
import pandas as pd


# ------------------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------------------

LOG_DIR = Path("logs_monte_carlo_dashboard")

ETHICS_CONSTRAINTS = LOG_DIR / "airline_ethics_constraints.json"
AUTOMATION_REDLINES = LOG_DIR / "airline_automation_redlines.csv"


# ------------------------------------------------------------------------------
# ETHICAL CONSTRAINTS (HARD LIMITS)
# ------------------------------------------------------------------------------

ETHICS_POLICY = {
    "human_authority_domains": [
        "Flight cancellation decisions",
        "Denied boarding overrides",
        "Safety vs profit trade-offs",
        "Emergency response escalation",
        "Regulatory compliance exceptions",
    ],
    "automation_prohibited_actions": [
        "Force boarding decisions",
        "Override safety crew judgement",
        "Ignore regulator mandates",
        "Optimize revenue under known safety stress",
    ],
    "mandatory_human_escalation": {
        "loss_probability": 0.20,
        "repeated_incidents": 2,
        "human_override_rate": 0.25,
        "stress_exposure_rate": 0.15,
    },
    "legal_basis": [
        "ICAO Annex 19 – Safety Management",
        "EU Regulation 965/2012",
        "EU AI Act – Human Oversight",
        "Aviation Duty of Care Doctrine",
    ],
    "principle": "No automated decision may reduce human safety margins",
}


# ------------------------------------------------------------------------------
# OPERATIONAL REDLINES
# ------------------------------------------------------------------------------

REDLINES = [
    {
        "redline_id": "RL-001",
        "condition": "Loss probability exceeds threshold",
        "trigger": "probability_of_loss >= 0.20",
        "action": "Automation disabled – human review required",
    },
    {
        "redline_id": "RL-002",
        "condition": "Repeated high-risk incidents",
        "trigger": "incident_count >= 2",
        "action": "Mandatory safety escalation",
    },
    {
        "redline_id": "RL-003",
        "condition": "Excessive human overrides",
        "trigger": "human_override_rate >= 0.25",
        "action": "Automation trust suspended",
    },
    {
        "redline_id": "RL-004",
        "condition": "Operational stress exposure",
        "trigger": "stress_exposure_rate >= 0.15",
        "action": "Safety review before continuation",
    },
    {
        "redline_id": "RL-005",
        "condition": "Conflict between profit and safety",
        "trigger": "profit_optimization_conflicts_with_safety == True",
        "action": "Safety authority prevails",
    },
]


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    print("\n🧭 AIRLINE SAFETY GOVERNANCE & ETHICS ENGINE\n")

    ethics_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "policy_type": "IMMUTABLE",
        "ethics_constraints": ETHICS_POLICY,
    }

    with open(ETHICS_CONSTRAINTS, "w") as f:
        json.dump(ethics_payload, f, indent=2)

    redlines_df = pd.DataFrame(REDLINES)
    redlines_df["generated_at"] = datetime.now(UTC).isoformat()
    redlines_df.to_csv(AUTOMATION_REDLINES, index=False)

    print("🔒 ETHICS CONSTRAINTS ESTABLISHED")
    print(f"📜 {ETHICS_CONSTRAINTS}")

    print("🚫 AUTOMATION REDLINES DEFINED")
    print(f"📄 {AUTOMATION_REDLINES}")

    print("\n📌 Automation is now legally and ethically bounded")
    print("📌 Humans retain final authority")


# ------------------------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
