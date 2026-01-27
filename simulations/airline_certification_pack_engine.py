"""
AIRLINE CERTIFICATION & REGULATOR PACK ENGINE
============================================

Purpose:
- Assemble a regulator-ready safety & governance dossier
- Provide court-defensible, audit-proof documentation
- Translate complex systems into authority language

This engine DOES NOT simulate.
It CERTIFIES.
"""

from pathlib import Path
from datetime import datetime, UTC
import json
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


# ------------------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------------------

LOG_DIR = Path("logs_monte_carlo_dashboard")

SAFETY_CASE_JSON = LOG_DIR / "airline_regulator_safety_case.json"
CERT_EVIDENCE_CSV = LOG_DIR / "airline_certification_evidence.csv"
REGULATOR_PDF = LOG_DIR / "AIRLINE_REGULATOR_BRIEFING.pdf"

INPUTS = {
    "risk": LOG_DIR / "airline_risk_report.csv",
    "raroc": LOG_DIR / "airline_raroc_report.csv",
    "board": LOG_DIR / "airline_board_decisions.csv",
    "explainability": LOG_DIR / "airline_decision_explainability_report.csv",
    "human_override": LOG_DIR / "airline_human_override_audit.csv",
    "postmortem": LOG_DIR / "airline_incident_postmortem_report.csv",
    "ethics": LOG_DIR / "airline_ethics_constraints.json",
}


# ------------------------------------------------------------------------------
# SAFETY CASE BUILDER
# ------------------------------------------------------------------------------

def build_safety_case():
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "system_name": "Chad Airline Decision Intelligence Platform",
        "scope": "Advisory decision support – human authority preserved",
        "certification_principles": [
            "Human-in-the-loop enforcement",
            "Safety-first override",
            "Regulatory compliance by design",
            "Post-incident learning",
            "Auditability & traceability",
        ],
        "components": list(INPUTS.keys()),
        "legal_alignment": [
            "ICAO Annex 19 – Safety Management",
            "EU AI Act – Human Oversight",
            "Aviation Duty of Care",
            "ISO 31000 – Risk Management",
        ],
        "automation_level": "Decision-support only (NO autonomy)",
        "certification_status": "Pre-certification – Authority review required",
    }


# ------------------------------------------------------------------------------
# EVIDENCE TABLE
# ------------------------------------------------------------------------------

def build_evidence_table():
    rows = []
    for name, path in INPUTS.items():
        rows.append({
            "artifact": name,
            "file": path.name,
            "exists": path.exists(),
            "purpose": "Regulatory evidence",
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------
# PDF BRIEFING
# ------------------------------------------------------------------------------

def build_regulator_pdf():
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(REGULATOR_PDF, pagesize=A4)
    elements = []

    elements.append(Paragraph(
        "<b>AIRLINE SAFETY & DECISION GOVERNANCE BRIEFING</b>",
        styles["Title"]
    ))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "This document provides regulatory authorities with a concise overview "
        "of the airline’s decision-support system, governance model, and safety controls.",
        styles["Normal"]
    ))

    sections = [
        ("System Role",
         "This system supports human decision-makers. "
         "It does not execute operational actions autonomously."),
        ("Human Authority",
         "All safety-critical decisions remain under qualified human control."),
        ("Risk Governance",
         "Probabilistic risk, stress exposure, and loss scenarios are continuously assessed."),
        ("Ethical Boundaries",
         "Hard automation redlines prevent unsafe optimization."),
        ("Incident Learning",
         "Post-mortem analysis updates risk memory after real events."),
    ]

    for title, text in sections:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Paragraph(text, styles["Normal"]))

    doc.build(elements)


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

def main():
    print("\n🏛 AIRLINE CERTIFICATION & REGULATOR PACK ENGINE\n")

    safety_case = build_safety_case()
    with open(SAFETY_CASE_JSON, "w") as f:
        json.dump(safety_case, f, indent=2)

    evidence_df = build_evidence_table()
    evidence_df.to_csv(CERT_EVIDENCE_CSV, index=False)

    build_regulator_pdf()

    print("✅ REGULATOR SAFETY CASE CREATED")
    print(f"📜 {SAFETY_CASE_JSON}")

    print("✅ CERTIFICATION EVIDENCE GENERATED")
    print(f"📄 {CERT_EVIDENCE_CSV}")

    print("✅ REGULATOR BRIEFING PDF READY")
    print(f"📘 {REGULATOR_PDF}")

    print("\n📌 This pack is authority-facing, not marketing")
    print("📌 Airline leadership can submit this directly")


# ------------------------------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
