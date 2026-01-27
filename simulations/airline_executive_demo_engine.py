"""
AIRLINE EXECUTIVE DEMO SCENARIO ENGINE
=====================================

Purpose:
- Demonstrate one realistic airline crisis
- Show human authority over algorithmic advice
- Provide regulator- and court-ready traceability

This is NOT a simulation engine.
This is a governance demonstration.
"""

from pathlib import Path
from datetime import datetime, UTC
import json

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ------------------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------------------

LOG_DIR = Path("logs_monte_carlo_dashboard")

TRACE_JSON = LOG_DIR / "airline_executive_demo_trace.json"
STORY_TXT = LOG_DIR / "airline_executive_demo_story.txt"
DEMO_PDF = LOG_DIR / "AIRLINE_EXECUTIVE_DEMO.pdf"


# ------------------------------------------------------------------------------
# SCENARIO
# ------------------------------------------------------------------------------

SCENARIO = {
    "incident": "Fuel price shock +40% on marginal route",
    "flight": "FL-1005",
    "class": "economy",
    "system_recommendation": "Reduce frequency / consider suspension",
    "risk_metrics": {
        "stressed_raroc": 0.42,
        "probability_of_loss": 0.63,
        "capital_at_risk": "Elevated",
    },
    "human_override": {
        "decision": "Maintain flight temporarily",
        "justification": [
            "Passenger connectivity obligation",
            "Lack of viable alternate routes",
            "Seasonal demand expected recovery",
        ],
        "override_authority": "Chief Operations Officer",
    },
    "final_outcome": "Flight maintained with monitoring and cost controls",
}


# ------------------------------------------------------------------------------
# BUILD TRACE
# ------------------------------------------------------------------------------

def build_trace():
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "automation_level": "Advisory only",
        "scenario": SCENARIO,
        "safety_guarantees": [
            "Human authority preserved",
            "No autonomous execution",
            "Override logged and auditable",
        ],
    }


# ------------------------------------------------------------------------------
# STORY
# ------------------------------------------------------------------------------

def build_story():
    lines = [
        "AIRLINE EXECUTIVE DEMO – REAL INCIDENT WALKTHROUGH\n",
        "Incident:",
        f"- {SCENARIO['incident']}",
        "",
        "System Advisory:",
        f"- Recommended action: {SCENARIO['system_recommendation']}",
        f"- Stressed RAROC: {SCENARIO['risk_metrics']['stressed_raroc']}",
        f"- Probability of loss: {SCENARIO['risk_metrics']['probability_of_loss']}",
        "",
        "Human Decision:",
        f"- Authority: {SCENARIO['human_override']['override_authority']}",
        f"- Decision: {SCENARIO['human_override']['decision']}",
        "Justifications:",
    ]

    for j in SCENARIO["human_override"]["justification"]:
        lines.append(f"  • {j}")

    lines.extend([
        "",
        "Outcome:",
        f"- {SCENARIO['final_outcome']}",
        "",
        "Key Message:",
        "The system informed the human. The human decided. Safety prevailed.",
    ])

    return "\n".join(lines)


# ------------------------------------------------------------------------------
# PDF
# ------------------------------------------------------------------------------

def build_pdf():
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(DEMO_PDF, pagesize=A4)
    elements = []

    elements.append(Paragraph(
        "<b>AIRLINE EXECUTIVE DECISION DEMONSTRATION</b>",
        styles["Title"]
    ))

    elements.append(Spacer(1, 16))
    elements.append(Paragraph(
        "This document demonstrates how decision-support technology assists, "
        "but does not replace, human airline leadership during operational stress.",
        styles["Normal"]
    ))

    for section, content in [
        ("Incident", SCENARIO["incident"]),
        ("System Recommendation", SCENARIO["system_recommendation"]),
        ("Human Override",
         f"{SCENARIO['human_override']['decision']} "
         f"by {SCENARIO['human_override']['override_authority']}"),
        ("Final Outcome", SCENARIO["final_outcome"]),
    ]:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>{section}</b>", styles["Heading2"]))
        elements.append(Paragraph(content, styles["Normal"]))

    doc.build(elements)


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    print("\n🎯 AIRLINE EXECUTIVE DEMO SCENARIO ENGINE\n")

    trace = build_trace()
    with open(TRACE_JSON, "w") as f:
        json.dump(trace, f, indent=2)

    with open(STORY_TXT, "w") as f:
        f.write(build_story())

    build_pdf()

    print("✅ EXECUTIVE DEMO TRACE CREATED")
    print(f"📜 {TRACE_JSON}")

    print("✅ EXECUTIVE STORY READY")
    print(f"📝 {STORY_TXT}")

    print("✅ EXECUTIVE DEMO PDF READY")
    print(f"📘 {DEMO_PDF}")

    print("\n📌 10-minute CEO walkthrough ready")
    print("📌 Human authority clearly demonstrated")
    print("📌 Regulator-safe by design")


# ------------------------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
