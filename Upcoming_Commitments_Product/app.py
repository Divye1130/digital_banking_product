from pathlib import Path
import pandas as pd
import streamlit as st

from src.recurring import detect_recurring
from src.forecast import upcoming_commitments, projected_available_balance

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "synthetic_transactions.csv"

st.set_page_config(page_title="Upcoming Commitments", page_icon="💳", layout="wide")
st.title("Upcoming Commitments")
st.caption("Digital-banking product using synthetic demonstration data.")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA, parse_dates=["date"])
    preds = detect_recurring(df)
    return df, preds

df, preds = load_data()
customers = sorted(df["customer_id"].unique())
customer = st.sidebar.selectbox("Synthetic customer", customers, index=0)
customer_tx = df[df["customer_id"].eq(customer)].copy()
customer_pred = preds[preds["customer_id"].eq(customer)].copy()

as_of = pd.Timestamp(customer_tx["date"].max()).normalize()
# The current build simulates the day after the latest observed transaction so predicted items can be shown.
as_of = as_of + pd.Timedelta(days=1)
current_balance = st.sidebar.number_input("Current balance (£)", min_value=0.0, value=1750.0, step=50.0)
warning_threshold = st.sidebar.number_input("Low-balance warning threshold (£)", min_value=0.0, value=500.0, step=50.0)

upcoming = upcoming_commitments(customer_pred, as_of=as_of, days=35)
projected = projected_available_balance(current_balance, upcoming)

c1, c2, c3 = st.columns(3)
c1.metric("Current balance", f"£{current_balance:,.2f}")
c2.metric("Expected commitments (35d)", f"£{upcoming['expected_amount'].sum():,.2f}" if not upcoming.empty else "£0.00")
c3.metric("Projected available", f"£{projected:,.2f}")

if projected < warning_threshold:
    st.warning(f"Projected available balance may fall below your £{warning_threshold:,.0f} alert threshold.")

home, recurring, detail, metrics = st.tabs(["Upcoming", "Recurring payments", "Payment detail", "Product notes"])

with home:
    st.subheader("Upcoming recurring commitments")
    if upcoming.empty:
        st.info("No recurring commitments are predicted in the next 35 days for this synthetic customer.")
    else:
        show = upcoming[["merchant", "category", "predicted_next_date", "expected_amount", "confidence", "days_until"]].copy()
        show["expected_amount"] = show["expected_amount"].map(lambda x: f"£{x:,.2f}")
        st.dataframe(show, use_container_width=True, hide_index=True)

with recurring:
    st.subheader("Detected recurring payments")
    if customer_pred.empty:
        st.info("No recurring payments detected.")
    else:
        view = customer_pred[["merchant", "category", "occurrences", "expected_amount", "predicted_next_date", "confidence"]].copy()
        st.dataframe(view, use_container_width=True, hide_index=True)

with detail:
    st.subheader("Review a detected payment")
    if customer_pred.empty:
        st.info("No detected recurring payment to review.")
    else:
        merchant = st.selectbox("Payment", customer_pred["merchant"].tolist())
        row = customer_pred[customer_pred["merchant"].eq(merchant)].iloc[0]
        st.write(f"**Expected amount:** £{row['expected_amount']:,.2f}")
        st.write(f"**Predicted date:** {row['predicted_next_date']}")
        st.write(f"**Confidence:** {row['confidence']:.0%}")
        hist = customer_tx[customer_tx["merchant"].eq(merchant)][["date", "amount"]].sort_values("date")
        st.line_chart(hist.set_index("date"))
        decision = st.radio("Is this a recurring payment?", ["Confirm", "Not recurring"], horizontal=True)
        if st.button("Save review"):
            st.success(f"Review saved in-session: {merchant} → {decision}.")

with metrics:
    st.subheader("Product scope")
    st.markdown(
        """
        - Synthetic data only; this is not connected to a real bank or customer account.
        - Recurring-payment detection is deterministic and explainable rather than ML-heavy.
        - Customer research, production security, regulatory review and live launch are outside the current build's completed scope.
        - Product artefacts in `/product` cover the problem brief, PRD, prioritised backlog, customer journey, metrics and launch-readiness checklist.
        """
    )
