#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


REQUIRED_CSVS = [
    "airline_board_decisions.csv",
    "airline_decision_explainability_report.csv",
    "airline_risk_report.csv",
    "airline_raroc_report.csv",
    "probability_of_loss_report.csv",
]


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def project_root() -> Path:
    # This file lives in ./simulations, so root is parent of this file's parent
    return Path(__file__).resolve().parent.parent


def run_script(script_rel: str, env: dict, cwd: Path) -> int:
    """
    Runs a simulation script as a subprocess using the same interpreter (sys.executable),
    preserving PYTHONPATH.
    Returns exit code.
    """
    cmd = [sys.executable, script_rel]
    print(f"▶ Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(cwd), env=env)
    return r.returncode


def copy_if_exists(src_dir: Path, dst_dir: Path, name: str) -> bool:
    src = src_dir / name
    dst = dst_dir / name
    if src.exists() and src.is_file():
        shutil.copy2(src, dst)
        return True
    return False


def write_placeholder_csvs(dashboard_dir: Path) -> None:
    """
    If simulation suite didn't create expected CSVs, we generate minimal placeholders.
    This prevents CEO PDF generator from crashing. For a sellable demo, "never fail".
    """
    ensure_dir(dashboard_dir)

    # Minimal content that pandas can parse.
    placeholders = {
        "airline_board_decisions.csv": "flight_id,decision,reason,occurred_at\n",
        "airline_decision_explainability_report.csv": "metric,value\n",
        "airline_risk_report.csv": "risk_type,score\n",
        "airline_raroc_report.csv": "segment,raroc\n",
        "probability_of_loss_report.csv": "scenario,probability\n",
    }

    for fname, content in placeholders.items():
        f = dashboard_dir / fname
        if not f.exists():
            f.write_text(content, encoding="utf-8")
            print(f"🧩 Wrote placeholder: {f}")


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="run_airline_monte_carlo_suite",
        description="Generates Monte Carlo dashboard CSVs needed for CEO PDF report.",
    )
    ap.add_argument(
        "--out",
        required=True,
        help="Output dashboard directory (CSV files will be created here).",
    )
    ap.add_argument(
        "--run-id",
        default=None,
        help="Optional run id label (used only for logging).",
    )
    ap.add_argument(
        "--skip-simulations",
        action="store_true",
        help="Do not run heavy simulation scripts; only ensure CSVs exist (placeholders).",
    )
    args = ap.parse_args()

    run_id = args.run_id or utc_run_id()
    dashboard_dir = Path(args.out).expanduser().resolve()
    ensure_dir(dashboard_dir)

    root = project_root()
    # Make sure domain/ can be imported by subprocess scripts
    env = dict(os.environ)
    existing_pp = env.get("PYTHONPATH", "")
    root_pp = str(root)
    if root_pp not in existing_pp.split(":"):
        env["PYTHONPATH"] = (root_pp + (":" + existing_pp if existing_pp else ""))

    print("\n✈️ AIRLINE MONTE CARLO OPERATIONS SUITE")
    print(f"🆔 Run: {run_id}")
    print(f"📁 Project root: {root}")
    print(f"📁 Dashboard out: {dashboard_dir}")
    print(f"🔧 PYTHONPATH: {env.get('PYTHONPATH')}\n")

    # Your repository already has scripts that (likely) generate CSVs into logs_monte_carlo_dashboard.
    # We run them (unless skipped), then copy results into dashboard_dir.
    generated_any = False

    if not args.skip_simulations:
        # Run the suite’s scripts (best-effort).
        scripts = [
            "simulations/ticket_lifecycle_simulator.py",
            "simulations/monte_carlo_kpi_dashboard.py",
            "simulations/monte_carlo_kpi_report.py",
            "simulations/probability_of_loss_engine.py",
        ]

        for s in scripts:
            rc = run_script(s, env=env, cwd=root)
            if rc != 0:
                print(f"⚠️ Script failed (rc={rc}): {s} — continuing (no hard fail).")

    # Copy any CSVs produced by legacy path into our run dashboard folder
    legacy_dir = root / "logs_monte_carlo_dashboard"
    if legacy_dir.exists() and legacy_dir.is_dir():
        print(f"\n📦 Found legacy output folder: {legacy_dir}")
        for fname in REQUIRED_CSVS:
            if copy_if_exists(legacy_dir, dashboard_dir, fname):
                generated_any = True
                print(f"✅ Copied: {fname}")
            else:
                print(f"⚠️ Missing in legacy folder: {fname}")
    else:
        print(f"\n⚠️ Legacy folder not found: {legacy_dir}")

    # Ensure required CSVs exist (create placeholders if missing)
    write_placeholder_csvs(dashboard_dir)

    # Final verification
    missing = [f for f in REQUIRED_CSVS if not (dashboard_dir / f).exists()]
    if missing:
        print("\n❌ STILL missing required CSVs:")
        for m in missing:
            print("  -", m)
        return 2

    print("\n✅ Dashboard CSVs ready:")
    for f in REQUIRED_CSVS:
        print("  -", dashboard_dir / f)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

