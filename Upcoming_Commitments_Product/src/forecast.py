from __future__ import annotations

import pandas as pd


def upcoming_commitments(predictions: pd.DataFrame, as_of: str | pd.Timestamp, days: int = 30) -> pd.DataFrame:
    if predictions.empty:
        return predictions.copy()
    start = pd.Timestamp(as_of).normalize()
    end = start + pd.Timedelta(days=days)
    out = predictions.copy()
    out["predicted_next_date"] = pd.to_datetime(out["predicted_next_date"])
    out = out[(out["predicted_next_date"] >= start) & (out["predicted_next_date"] <= end)].copy()
    out["days_until"] = (out["predicted_next_date"] - start).dt.days
    return out.sort_values(["predicted_next_date", "expected_amount"], ascending=[True, False])


def projected_available_balance(current_balance: float, upcoming: pd.DataFrame) -> float:
    if upcoming.empty:
        return round(float(current_balance), 2)
    return round(float(current_balance) - float(upcoming["expected_amount"].sum()), 2)
