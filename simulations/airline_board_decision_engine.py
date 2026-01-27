#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path("logs_monte_carlo_dashboard")

RISK_FILE = BASE_DIR / "airline_risk_report.csv"
LOSS_FILE = BASE_DIR / "probability_of_loss_report.csv"
RAROC_FILE = BASE_DIR / "airline_raroc_report.csv"
STRESS_FILE = BASE_DIR / "airline_stress_test_report.csv"
OUTPUT_FILE = BASE_DIR / "airline_board_decisions.csv"


def require_file(p: Path) -> None:
    if not p.exists():
        raise FileNotFoundError(f"Required input missing: {p}")


def pick_existing(df: pd.DataFrame, cols: list[str]) -> list[str]:
    """Return only columns that actually exist in df, preserving order."""
    return [c for c in cols if c in df.columns]


def board_decision(row: pd.Series) -> str:
    """
    Final airline board decision logic (audit-friendly).
    """
    survival = str(row.get("survival", "SURVIVES"))
    prob_loss = float(row.get("probability_of_loss", 0.0))
    raroc = float(row.get("RAROC", 0.0))

    # Extreme risk override
    if survival == "FAILS" and prob_loss > 0.05:
        return "GROUND IMMEDIATELY"

    # Growth decision
    if raroc >= 1.30 and survival == "SURVIVES":
        return "EXPAND"

    # Standard decisions
    if raroc >= 1.20:
        return "MAINTAIN"

    if raroc >= 1.10:
        return "RESTRUCTURE"

    return "EXIT"


def main() -> None:
    print("\n🏛️ AIRLINE BOARD DECISION ENGINE\n")

    for p in [RISK_FILE, LOSS_FILE, RAROC_FILE, STRESS_FILE]:
        require_file(p)

    risk_df = pd.read_csv(RISK_FILE)
    loss_df = pd.read_csv(LOSS_FILE)
    raroc_df = pd.read_csv(RAROC_FILE)
    stress_df = pd.read_csv(STRESS_FILE)

    # Minimum required keys
    for name, df, required in [
        ("risk", risk_df, {"flight", "class"}),
        ("loss", loss_df, {"flight", "class", "probability_of_loss"}),
        ("raroc", raroc_df, {"flight", "class", "RAROC"}),
        ("stress", stress_df, {"flight", "class", "stressed_raroc", "survival"}),
    ]:
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"{name} report missing columns: {sorted(missing)}")

    # Worst-case stress per flight/class (lowest stressed_raroc)
    stress_df = (
        stress_df.sort_values("stressed_raroc", ascending=True)
        .groupby(["flight", "class"], as_index=False)
        .first()
    )

    # --- Build merged dataset (schema-adaptive) ---
    # Risk report may have different schemas. We bring keys + any useful numeric fields if present.
    risk_keep = pick_existing(
        risk_df,
        [
            "flight",
            "class",
            "mean_revenue",
            "revenue_std",
            "ci_lower_95",
            "ci_upper_95",
            "VaR_95",
            "CVaR_95",
        ],
    )
    risk_min = risk_df[risk_keep].copy()

    loss_keep = pick_existing(
        loss_df,
        ["flight", "class", "probability_of_loss", "risk_level", "mean_revenue", "revenue_std"],
    )
    loss_min = loss_df[loss_keep].copy()

    raroc_keep = pick_existing(
        raroc_df,
        ["flight", "class", "RAROC", "decision"],
    )
    raroc_min = raroc_df[raroc_keep].copy()

    stress_keep = pick_existing(
        stress_df,
        ["flight", "class", "stressed_raroc", "stress_multiplier", "survival"],
    )
    stress_min = stress_df[stress_keep].copy()

    # Merge, keeping everything we can without causing suffix chaos
    df = (
        risk_min.merge(loss_min, on=["flight", "class"], how="inner", suffixes=("", "_loss"))
        .merge(raroc_min, on=["flight", "class"], how="inner")
        .merge(stress_min, on=["flight", "class"], how="inner")
    )

    # If mean_revenue/revenue_std are missing in df (depends on upstream schemas),
    # try to recover from any suffixed columns we pulled.
    if "mean_revenue" not in df.columns:
        for alt in ["mean_revenue_loss"]:
            if alt in df.columns:
                df["mean_revenue"] = df[alt]
                break

    if "revenue_std" not in df.columns:
        for alt in ["revenue_std_loss"]:
            if alt in df.columns:
                df["revenue_std"] = df[alt]
                break

    # Compute decision
    df["board_decision"] = df.apply(board_decision, axis=1)

    # Professional stable ordering
    order = {"GROUND IMMEDIATELY": 0, "EXPAND": 1, "MAINTAIN": 2, "RESTRUCTURE": 3, "EXIT": 4}
    df["_rank"] = df["board_decision"].map(order).fillna(99).astype(int)

    df = df.sort_values(
        ["_rank", "RAROC", "probability_of_loss"],
        ascending=[True, False, True],
    ).drop(columns=["_rank"])

    # Final client-ready columns (only include ones that exist)
    out_cols = pick_existing(
        df,
        [
            "flight",
            "class",
            "RAROC",
            "decision",
            "probability_of_loss",
            "risk_level",
            "mean_revenue",
            "revenue_std",
            "ci_lower_95",
            "ci_upper_95",
            "VaR_95",
            "CVaR_95",
            "stress_multiplier",
            "stressed_raroc",
            "survival",
            "board_decision",
        ],
    )

    out_df = df[out_cols].copy()

    BASE_DIR.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_FILE, index=False)

    print(out_df.head(30))
    print(f"\n✅ BOARD DECISIONS SAVED: {OUTPUT_FILE}  (rows={len(out_df)})")


if __name__ == "__main__":
    main()
