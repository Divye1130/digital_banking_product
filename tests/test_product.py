import pandas as pd

from src.data_gen import SyntheticConfig, generate_transactions
from src.recurring import detect_recurring, evaluate_detection
from src.forecast import upcoming_commitments, projected_available_balance


def small_df():
    return generate_transactions(SyntheticConfig(n_customers=12, months=6, seed=11))


def test_generator_reproducible():
    a = generate_transactions(SyntheticConfig(n_customers=5, seed=1))
    b = generate_transactions(SyntheticConfig(n_customers=5, seed=1))
    pd.testing.assert_frame_equal(a, b)


def test_generator_has_expected_customers():
    df = small_df()
    assert df["customer_id"].nunique() == 12


def test_no_missing_core_fields():
    df = small_df()
    assert not df[["customer_id", "date", "merchant", "amount", "direction"]].isna().any().any()


def test_amounts_positive():
    df = small_df()
    assert (df["amount"] > 0).all()


def test_detection_returns_required_columns():
    pred = detect_recurring(small_df())
    required = {"customer_id", "merchant", "expected_amount", "predicted_next_date", "confidence"}
    assert required.issubset(pred.columns)


def test_detection_is_high_precision_on_synthetic_truth():
    df = small_df()
    pred = detect_recurring(df)
    m = evaluate_detection(df, pred)
    assert m["precision"] >= 0.90


def test_detection_has_useful_recall():
    df = small_df()
    pred = detect_recurring(df)
    m = evaluate_detection(df, pred)
    assert m["recall"] >= 0.60


def test_upcoming_window():
    pred = pd.DataFrame([
        {"customer_id": "C1", "merchant": "A", "predicted_next_date": "2026-07-10", "expected_amount": 20.0},
        {"customer_id": "C1", "merchant": "B", "predicted_next_date": "2026-08-20", "expected_amount": 30.0},
    ])
    out = upcoming_commitments(pred, "2026-07-01", days=30)
    assert out["merchant"].tolist() == ["A"]


def test_projected_balance():
    upcoming = pd.DataFrame({"expected_amount": [20.0, 30.0]})
    assert projected_available_balance(200.0, upcoming) == 150.0
