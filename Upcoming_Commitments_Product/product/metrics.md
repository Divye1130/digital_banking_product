# Product Metrics Framework

## Proposed primary metric
**Useful review rate:** percentage of active users who open Upcoming Commitments and either review an upcoming payment or confirm/correct at least one recurring-payment classification.

## Supporting metrics
- Feature activation rate.
- Percentage of customers with at least one detected recurring payment.
- Confirmation rate for detected recurring payments.
- Correction/rejection rate.
- Low-balance alert opt-in rate.
- Return usage over 30 days.

## Quality / guardrail metrics
- Recurring-payment precision and recall against labelled data.
- False-positive alert rate.
- Percentage of predictions below confidence threshold.
- Application error rate / failed calculations.
- Latency for loading a customer's recurring-payment view.

## Interpretation
These metrics are definitions for a future pilot. The only measured metrics in the current build are algorithm-quality and technical-test results on synthetic labelled data.
