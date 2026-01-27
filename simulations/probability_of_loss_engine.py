import math
import pandas as pd

INPUT_CSV = "logs_monte_carlo_dashboard/airline_risk_report.csv"
OUTPUT_CSV = "logs_monte_carlo_dashboard/probability_of_loss_report.csv"

# ---------- NORMAL DISTRIBUTION (NO SCIPY) ----------

def normal_cdf(x: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0 if x < mean else 1.0
    z = (x - mean) / (std * math.sqrt(2))
    return 0.5 * (1 + math.erf(z))


def probability_of_loss(mean_revenue: float, revenue_std: float, cost: float) -> float:
    """
    P(Revenue < Cost)
    """
    return normal_cdf(cost, mean_revenue, revenue_std)


# ---------- MAIN ENGINE ----------

def main():
    df = pd.read_csv(INPUT_CSV)

    COST_RATIO = 0.85  # 85% of mean revenue assumed as operating cost
    results = []

    for _, row in df.iterrows():
        cost = row["mean_revenue"] * COST_RATIO
        p_loss = probability_of_loss(
            mean_revenue=row["mean_revenue"],
            revenue_std=row["revenue_std"],
            cost=cost,
        )

        risk_level = (
            "SAFE" if p_loss < 0.05 else
            "WARNING" if p_loss < 0.15 else
            "CRITICAL"
        )

        results.append({
            "flight": row["flight"],
            "class": row["class"],
            "mean_revenue": row["mean_revenue"],
            "revenue_std": row["revenue_std"],
            "probability_of_loss": round(p_loss, 4),
            "risk_level": risk_level,
        })

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_CSV, index=False)

    print("\n📊 PROBABILITY OF LOSS REPORT\n")
    print(out_df)
    print(f"\n✅ Report saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
