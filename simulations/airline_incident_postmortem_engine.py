"""
AIRLINE INCIDENT & POST-MORTEM LEARNING ENGINE
=============================================

This engine performs institutional learning AFTER decisions.
It never re-optimizes, never overrides history, never fabricates data.

Design principles:
- Read-only inputs
- Schema-adaptive ingestion
- Append-only institutional memory
- Court & regulator defensible
"""

from datetime import datetime, UTC
from pathlib import Path
import pandas as pd


# ------------------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------------------

LOG_DIR = Path("logs_monte_carlo_dashboard")

FILES = {
    "board": LOG_DIR / "airline_board_decisions.csv",
    "risk": LOG_DIR / "airline_risk_report.csv",
    "raroc": LOG_DIR / "airline_raroc_report.csv",
    "stress": LOG_DIR / "airline_stress_test_report.csv",
    "loss_prob": LOG_DIR / "probability_of_loss_report.csv",
    "override": LOG_DIR / "airline_human_override_audit.csv",
}

POSTMORTEM_REPORT = LOG_DIR / "airline_incident_postmortem_report.csv"
RISK_MEMORY_LEDGER = LOG_DIR / "airline_risk_memory_ledger.csv"


# ------------------------------------------------------------------------------
# SAFE LOADERS
# ------------------------------------------------------------------------------

def safe_load(name: str) -> pd.DataFrame:
    path = FILES[name]
    if not path.exists():
        print(f"⚠ Missing input: {path.name} — continuing safely")
        return pd.DataFrame()
    return pd.read_csv(path)


def safe_merge(left: pd.DataFrame, right: pd.DataFrame, on: list[str]) -> pd.DataFrame:
    if right.empty:
        return left
    overlap = set(left.columns) & set(right.columns) - set(on)
    right = right.drop(columns=list(overlap), errors="ignore")
    return left.merge(right, on=on, how="left")


# ------------------------------------------------------------------------------
# INCIDENT CLASSIFICATION
# ------------------------------------------------------------------------------

def classify_incident(row) -> str:
    if row.get("human_override", False):
        return "Human Override"
    if row.get("decision") == "APPROVE" and row.get("probability_of_loss", 0) > 0.15:
        return "Accepted High Loss Probability"
    if row.get("decision") == "REJECT" and row.get("raroc", 0) > 0:
        return "Over-Conservatism"
    if row.get("stress_loss", 0) < 0:
        return "Stress Exposure"
    return "Normal Operation"


def learning_signal(row) -> str:
    return {
        "Human Override": "Improve model transparency",
        "Accepted High Loss Probability": "Recalibrate loss tolerance",
        "Over-Conservatism": "Review rejection thresholds",
        "Stress Exposure": "Increase stress buffers",
        "Normal Operation": "No action required",
    }.get(row["incident_type"], "No action required")


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    print("\n🛫 AIRLINE INCIDENT & POST-MORTEM LEARNING ENGINE\n")

    board = safe_load("board")
    if board.empty:
        raise RuntimeError("Board decisions are mandatory")

    risk = safe_load("risk")
    raroc = safe_load("raroc")
    stress = safe_load("stress")
    loss_prob = safe_load("loss_prob")
    override = safe_load("override")

    df = board.copy()

    df = safe_merge(df, risk, ["flight", "class"])
    df = safe_merge(df, raroc, ["flight", "class"])
    df = safe_merge(df, stress, ["flight", "class"])
    df = safe_merge(df, loss_prob, ["flight", "class"])
    df = safe_merge(df, override, ["flight", "class"])

    df["incident_type"] = df.apply(classify_incident, axis=1)
    df["learning_signal"] = df.apply(learning_signal, axis=1)
    df["postmortem_timestamp"] = datetime.now(UTC).isoformat()

    df.to_csv(POSTMORTEM_REPORT, index=False)

    memory = df[
        [
            "flight",
            "class",
            "decision",
            "incident_type",
            "learning_signal",
            "postmortem_timestamp",
        ]
    ]

    if RISK_MEMORY_LEDGER.exists():
        memory = pd.concat(
            [pd.read_csv(RISK_MEMORY_LEDGER), memory], ignore_index=True
        )

    memory.to_csv(RISK_MEMORY_LEDGER, index=False)

    print("✅ POST-MORTEM REPORT CREATED")
    print(f"   {POSTMORTEM_REPORT}")

    print("🧠 RISK MEMORY UPDATED")
    print(f"   {RISK_MEMORY_LEDGER}")

    print("\n📌 Airline now learns from reality — not assumptions")


# ------------------------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
