from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SyntheticConfig:
    n_customers: int = 200
    start_date: str = "2026-01-01"
    months: int = 6
    seed: int = 42


RECURRING_CATALOG = [
    ("Rent / Mortgage", "housing", 850.0, 30, 0.03),
    ("Electricity", "utilities", 78.0, 30, 0.15),
    ("Broadband", "utilities", 32.0, 30, 0.02),
    ("Mobile Plan", "utilities", 24.0, 30, 0.02),
    ("Video Streaming", "subscription", 10.99, 30, 0.00),
    ("Music Streaming", "subscription", 10.99, 30, 0.00),
    ("Gym", "subscription", 29.99, 30, 0.00),
    ("Cloud Storage", "subscription", 2.99, 30, 0.00),
]

DISCRETIONARY = [
    ("Supermarket", "groceries", 42.0, 0.55),
    ("Coffee Shop", "eating_out", 5.0, 0.55),
    ("Restaurant", "eating_out", 28.0, 0.60),
    ("Online Retailer", "shopping", 35.0, 0.80),
    ("Fuel", "transport", 48.0, 0.35),
    ("Rail", "transport", 18.0, 0.50),
]


def _month_starts(start: pd.Timestamp, months: int) -> list[pd.Timestamp]:
    return [start + pd.DateOffset(months=i) for i in range(months)]


def generate_transactions(config: SyntheticConfig = SyntheticConfig()) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)
    start = pd.Timestamp(config.start_date)
    rows: list[dict] = []

    for cid in range(1, config.n_customers + 1):
        customer_id = f"C{cid:04d}"
        salary = float(rng.normal(2600, 450))
        salary = max(salary, 1600)
        payday = int(rng.integers(24, 29))
        chosen = rng.choice(len(RECURRING_CATALOG), size=int(rng.integers(4, 8)), replace=False)

        # salary income
        for ms in _month_starts(start, config.months):
            day = min(payday, (ms + pd.offsets.MonthEnd(0)).day)
            rows.append({
                "customer_id": customer_id,
                "date": pd.Timestamp(ms.year, ms.month, day),
                "merchant": "Employer Payroll",
                "category": "income",
                "amount": round(salary + rng.normal(0, 12), 2),
                "direction": "credit",
                "is_true_recurring": True,
            })

        # recurring bills/subscriptions
        for idx in chosen:
            merchant, category, base_amount, interval, variability = RECURRING_CATALOG[idx]
            base_day = int(rng.integers(1, 23))
            cancelled_after = int(rng.integers(3, config.months + 1)) if rng.random() < 0.10 else config.months
            for m, ms in enumerate(_month_starts(start, config.months)):
                if m >= cancelled_after:
                    break
                # small payment-date shifts mimic weekends/merchant processing
                day_shift = int(rng.integers(-2, 3))
                day = min(max(base_day + day_shift, 1), (ms + pd.offsets.MonthEnd(0)).day)
                amount = base_amount * (1 + rng.normal(0, variability))
                rows.append({
                    "customer_id": customer_id,
                    "date": pd.Timestamp(ms.year, ms.month, day),
                    "merchant": merchant,
                    "category": category,
                    "amount": round(abs(amount), 2),
                    "direction": "debit",
                    "is_true_recurring": True,
                })

        # discretionary spending
        end = start + pd.DateOffset(months=config.months) - pd.Timedelta(days=1)
        total_days = (end - start).days + 1
        n_random = int(rng.integers(95, 150))
        for _ in range(n_random):
            merchant, category, mean_amount, variability = DISCRETIONARY[int(rng.integers(0, len(DISCRETIONARY)))]
            dt = start + pd.Timedelta(days=int(rng.integers(0, total_days)))
            amount = max(1.0, rng.lognormal(np.log(mean_amount), variability))
            rows.append({
                "customer_id": customer_id,
                "date": dt,
                "merchant": merchant,
                "category": category,
                "amount": round(amount, 2),
                "direction": "debit",
                "is_true_recurring": False,
            })

    df = pd.DataFrame(rows).sort_values(["customer_id", "date", "merchant"]).reset_index(drop=True)
    return df


def save_transactions(path: str | Path, config: SyntheticConfig = SyntheticConfig()) -> pd.DataFrame:
    df = generate_transactions(config)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    out = Path(__file__).resolve().parents[1] / "data" / "synthetic_transactions.csv"
    df = save_transactions(out)
    print(f"wrote {len(df):,} rows to {out}")
