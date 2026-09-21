from __future__ import annotations

import numpy as np
import pandas as pd


KNOWN_REGULAR_CADENCES = (7, 14, 28, 29, 30, 31)


def _cadence_score(median_days: float) -> float:
    distance = min(abs(median_days - c) for c in KNOWN_REGULAR_CADENCES)
    return max(0.0, 1.0 - distance / 4.0)


def detect_recurring(transactions: pd.DataFrame, min_occurrences: int = 3) -> pd.DataFrame:
    """Detect recurring debit merchants for each customer using transparent rules."""
    tx = transactions.copy()
    tx["date"] = pd.to_datetime(tx["date"])
    tx = tx[tx["direction"].eq("debit")]
    results: list[dict] = []

    for (customer_id, merchant), g in tx.groupby(["customer_id", "merchant"]):
        g = g.sort_values("date")
        if len(g) < min_occurrences:
            continue

        dates = g["date"].drop_duplicates().sort_values()
        if len(dates) < min_occurrences:
            continue
        intervals = dates.diff().dropna().dt.days.astype(float)
        if intervals.empty:
            continue

        median_interval = float(intervals.median())
        interval_mad = float(np.median(np.abs(intervals - median_interval)))
        cadence = _cadence_score(median_interval)

        amounts = g["amount"].astype(float)
        amount_median = float(amounts.median())
        amount_cv = float(amounts.std(ddof=0) / amount_median) if amount_median else 999.0

        regular_timing = cadence >= 0.50 and interval_mad <= 5.0
        regular_amount = amount_cv <= 0.25
        detected = bool(regular_timing and regular_amount)
        if not detected:
            continue

        regularity = max(0.0, 1.0 - interval_mad / 7.0)
        amount_score = max(0.0, 1.0 - amount_cv / 0.30)
        confidence = float(np.clip(0.45 * cadence + 0.35 * regularity + 0.20 * amount_score, 0, 1))

        last_date = dates.iloc[-1]
        next_date = last_date + pd.Timedelta(days=int(round(median_interval)))
        results.append({
            "customer_id": customer_id,
            "merchant": merchant,
            "category": g["category"].mode().iat[0],
            "occurrences": int(len(g)),
            "median_interval_days": round(median_interval, 1),
            "interval_mad_days": round(interval_mad, 1),
            "expected_amount": round(amount_median, 2),
            "amount_cv": round(amount_cv, 3),
            "last_payment_date": last_date.date().isoformat(),
            "predicted_next_date": next_date.date().isoformat(),
            "confidence": round(confidence, 3),
        })

    return pd.DataFrame(results).sort_values(["customer_id", "predicted_next_date", "merchant"]).reset_index(drop=True)


def evaluate_detection(transactions: pd.DataFrame, predictions: pd.DataFrame) -> dict:
    """Evaluate merchant-level recurring detection against synthetic ground truth."""
    true_pairs = set(
        transactions.loc[
            transactions["is_true_recurring"].astype(bool) & transactions["direction"].eq("debit"),
            ["customer_id", "merchant"],
        ].drop_duplicates().itertuples(index=False, name=None)
    )
    pred_pairs = set(predictions[["customer_id", "merchant"]].itertuples(index=False, name=None)) if not predictions.empty else set()
    tp = len(true_pairs & pred_pairs)
    fp = len(pred_pairs - true_pairs)
    fn = len(true_pairs - pred_pairs)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_recurring_pairs": len(true_pairs),
        "predicted_pairs": len(pred_pairs),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
