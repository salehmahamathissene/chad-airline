#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet


def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def read_csv_safe(path: Path) -> tuple[pd.DataFrame | None, str | None]:
    try:
        if not path.exists():
            return None, f"Missing file: {path.name}"
        df = pd.read_csv(path)
        if df.empty:
            return None, f"Empty CSV: {path.name}"
        return df, None
    except Exception as e:
        return None, f"Failed reading {path.name}: {e}"


def df_to_table(df: pd.DataFrame, max_rows: int = 20) -> Table:
    show = df.head(max_rows).copy()
    data = [list(show.columns)] + show.values.tolist()

    t = Table(data, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def pick_key_decisions(board_df: pd.DataFrame) -> pd.DataFrame:
    """
    Professional executive slice:
    - Ground immediately
    - Expand
    - Restructure
    - Maintain
    """
    cols = [c for c in ["flight", "class", "board_decision", "RAROC", "probability_of_loss", "survival"] if c in board_df.columns]
    view = board_df[cols].copy() if cols else board_df.copy()

    # Sort by severity if possible
    if "board_decision" in view.columns:
        priority = {
            "GROUND IMMEDIATELY": 0,
            "RESTRUCTURE": 1,
            "EXIT": 2,
            "MAINTAIN": 3,
            "EXPAND": 4,
        }
        view["_prio"] = view["board_decision"].map(priority).fillna(99)
        view = view.sort_values(["_prio"], ascending=True).drop(columns=["_prio"], errors="ignore")

    return view.head(20)


def iter_pngs(images_dir: Path) -> Iterable[Path]:
    if not images_dir.exists():
        return []
    # Keep a stable order: heatmaps first, then revenue distributions, then everything else.
    all_png = sorted(images_dir.glob("*.png"), key=lambda p: p.name.lower())

    def rank(name: str) -> int:
        n = name.lower()
        if "heatmap" in n:
            return 0
        if "distribution" in n:
            return 1
        if "monte_carlo" in n:
            return 2
        if "revenue" in n:
            return 3
        return 9

    return sorted(all_png, key=lambda p: (rank(p.name), p.name.lower()))


def scaled_image(path: Path, max_w: float, max_h: float) -> Image:
    """
    Create a ReportLab Image scaled to fit max_w/max_h while preserving aspect ratio.
    """
    img = Image(str(path))
    iw, ih = img.imageWidth, img.imageHeight
    if iw <= 0 or ih <= 0:
        return img

    scale = min(max_w / iw, max_h / ih)
    img.drawWidth = iw * scale
    img.drawHeight = ih * scale
    return img


def build_pdf(dashboard_dir: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "EXECUTIVE_REPORT.pdf"

    styles = getSampleStyleSheet()
    H1 = styles["Heading1"]
    H2 = styles["Heading2"]
    P = styles["BodyText"]

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="CHAD-AIRLINE Executive Report",
        author="CHAD-AIRLINE Engine",
    )

    story = []

    # Title page
    story.append(Paragraph("CHAD-AIRLINE Executive Report", H1))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Generated (UTC): {utc_now_str()}", P))
    story.append(Paragraph(f"Dashboard source: {dashboard_dir}", P))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "Scope: Monte Carlo KPI → Risk (CI/VaR/CVaR) → Probability of Loss → RAROC → Stress Test → Board Decisions → Execution Plan → Explainability.",
        P
    ))
    story.append(PageBreak())

    # Load CSVs
    files = {
        "Risk Report": dashboard_dir / "airline_risk_report.csv",
        "Probability of Loss": dashboard_dir / "probability_of_loss_report.csv",
        "RAROC": dashboard_dir / "airline_raroc_report.csv",
        "Stress Test": dashboard_dir / "airline_stress_test_report.csv",
        "Board Decisions": dashboard_dir / "airline_board_decisions.csv",
        "Execution Plan": dashboard_dir / "airline_execution_plan.csv",
        "Explainability": dashboard_dir / "airline_decision_explainability_report.csv",
    }

    warnings: list[str] = []
    dfs: dict[str, pd.DataFrame] = {}

    for title, path in files.items():
        df, err = read_csv_safe(path)
        if err:
            warnings.append(err)
        else:
            dfs[title] = df

    # Executive Summary
    story.append(Paragraph("Executive Summary", H2))
    story.append(Spacer(1, 0.2 * cm))

    if "Board Decisions" in dfs:
        bd = dfs["Board Decisions"]
        key = pick_key_decisions(bd)
        story.append(Paragraph("Key Decisions (Top 20)", styles["Heading3"]))
        story.append(df_to_table(key, max_rows=20))
        story.append(Spacer(1, 0.4 * cm))

        if "board_decision" in bd.columns:
            counts = bd["board_decision"].value_counts().reset_index()
            counts.columns = ["board_decision", "count"]
            story.append(Paragraph("Decision Distribution", styles["Heading3"]))
            story.append(df_to_table(counts, max_rows=20))
            story.append(Spacer(1, 0.3 * cm))
    else:
        story.append(Paragraph("Board Decisions not available.", P))

    if warnings:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("Warnings", styles["Heading3"]))
        for w in warnings[:12]:
            story.append(Paragraph(f"• {w}", P))

    story.append(PageBreak())

    # Data sections
    for section in ["Risk Report", "Probability of Loss", "RAROC", "Stress Test", "Execution Plan", "Explainability"]:
        if section in dfs:
            story.append(Paragraph(section, H2))
            story.append(Spacer(1, 0.2 * cm))
            story.append(df_to_table(dfs[section], max_rows=30))
            story.append(PageBreak())

    # Charts section
    images_dir = dashboard_dir / "images"
    pngs = list(iter_pngs(images_dir))

    story.append(Paragraph("Charts & Visual Evidence", H2))
    story.append(Spacer(1, 0.2 * cm))

    if not pngs:
        story.append(Paragraph("No charts found in dashboard/images/.", P))
    else:
        max_per_report = 24  # keep PDF sane
        page_w, page_h = A4
        usable_w = page_w - doc.leftMargin - doc.rightMargin
        usable_h = page_h - doc.topMargin - doc.bottomMargin

        # Layout: 1 chart per page (clean + professional)
        for i, p in enumerate(pngs[:max_per_report], start=1):
            story.append(Paragraph(f"Chart {i}: {p.name}", styles["Heading3"]))
            story.append(Spacer(1, 0.15 * cm))

            # Leave room for caption/title
            img = scaled_image(p, max_w=usable_w, max_h=usable_h - 4 * cm)
            story.append(img)
            story.append(Spacer(1, 0.4 * cm))
            story.append(PageBreak())

    doc.build(story)
    return pdf_path


def main() -> int:
    ap = argparse.ArgumentParser(prog="airline_ceo_pdf_report")
    ap.add_argument("--dashboard", required=True, help="Dashboard directory containing CSVs (+ images/).")
    ap.add_argument("--out", required=True, help="Reports output directory.")
    args = ap.parse_args()

    dashboard_dir = Path(args.dashboard)
    out_dir = Path(args.out)

    pdf_path = build_pdf(dashboard_dir, out_dir)
    size = pdf_path.stat().st_size if pdf_path.exists() else 0
    print(f"✅ CEO report generated: {pdf_path} (bytes={size})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
