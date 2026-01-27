from __future__ import annotations

from pathlib import Path
import shutil


def generate(base_dir: Path) -> Path:
    base_dir = Path(base_dir)
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Output produced by simulations/airline_ceo_pdf_report.py
    src = Path("logs_monte_carlo_dashboard") / "AIRLINE_CEO_RISK_REPORT.pdf"
    dst = reports_dir / "EXECUTIVE_REPORT.pdf"

    if not src.exists():
        raise FileNotFoundError(f"Missing source PDF: {src}")

    shutil.copyfile(src, dst)
    return dst
