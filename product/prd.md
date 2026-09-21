# Product Requirements Document - Upcoming Commitments

## Objective
Give a current-account customer a forward-looking view of recurring commitments over the next 30-35 days and an estimate of the balance that remains available after those commitments.

## MVP user stories and acceptance criteria

### US1 - View upcoming recurring commitments
**As a** current-account customer, **I want** to see recurring payments expected soon **so that** I understand near-term commitments.

Acceptance criteria:
- Display merchant, expected amount, predicted payment date and confidence.
- Only display items whose predicted date falls inside the selected forecast window.
- Sort by predicted payment date.

### US2 - Understand projected available balance
**As a** customer, **I want** to see my balance after expected commitments **so that** I can make a more informed spending decision.

Acceptance criteria:
- Accept current balance as an input in the application.
- Sum expected payments in the forecast window.
- Show `current balance - expected commitments` as projected available balance.

### US3 - Receive a low-balance warning
**As a** customer, **I want** to choose a warning threshold **so that** I receive an early warning if upcoming commitments may leave too little available cash.

Acceptance criteria:
- User can enter a threshold.
- Warning is shown when projected available balance is below the threshold.

### US4 - Review a detected recurring payment
**As a** customer, **I want** to confirm or reject a detected recurring payment **so that** the product can surface obvious classification errors.

Acceptance criteria:
- User can select a detected payment.
- Show its payment history, expected amount/date and confidence.
- User can choose Confirm or Not recurring.
- The application records the decision within the current session only.

## Non-functional requirements
- Deterministic and explainable recurrence logic.
- Synthetic data only.
- Reproducible generation using fixed random seed.
- Automated tests for data integrity, detection quality and forecast calculations.
- No secrets, customer PII or external account connectivity.

## Non-goals
- Production-grade affordability advice.
- Automated cancellation of subscriptions.
- Credit decisions.
- Personalised financial advice.
- Real banking integration.
