# Product Architecture

```text
Synthetic transaction generator
          |
          v
synthetic_transactions.csv
          |
          v
Explainable recurring-payment detector
          |
          +----> merchant-level confidence / expected amount / next date
          |
          v
Upcoming commitments + projected balance calculations
          |
          v
Streamlit product application
```

## Design choice
The project intentionally uses transparent deterministic rules rather than a complex model. The goal is to demonstrate product discovery, requirements, prioritisation, implementation and validation. A more sophisticated model would only be justified if real labelled data showed that the rules were insufficient.
