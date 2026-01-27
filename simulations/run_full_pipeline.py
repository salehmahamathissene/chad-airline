#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Headless-safe charts in Docker
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# CSVs expected by CEO PDF
REQUIRED_CSVS = [
    "airline_board_decisions.csv",
    "airline_decision_explainability_report.csv",
    "airline_risk_report.csv",
    "airline_raroc_report.csv",
    "probability_of_loss_report.csv",
    "airline_execution_plan.csv",
]

# Extra CSV required by board engine
EXTRA_REQUIRED = [
    "airline_stress_test_report.csv",
]

ALL_REQUIRED = REQUIRED_CSVS + EXTRA_REQUIRED


def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def repo_root() -> Path:
    # This file lives at /app/simulations/run_full_pipeline.py inside the image
    return Path(__file__).resolve().parents[1]


def _append_log(log_file: Path, text: str) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(text)


def run_script(
    script_rel: str,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    extra_args: list[str] | None = None,
    log_file: Path | None = None,
) -> int:
    """
    PRO runner:
    - Captures stdout/stderr always
    - Logs every command, RC, stdout, stderr to pipeline_debug.log
    - Uses cwd=/app by default so scripts that rely on repo-relative paths do not break
    """
    cmd = [sys.executable, script_rel]
    if extra_args:
        cmd.extend(extra_args)

    cwd_use = cwd if cwd is not None else repo_root()

    print(f"▶ Running: {' '.join(cmd)}")
    try:
        p = subprocess.run(
            cmd,
            env=env,
            cwd=str(cwd_use),
            text=True,
            capture_output=True,
        )

        # Print to console
        if p.stdout:
            print(p.stdout.rstrip())
        if p.stderr:
            print(p.stderr.rstrip())

        # Write to debug log
        if log_file is not None:
            _append_log(
                log_file,
                "\n"
                + "=" * 90
                + "\n"
                + f"TIME: {utc_now_str()}\n"
                + f"CMD : {' '.join(cmd)}\n"
                + f"CWD : {cwd_use}\n"
                + f"RC  : {p.returncode}\n"
                + ("--- STDOUT ---\n" + p.stdout + "\n" if p.stdout else "")
                + ("--- STDERR ---\n" + p.stderr + "\n" if p.stderr else "")
            )

        return int(p.returncode)

    except Exception as e:
        msg = f"⚠️ Script launcher failed: {script_rel}: {e}\n"
        print(msg.rstrip())
        if log_file is not None:
            _append_log(
                log_file,
                "\n" + "=" * 90 + "\n" + f"TIME: {utc_now_str()}\n" + f"CMD : {' '.join(cmd)}\n" + f"EXC : {e}\n"
            )
        return 1


def ensure_symlink(link_path: Path, target_dir: Path, *, log_file: Path | None = None) -> None:
    """
    Create/refresh a symlink so scripts writing to /app/logs_monte_carlo_dashboard
    actually write into the mounted output volume: /out/<run_id>/logs_monte_carlo_dashboard
    """
    try:
        ensure_dir(target_dir)

        # If it exists and is already correct, leave it
        if link_path.exists() or link_path.is_symlink():
            try:
                if link_path.is_symlink() and link_path.resolve() == target_dir.resolve():
                    return
            except Exception:
                pass

            # Remove existing file/dir/symlink
            if link_path.is_symlink() or link_path.is_file():
                link_path.unlink(missing_ok=True)  # py3.11+
            elif link_path.is_dir():
                shutil.rmtree(link_path)

        link_path.symlink_to(target_dir, target_is_directory=True)

        if log_file is not None:
            _append_log(
                log_file,
                "\n" + "=" * 90 + "\n" + f"TIME: {utc_now_str()}\n" + f"SYMLINK: {link_path} -> {target_dir}\n",
            )

    except Exception as e:
        warn = f"⚠️ Could not create symlink {link_path} -> {target_dir}: {e}\n"
        print(warn.rstrip())
        if log_file is not None:
            _append_log(log_file, "\n" + "=" * 90 + "\n" + f"TIME: {utc_now_str()}\n" + warn)


