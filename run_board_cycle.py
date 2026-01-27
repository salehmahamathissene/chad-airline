import subprocess

PIPELINE = [
    "simulations/monte_carlo_kpi_dashboard.py",
    "simulations/airline_risk_engine.py",
    "simulations/probability_of_loss_engine.py",
    "simulations/airline_raroc_engine.py",
    "simulations/airline_stress_test_engine.py",
    "simulations/airline_board_decision_engine.py",
    "simulations/airline_execution_plan_engine.py",
    "simulations/airline_capital_allocation_engine.py",
    "simulations/airline_execution_interface.py",
    "simulations/airline_ceo_pdf_report.py",
    "simulations/airline_audit_trail_engine.py"
]


def main():
    print("\n🏛 AIRLINE BOARD STRATEGIC CYCLE STARTED\n")

    for step in PIPELINE:
        print(f"▶ RUNNING: {step}")
        subprocess.run(["python", step], check=True)

    print("\n✅ BOARD CYCLE COMPLETE — CEO READY")


if __name__ == "__main__":
    main()
