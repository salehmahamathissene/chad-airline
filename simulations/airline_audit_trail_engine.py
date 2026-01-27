import hashlib
from pathlib import Path
import datetime

FILES_TO_AUDIT = [
    "airline_risk_report.csv",
    "probability_of_loss_report.csv",
    "airline_raroc_report.csv",
    "airline_stress_test_report.csv",
    "airline_board_decisions.csv",
    "airline_execution_plan.csv"
]

BASE_DIR = Path("logs_monte_carlo_dashboard")
OUTPUT_FILE = BASE_DIR / "airline_audit_trail.log"


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def main():
    print("\n🛡 AIRLINE REGULATORY AUDIT TRAIL\n")

    with open(OUTPUT_FILE, "w") as audit:
        audit.write(f"AUDIT TIMESTAMP: {datetime.datetime.utcnow()}\n\n")

        for fname in FILES_TO_AUDIT:
            fpath = BASE_DIR / fname
            if fpath.exists():
                audit.write(f"{fname} | SHA256: {file_hash(fpath)}\n")

    print(f"✅ AUDIT TRAIL CREATED: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