def copy_if_exists(src: Path, dst: Path) -> bool:
    """
    Copy only if src is a real non-empty file and NOT the same file as dst.
    """
    try:
        if not (src.exists() and src.is_file() and src.stat().st_size > 0):
            return False

        # Same-file protections
        try:
            if src.resolve() == dst.resolve():
                return False
        except Exception:
            pass

        try:
            if os.path.samefile(src, dst):
                return False
        except FileNotFoundError:
            pass
        except Exception:
            pass

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def write_or_repair_placeholders(dashboard_dir: Path) -> None:
    """
    Sellable mode guarantee:
    - Every required CSV exists
    - Every required CSV is readable by pandas (not empty / not broken)

    NOTE:
    In STRICT mode we still fail later if placeholders are used.
    """
    ensure_dir(dashboard_dir)

    placeholders = {
        "airline_board_decisions.csv": (
            "flight,class,RAROC,probability_of_loss,survival,board_decision\n"
            "FL-1001,economy,1.20,0.0000,SURVIVES,MAINTAIN\n"
        ),
        "airline_decision_explainability_report.csv": (
            "metric,value,notes\n"
            "model_version,1.0,placeholder-generated\n"
        ),
        "airline_execution_plan.csv": (
            "flight,class,board_decision,pricing_action,fleet_action,status\n"
            "FL-1001,economy,MAINTAIN,HOLD,NO CHANGE,ACTIVE\n"
        ),
        "airline_risk_report.csv": (
            "flight,class,mean_revenue,revenue_std,ci_lower_95,ci_upper_95,VaR_95,CVaR_95\n"
            "FL-1001,economy,22000,400,21200,22800,21500,21300\n"
        ),
        "airline_raroc_report.csv": (
            "flight,class,RAROC,decision\n"
            "FL-1001,economy,1.20,MAINTAIN\n"
        ),
        "probability_of_loss_report.csv": (
            "flight,class,mean_revenue,revenue_std,probability_of_loss,risk_level\n"
            "FL-1001,economy,22000,400,0.0000,SAFE\n"
        ),
        "airline_stress_test_report.csv": (
            "flight,class,stress_multiplier,stressed_raroc,survival\n"
            "FL-1001,economy,1.25,1.10,SURVIVES\n"
        ),
    }

    for fname in ALL_REQUIRED:
        f = dashboard_dir / fname

        if not f.exists():
            f.write_text(placeholders.get(fname, "col\nplaceholder\n"), encoding="utf-8")
            print(f"🧩 Created placeholder (missing): {fname}")
            continue

        if f.stat().st_size < 10:
            f.write_text(placeholders.get(fname, "col\nplaceholder\n"), encoding="utf-8")
            print(f"🧩 Repaired placeholder (too small): {fname}")
            continue

        try:
            pd.read_csv(f)
        except Exception:
            f.write_text(placeholders.get(fname, "col\nplaceholder\n"), encoding="utf-8")
            print(f"🧩 Repaired placeholder (unreadable): {fname}")


def csv_rowcount(path: Path) -> int:
    """
    Return number of rows in a CSV excluding header.
    Returns 0 on failure.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        return max(0, lines - 1)
    except Exception:
        return 0


def _env_for_run(
    *,
    out_dir: Path,
    run_id: str,
    flights: int,
    tickets_per_flight: int,
    seed: int | None,
) -> dict[str, str]:
    """
    Single source of truth for environment passed to all scripts.
    SAFE: scripts that don't care will ignore.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = env.get("PYTHONPATH", "/app")
    env["CHAD_AIRLINE_OUT_DIR"] = str(out_dir)
    env["CHAD_AIRLINE_RUN_ID"] = run_id
    env["CHAD_AIRLINE_FLIGHTS"] = str(flights)
    env["CHAD_AIRLINE_TICKETS_PER_FLIGHT"] = str(tickets_per_flight)
    if seed is not None:
        env["CHAD_AIRLINE_SEED"] = str(seed)
    return env


