import pandas as pd
from pathlib import Path

INPUT_FILE = Path("logs_monte_carlo_dashboard/airline_execution_plan.csv")
OUTPUT_FILE = Path("logs_monte_carlo_dashboard/airline_execution_instructions.csv")


def generate_instruction(row):
    return f"{row['flight']} ({row['class']}): {row['status']}, " \
           f"Freq {row['frequency_change']}, Price {row['pricing_action']}, Fleet {row['fleet_action']}"


def main():
    print("\n🔗 AIRLINE EXECUTION INTERFACE ENGINE\n")

    df = pd.read_csv(INPUT_FILE)

    df["instruction"] = df.apply(generate_instruction, axis=1)

    instructions_df = df[["flight", "class", "board_decision", "instruction"]]

    print(instructions_df)

    instructions_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ EXECUTION INSTRUCTIONS SAVED: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
