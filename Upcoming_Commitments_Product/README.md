# Upcoming Commitments - Digital Banking Product

Independent portfolio product designed to demonstrate end-to-end digital product thinking for a consumer-banking use case: problem framing, product requirements, prioritisation, technical implementation, validation and launch-readiness thinking.

## What is actually implemented
- Synthetic labelled transaction generator for 200 customers across six months.
- Explainable recurring-payment detection.
- Prediction of expected next date and amount.
- 35-day upcoming-commitments view.
- Projected available-balance calculation and configurable low-balance warning.
- Standalone interactive HTML/JavaScript review flow (open `index.html` in any modern browser).
- Optional Streamlit implementation in `app.py` for the same core flow.
- Product artefacts: problem brief, PRD, customer journey, prioritised RICE backlog, metrics framework and launch-readiness checklist.
- Automated pytest suite.

## What is not claimed
No real bank data, customer interviews, real user-testing participants, Open Banking integration, production deployment, regulatory approval or live customer launch.

## Run
```bash
python -m src.data_gen
pytest -q
python build_product.py
# Then open index.html in a browser
# Optional: pip install -r requirements.txt && streamlit run app.py
```

## Why the product uses simple rules
The purpose is not to optimise a machine-learning benchmark. The recurrence logic is deliberately transparent so product behaviour is explainable and easy to test. A more complex approach would need evidence from real labelled data that it creates incremental customer value.