def _write_run_metadata(run_dir: Path, *, run_id: str, flights: int, tickets_per_flight: int, seed: int | None) -> None:
    ensure_dir(run_dir)
    meta = run_dir / "RUN_METADATA.txt"
    lines = [
        "CHAD-AIRLINE RUN METADATA",
        f"time_utc={utc_now_str()}",
        f"run_id={run_id}",
        f"flights={flights}",
        f"tickets_per_flight={tickets_per_flight}",
        f"seed={seed if seed is not None else ''}",
        "",
        "env_keys:",
        " - CHAD_AIRLINE_OUT_DIR",
        " - CHAD_AIRLINE_RUN_ID",
        " - CHAD_AIRLINE_FLIGHTS",
        " - CHAD_AIRLINE_TICKETS_PER_FLIGHT",
        " - CHAD_AIRLINE_SEED (optional)",
        "",
        "IMPORTANT:",
        " - Scripts run with cwd=/app (repo root) for stable relative reads.",
        " - logs_monte_carlo_dashboard/ is symlinked into the mounted run dir for stable outputs.",
        " - Charts are generated by run_full_pipeline into dashboard/images/ for CEO PDF embedding.",
        "",
    ]
    meta.write_text("\n".join(lines), encoding="utf-8")


def _safe_save(fig, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_dashboard_charts(dashboard_dir: Path, *, log_file: Path | None = None) -> int:
    """
    PRO: Guaranteed chart generation from the CSVs that already exist in dashboard/.
    Writes into dashboard/images/*.png so CEO PDF can embed them.
    Returns number of pngs created.
    """
    images_dir = dashboard_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    created = 0

    def log(msg: str) -> None:
        print(msg)
        if log_file is not None:
            _append_log(log_file, "\n" + msg + "\n")

    # ---- Chart 1: Mean revenue by flight/class from airline_risk_report.csv
    risk_csv = dashboard_dir / "airline_risk_report.csv"
    if risk_csv.exists():
        try:
            df = pd.read_csv(risk_csv)
            if {"flight", "class", "mean_revenue"}.issubset(df.columns):
                pivot = df.pivot(index="flight", columns="class", values="mean_revenue")
                fig = plt.figure(figsize=(11, 5))
                ax = fig.add_subplot(111)
                pivot.plot(kind="bar", ax=ax)
                ax.set_title("Mean Revenue by Flight and Cabin Class")
                ax.set_xlabel("Flight")
                ax.set_ylabel("Mean Revenue")
                out = images_dir / "01_mean_revenue_by_flight_class.png"
                _safe_save(fig, out)
                created += 1
                log(f"🖼️ saved: {out}")
        except Exception as e:
            log(f"⚠️ chart failed (mean revenue): {e}")

    # ---- Chart 2: Probability of loss by flight/class
    pol_csv = dashboard_dir / "probability_of_loss_report.csv"
    if pol_csv.exists():
        try:
            df = pd.read_csv(pol_csv)
            if {"flight", "class", "probability_of_loss"}.issubset(df.columns):
                pivot = df.pivot(index="flight", columns="class", values="probability_of_loss")
                fig = plt.figure(figsize=(11, 5))
                ax = fig.add_subplot(111)
                pivot.plot(kind="bar", ax=ax)
                ax.set_title("Probability of Loss by Flight and Cabin Class")
                ax.set_xlabel("Flight")
                ax.set_ylabel("Probability of Loss")
                out = images_dir / "02_probability_of_loss_by_flight_class.png"
                _safe_save(fig, out)
                created += 1
                log(f"🖼️ saved: {out}")
        except Exception as e:
            log(f"⚠️ chart failed (probability of loss): {e}")

    # ---- Chart 3: RAROC by flight/class
    raroc_csv = dashboard_dir / "airline_raroc_report.csv"
    if raroc_csv.exists():
        try:
            df = pd.read_csv(raroc_csv)
            if {"flight", "class", "RAROC"}.issubset(df.columns):
                pivot = df.pivot(index="flight", columns="class", values="RAROC")
                fig = plt.figure(figsize=(11, 5))
                ax = fig.add_subplot(111)
                pivot.plot(kind="bar", ax=ax)
                ax.set_title("RAROC by Flight and Cabin Class")
                ax.set_xlabel("Flight")
                ax.set_ylabel("RAROC")
                out = images_dir / "03_raroc_by_flight_class.png"
                _safe_save(fig, out)
                created += 1
                log(f"🖼️ saved: {out}")
        except Exception as e:
            log(f"⚠️ chart failed (RAROC): {e}")

    # ---- Chart 4: Board decisions distribution
    board_csv = dashboard_dir / "airline_board_decisions.csv"
    if board_csv.exists():
        try:
            df = pd.read_csv(board_csv)
            if "board_decision" in df.columns:
                counts = df["board_decision"].value_counts().sort_index()
                fig = plt.figure(figsize=(9, 4.5))
                ax = fig.add_subplot(111)
                counts.plot(kind="bar", ax=ax)
                ax.set_title("Board Decision Distribution")
                ax.set_xlabel("Decision")
                ax.set_ylabel("Count")
                out = images_dir / "04_board_decision_distribution.png"
                _safe_save(fig, out)
                created += 1
                log(f"🖼️ saved: {out}")
        except Exception as e:
            log(f"⚠️ chart failed (board decisions): {e}")

    # ---- Chart 5: Fleet actions distribution
    exec_csv = dashboard_dir / "airline_execution_plan.csv"
    if exec_csv.exists():
        try:
            df = pd.read_csv(exec_csv)
            if "fleet_action" in df.columns:
                counts = df["fleet_action"].value_counts().sort_index()
                fig = plt.figure(figsize=(9, 4.5))
                ax = fig.add_subplot(111)
                counts.plot(kind="bar", ax=ax)
                ax.set_title("Fleet Action Distribution")
                ax.set_xlabel("Fleet Action")
                ax.set_ylabel("Count")
                out = images_dir / "05_fleet_action_distribution.png"
                _safe_save(fig, out)
                created += 1
                log(f"🖼️ saved: {out}")
        except Exception as e:
            log(f"⚠️ chart failed (fleet actions): {e}")

    log(f"🖼️ charts_created={created} (dashboard/images)")
    return created


def main() -> int:
    ap = argparse.ArgumentParser(prog="run_full_pipeline")
    ap.add_argument("--out", required=True, help="Base output directory (mounted volume).")
    ap.add_argument("--run-id", required=True, help="Run ID (created by cli if not provided).")
    ap.add_argument("--flights", type=int, default=10)
    ap.add_argument("--tickets-per-flight", type=int, default=5)
    ap.add_argument("--seed", type=int, default=None, help="Optional deterministic seed (exported via env).")

    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail non-zero if required artifacts look like placeholders/small files.",
    )

    args = ap.parse_args()

    out_base = Path(args.out)
    run_id = args.run_id
    flights = int(args.flights)
    tpf = int(args.tickets_per_flight)
    seed = args.seed if args.seed is None else int(args.seed)

    run_dir = out_base / run_id
    dashboard_dir = run_dir / "dashboard"
    reports_dir = run_dir / "reports"
    legacy_dir = run_dir / "logs_monte_carlo_dashboard"  # artifacts produced by scripts today

    ensure_dir(run_dir)
    ensure_dir(dashboard_dir)
    ensure_dir(reports_dir)
    ensure_dir(legacy_dir)

    debug_log = run_dir / "pipeline_debug.log"

    # Symlink logs folder into mounted volume
    ensure_symlink(repo_root() / "logs_monte_carlo_dashboard", legacy_dir, log_file=debug_log)

    env = _env_for_run(out_dir=run_dir, run_id=run_id, flights=flights, tickets_per_flight=tpf, seed=seed)

    print("\n🚀 CHAD-AIRLINE FULL PIPELINE")
    print(f"🕒 Time : {utc_now_str()}")
    print(f"🆔 Run ID: {run_id}")
    print(f"📁 Run dir: {run_dir}")
    print(f"📊 Dashboard: {dashboard_dir}")
    print(f"📄 Reports: {reports_dir}")
    print(f"🧾 Legacy dir (real): {legacy_dir}")
    print(f"🧾 Debug log: {debug_log}")

    _write_run_metadata(run_dir, run_id=run_id, flights=flights, tickets_per_flight=tpf, seed=seed)

    pipeline = [
        "simulations/ticket_lifecycle_simulator.py",
        "simulations/monte_carlo_kpi_dashboard.py",
        "simulations/airline_risk_engine.py",
        "simulations/probability_of_loss_engine.py",
        "simulations/airline_raroc_engine.py",
        "simulations/airline_stress_test_engine.py",
        "simulations/airline_board_decision_engine.py",
        "simulations/airline_execution_engine.py",
        "simulations/airline_decision_explainability_engine.py",
    ]

    rc_any = 0
    for script in pipeline:
        rc = run_script(script, env=env, cwd=repo_root(), log_file=debug_log)
        if rc != 0:
            rc_any = rc_any or rc
            print(f"⚠️ {Path(script).name} failed — continuing (sellable mode). See {debug_log}")

    # Copy required CSVs from legacy into dashboard
    copied = 0
    for csv_name in ALL_REQUIRED:
        src = legacy_dir / csv_name
        dst = dashboard_dir / csv_name
        if copy_if_exists(src, dst):
            copied += 1

    # Copy any PDFs already present
    for pdf in reports_dir.glob("*.pdf"):
        if copy_if_exists(pdf, dashboard_dir / pdf.name):
            copied += 1

    print(f"✅ Copied {copied} report file(s) into dashboard/")

    # Ensure CSVs exist and readable (placeholders if needed)
    write_or_repair_placeholders(dashboard_dir)

    # ✅ GUARANTEED charts from dashboard CSVs
    print("\n📊 Generating charts into dashboard/images/ ...\n")
    charts_created = generate_dashboard_charts(dashboard_dir, log_file=debug_log)

    # CEO PDF generation (must pass args)
    print("\n🧾 Generating CEO PDF...\n")
    rc_pdf = run_script(
        "simulations/airline_ceo_pdf_report.py",
        env=env,
        cwd=repo_root(),
        extra_args=["--dashboard", str(dashboard_dir), "--out", str(reports_dir)],
        log_file=debug_log,
    )
    if rc_pdf != 0:
        print(f"⚠️ CEO PDF generator failed — continuing (sellable mode). See {debug_log}")

    # After PDF, copy again if created
    for pdf in reports_dir.glob("*.pdf"):
        copy_if_exists(pdf, dashboard_dir / pdf.name)

    # Artifact Summary + strict validation
    print("\n📦 RUN ARTIFACT SUMMARY")
    problems: list[str] = []

    for name in ALL_REQUIRED:
        f = dashboard_dir / name
        rows = csv_rowcount(f) if f.exists() else 0
        status = "OK" if rows > 10 else "PLACEHOLDER/SMALL"
        print(f" - {name:<35} rows={rows:<6} status={status}")
        if args.strict and rows <= 10:
            problems.append(f"{name} has only {rows} rows (expected > 10)")

    pdf_path = reports_dir / "EXECUTIVE_REPORT.pdf"
    if pdf_path.exists() and pdf_path.stat().st_size > 1000:
        print(" - EXECUTIVE_REPORT.pdf                     status=OK")
    else:
        print(" - EXECUTIVE_REPORT.pdf                     status=MISSING/SMALL")
        if args.strict:
            problems.append("EXECUTIVE_REPORT.pdf missing/small")

    # Strict also requires charts (professional)
    if args.strict and charts_created <= 0:
        problems.append("No charts were generated into dashboard/images/")

    if problems:
        print("\n❌ STRICT VALIDATION FAILED")
        for p in problems:
            print(f" - {p}")
        print(f"\n🧾 Debug: {debug_log}")
        return 2

    print("\n✅ RUN COMPLETED (charts embedded-ready)")
    print(f"🖼️ dashboard/images pngs = {charts_created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
