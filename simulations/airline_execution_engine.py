import pandas as pd
from pathlib import Path

INPUT_FILE = Path("logs_monte_carlo_dashboard/airline_board_decisions.csv")
OUTPUT_FILE = Path("logs_monte_carlo_dashboard/airline_execution_plan.csv")


def execution_action(decision):
    if decision == "EXPAND":
        return {
            "frequency_change": "+15%",
            "pricing_action": "INCREASE",
            "fleet_action": "UPGAUGE",
            "status": "ACTIVE"
        }

    if decision == "MAINTAIN":
        return {
            "frequency_change": "0%",
            "pricing_action": "HOLD",
            "fleet_action": "NO CHANGE",
            "status": "ACTIVE"
        }

    if decision == "RESTRUCTURE":
        return {
            "frequency_change": "-20%",
            "pricing_action": "DISCOUNT",
            "fleet_action": "DOWNGAUGE",
            "status": "ACTIVE"
        }

    if decision == "EXIT":
        return {
            "frequency_change": "-100%",
            "pricing_action": "N/A",
            "fleet_action": "REMOVE CABIN",
            "status": "SUSPENDED"
        }

    if decision == "GROUND IMMEDIATELY":
        return {
            "frequency_change": "-100%",
            "pricing_action": "STOP SALES",
            "fleet_action": "GROUND AIRCRAFT",
            "status": "GROUND"
        }


def main():
    print("\n🛫 AIRLINE EXECUTION ENGINE\n")

    df = pd.read_csv(INPUT_FILE)

    actions = df["board_decision"].apply(execution_action)
    actions_df = pd.DataFrame(actions.tolist())

    final_df = pd.concat([df, actions_df], axis=1)

    print(final_df[[
        "flight",
        "class",
        "board_decision",
        "frequency_change",
        "pricing_action",
        "fleet_action",
        "status"
    ]])

    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ EXECUTION PLAN SAVED: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
