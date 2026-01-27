from __future__ import annotations

import argparse
import json
import os
import sys
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

VERSION = "1.0.0"


# ---------------------------
# Utilities
# ---------------------------

def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def is_tty() -> bool:
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def colorize(s: str, code: str, *, enable: bool) -> str:
    if not enable:
        return s
    return f"\033[{code}m{s}\033[0m"


def ok(s: str, *, color: bool) -> str:
    return colorize(s, "32", enable=color)  # green


def warn(s: str, *, color: bool) -> str:
    return colorize(s, "33", enable=color)  # yellow


def err(s: str, *, color: bool) -> str:
    return colorize(s, "31", enable=color)  # red


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def csv_rows(path: Path) -> int:
    """
    Count CSV rows excluding header. Returns 0 if file missing/unreadable.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        return max(0, lines - 1)
    except Exception:
        return 0


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    issues: list[str]
    summary: dict[str, object]


def strict_validate(run_dir: Path, *, min_rows: int = 10) -> ValidationResult:
    """
    Professional validation:
    - CEO PDF exists and is not tiny
    - key CSVs exist and have > min_rows rows
    """
    dashboard = run_dir / "dashboard"
    reports = run_dir / "reports"
    pdf = reports / "EXECUTIVE_REPORT.pdf"

    required_csvs = [
        "airline_risk_report.csv",
        "probability_of_loss_report.csv",
        "airline_raroc_report.csv",
        "airline_stress_test_report.csv",
        "airline_board_decisions.csv",
        "airline_execution_plan.csv",
        "airline_decision_explainability_report.csv",
    ]

    issues: list[str] = []
    per_file: dict[str, dict[str, object]] = {}

    # PDF checks
    if not pdf.exists():
        issues.append("Missing EXECUTIVE_REPORT.pdf")
        per_file["EXECUTIVE_REPORT.pdf"] = {"exists": False, "size_bytes": 0}
    else:
        try:
            size = int(pdf.stat().st_size)
            per_file["EXECUTIVE_REPORT.pdf"] = {"exists": True, "size_bytes": size}
            if size < 1000:
                issues.append("EXECUTIVE_REPORT.pdf is too small (likely failed/empty)")
        except Exception:
            issues.append("EXECUTIVE_REPORT.pdf stat failed")
            per_file["EXECUTIVE_REPORT.pdf"] = {"exists": True, "size_bytes": None}

    # CSV checks
    for name in required_csvs:
        p = dashboard / name
        if not p.exists():
            issues.append(f"Missing {name}")
            per_file[name] = {"exists": False, "rows": 0}
            continue

        rows = csv_rows(p)
        per_file[name] = {"exists": True, "rows": rows}
        if rows <= min_rows:
            issues.append(f"{name} has only {rows} rows (expected > {min_rows})")

    summary = {
        "run_dir": str(run_dir),
        "min_rows": min_rows,
        "files": per_file,
    }
    return ValidationResult(ok=(len(issues) == 0), issues=issues, summary=summary)


# ---------------------------
# Process execution (PRO)
# ---------------------------

def iter_stream_lines(stream) -> Iterable[str]:
    """
    Iterates lines from a stream (bytes/str safe) without buffering everything.
    """
    for raw in stream:
        if isinstance(raw, bytes):
            yield raw.decode(errors="replace")
        else:
            yield str(raw)


def run_process(
    cmd: list[str],
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
    verbose: bool,
    tee_path: Path | None,
) -> int:
    """
    Run child process. Quiet by default:
    - In quiet mode, only prints key lines (✅, ❌, ⚠️, 🚀, 📦, 📁, ▶)
    - In verbose mode, streams everything.
    - If tee_path is provided, writes full output to that file (always).
    """
    ensure_dir(tee_path.parent) if tee_path else None

    # Start process
    p = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    keep_prefixes = ("✅", "❌", "⚠️", "🚀", "📦", "📁", "▶", "🧾", "📊", "📄", "🆔", "🕒")
    tee_fh = tee_path.open("w", encoding="utf-8") if tee_path else None

    try:
        assert p.stdout is not None
        for line in iter_stream_lines(p.stdout):
            if tee_fh:
                tee_fh.write(line)
                tee_fh.flush()

            if verbose:
                print(line, end="")
            else:
                s = line.lstrip()
                if s.startswith(keep_prefixes):
                    print(line, end="")

        return int(p.wait())
    finally:
        if tee_fh:
            tee_fh.close()


# ---------------------------
# CLI
# ---------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chad-airline-engine",
        description="CHAD-AIRLINE Simulation Engine — Monte Carlo → Risk → Board → Execution → CEO PDF",
    )
    p.add_argument("--version", action="store_true", help="Print version and exit.")
    p.add_argument("--json", action="store_true", help="Machine-readable output (validation + paths).")
    p.add_argument("--verbose", action="store_true", help="Stream full child output (no filtering).")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    p.add_argument(
        "--tee-log",
        type=str,
        default=None,
        help="Write full pipeline output to a log file (useful for audit).",
    )

    sub = p.add_subparsers(dest="cmd")

    # run
    run = sub.add_parser("run", help="Run the full pipeline and generate dashboard + CEO PDF.")
    run.add_argument("--flights", type=int, default=10)
    run.add_argument("--tickets-per-flight", type=int, default=5)
    run.add_argument("--out", type=str, default="./out", help="Host output directory.")
    run.add_argument("--run-id", type=str, default=None, help="Default: UTC timestamp.")
    run.add_argument("--seed", type=int, default=None, help="Optional deterministic seed (forwarded).")
    run.add_argument(
        "--strict",
        action="store_true",
        help="Fail (non-zero) if outputs look like placeholders/small files.",
    )
    run.add_argument("--min-rows", type=int, default=10, help="Strict validation: minimum CSV rows.")

    # smoke-test
    sm = sub.add_parser("smoke-test", help="Fast validation run to verify artifacts are real.")
    sm.add_argument("--out", type=str, default="./out")
    sm.add_argument("--run-id", type=str, default=None)
    sm.add_argument("--seed", type=int, default=123)
    sm.add_argument("--min-rows", type=int, default=10, help="Minimum expected CSV rows (excluding header).")

    return p


def build_run_full_pipeline_cmd(
    *,
    out_dir: Path,
    run_id: str,
    flights: int,
    tickets_per_flight: int,
    seed: int | None,
    strict: bool,
) -> list[str]:
    cmd = [
        sys.executable,
        "simulations/run_full_pipeline.py",
        "--out",
        str(out_dir),
        "--run-id",
        run_id,
        "--flights",
        str(flights),
        "--tickets-per-flight",
        str(tickets_per_flight),
    ]
    if seed is not None:
        cmd += ["--seed", str(seed)]
    if strict:
        cmd += ["--strict"]
    return cmd


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    color = (not args.no_color) and is_tty()

    if args.version:
        print(f"chad-airline-engine {VERSION}")
        return 0

    cmd = args.cmd or "run"

    # Normalize output root
    out_dir = Path(getattr(args, "out", "./out")).expanduser()
    run_id = getattr(args, "run_id", None) or utc_run_id()
    run_dir = out_dir.resolve() / run_id

    # Tee log path
    tee_path = Path(args.tee_log).expanduser() if args.tee_log else None
    if tee_path is None:
        # Default: store an audit log inside run_dir (nice for customers)
        tee_path = run_dir / "pipeline.log"

    # Header
    if not args.json:
        print(ok("🚀 CHAD-AIRLINE ENGINE", color=color))
        print(f"🕒 Time  : {utc_now_str()}")
        print(f"🆔 Run ID: {run_id}")
        print(f"📁 Out   : {run_dir}")
        print(f"🧾 Log   : {tee_path}")

    # Command selection
    if cmd == "run":
        strict_flag = bool(getattr(args, "strict", False))

        proc_cmd = build_run_full_pipeline_cmd(
            out_dir=out_dir,
            run_id=run_id,
            flights=int(args.flights),
            tickets_per_flight=int(args.tickets_per_flight),
            seed=args.seed,
            strict=strict_flag,
        )

        if not args.json:
            print(f"▶ Running: {' '.join(proc_cmd)}")

        # Run pipeline (quiet by default)
        rc = run_process(
            proc_cmd,
            cwd=Path("."),
            env=os.environ.copy(),
            verbose=bool(args.verbose),
            tee_path=tee_path,
        )

        # Optional strict validation at CLI level as well (belt + suspenders)
        exit_code = rc
        validation = None
        if strict_flag:
            validation = strict_validate(run_dir, min_rows=int(args.min_rows))
            if not validation.ok:
                exit_code = 2

        if args.json:
            payload = {
                "tool": "chad-airline-engine",
                "version": VERSION,
                "cmd": "run",
                "time_utc": utc_now_str(),
                "run_id": run_id,
                "out_dir": str(out_dir.resolve()),
                "run_dir": str(run_dir),
                "pipeline_rc": rc,
                "exit_code": exit_code,
                "strict": strict_flag,
                "validation": validation.summary if validation else None,
                "issues": validation.issues if validation else [],
                "log": str(tee_path),
            }
            print(json.dumps(payload, indent=2))
            return int(exit_code)

        # Human output
        if strict_flag and validation is not None and not validation.ok:
            print()
            print(err("❌ STRICT VALIDATION FAILED", color=color))
            for i in validation.issues:
                print(f" - {i}")
            print(f"\n📁 {run_dir}")
            print(f"🧾 {tee_path}")
            return 2

        if rc != 0:
            print()
            print(warn(f"⚠️ Pipeline exited rc={rc}. Check log: {tee_path}", color=color))
            print(f"📁 {run_dir}")
            return int(exit_code)

        print()
        print(ok("✅ RUN COMPLETED", color=color))
        print(f"📁 {run_dir}")
        print(f"🧾 {tee_path}")
        return int(exit_code)

    if cmd == "smoke-test":
        # Fast, deterministic, minimal workload
        proc_cmd = build_run_full_pipeline_cmd(
            out_dir=out_dir,
            run_id=run_id,
            flights=2,
            tickets_per_flight=2,
            seed=int(args.seed),
            strict=False,  # do not rely on pipeline strict here; validate ourselves
        )

        if not args.json:
            print(f"▶ Running: {' '.join(proc_cmd)}")

        rc = run_process(
            proc_cmd,
            cwd=Path("."),
            env=os.environ.copy(),
            verbose=bool(args.verbose),
            tee_path=tee_path,
        )

        validation = strict_validate(run_dir, min_rows=int(args.min_rows))
        ok_smoke = validation.ok

        if args.json:
            payload = {
                "tool": "chad-airline-engine",
                "version": VERSION,
                "cmd": "smoke-test",
                "time_utc": utc_now_str(),
                "run_id": run_id,
                "out_dir": str(out_dir.resolve()),
                "run_dir": str(run_dir),
                "pipeline_rc": rc,
                "ok": ok_smoke,
                "exit_code": 0 if ok_smoke else 2,
                "validation": validation.summary,
                "issues": validation.issues,
                "log": str(tee_path),
            }
            print(json.dumps(payload, indent=2))
            return 0 if ok_smoke else 2

        if ok_smoke:
            print()
            print(ok("✅ SMOKE TEST PASSED", color=color))
            print(f"📁 {run_dir}")
            print(f"🧾 {tee_path}")
            return 0

        print()
        print(err("❌ SMOKE TEST FAILED", color=color))
        for i in validation.issues:
            print(f" - {i}")
        print(f"\n📁 {run_dir}")
        print(f"🧾 {tee_path}")
        return 2

    eprint("Unknown command. Use: run | smoke-test | --version")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
