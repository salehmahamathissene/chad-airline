"""
AIRLINE EARLY WARNING & SAFETY INTELLIGENCE ENGINE
=================================================

Purpose:
- Detect incident precursors BEFORE accidents
- Learn from institutional memory
- Trigger human review early

STRICT RULES:
- Read-only inputs
- No optimization
- No decision overrides
- Human authority preserved
"""

from pathlib import Path
from datetime import datetime, UTC
import json
import pandas as pd


# ------------------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------------------

LOG_DIR = Path("logs_monte_carlo_dashboard")

RISK_MEMORY = LOG_DIR / "airline_risk_memory_ledger.csv"

EARLY_WARNING_REPORT = LOG_DIR / "airline_early_warning_report.csv"
SAFETY_TRIGGERS = LOG_DIR / "airline_safety_triggers.json"


# ------------------------------------------------------------------------------
# THRESHOLDS (POLICY, NOT CODE LOGIC)
# ------------------------------------------------------------------------------

THRESHOLDS = {
    "human_override_rate": 0.25,
    "high_loss_acceptance_rate": 0.20,
    "stress_exposure_rate": 0.15,
    "incident_repeat_count": 2,
}


# ------------------------------------------------------------------------------
# SIGNAL DETECTION
# ------------------------------------------------------------------------------

def detect_signals(df: pd.DataFrame) -> pd.DataFrame:
    signals = []

    grouped = df.groupby(["flight", "class"])

    for (flight, cls), g in grouped:
        total = len(g)

        overrides = (g["incident_type"] == "Human Override").sum()
        high_loss = (g["incident_type"] == "Accepted High Loss Probability").sum()
        stress = (g["incident_type"] == "Stress Exposure").sum()

        if total == 0:
            continue

        override_rate = overrides / total
        high_loss_rate = high_loss / total
        stress_rate = stress / total

        incident_repeats = g["incident_type"].value_counts().max()

        warnings = []

        if override_rate >= THRESHOLDS["human_override_rate"]:
            warnings.append("Excessive human overrides")

        if high_loss_rate >= THRESHOLDS["high_loss_acceptance_rate"]:
            warnings.append("Repeated acceptance of high-loss decisions")

        if stress_rate >= THRESHOLDS["stress_exposure_rate"]:
            warnings.append("Recurring stress exposure")

        if incident_repeats >= THRESHOLDS["incident_repeat_count"]:
            warnings.append("Repeated incident pattern detected")

        if warnings:
            signals.append(
                {
                    "flight": flight,
                    "class": cls,
                    "override_rate": round(override_rate, 2),
                    "high_loss_acceptance_rate": round(high_loss_rate, 2),
                    "stress_exposure_rate": round(stress_rate, 2),
                    "total_incidents": total,
                    "warnings": "; ".join(warnings),
                }
            )

    return pd.DataFrame(signals)


# ------------------------------------------------------------------------------
# SAFETY TRIGGER BUILDER
# ------------------------------------------------------------------------------

def build_triggers(df: pd.DataFrame) -> dict:
    triggers = []

    for _, row in df.iterrows():
        triggers.append(
            {
                "flight": row["flight"],
                "class": row["class"],
                "trigger_level": "ELEVATED",
                "reason": row["warnings"],
                "recommended_action": "Human safety review required",
            }
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_triggers": len(triggers),
        "triggers": triggers,
    }


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    print("\n🚨 AIRLINE EARLY WARNING & SAFETY INTELLIGENCE ENGINE\n")

    if not RISK_MEMORY.exists():
        raise RuntimeError("Risk memory ledger missing — post-mortem engine required")

    memory = pd.read_csv(RISK_MEMORY)

    signals = detect_signals(memory)

    if signals.empty:
        print("✅ No early warning signals detected")
        return

    signals["generated_at"] = datetime.now(UTC).isoformat()
    signals.to_csv(EARLY_WARNING_REPORT, index=False)

    triggers = build_triggers(signals)

    with open(SAFETY_TRIGGERS, "w") as f:
        json.dump(triggers, f, indent=2)

    print("⚠ EARLY WARNING SIGNALS DETECTED")
    print(f"📄 Report: {EARLY_WARNING_REPORT}")
    print(f"🧾 Triggers: {SAFETY_TRIGGERS}")

    print("\n📌 This is a preventive system — no automation without humans")


# ------------------------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
