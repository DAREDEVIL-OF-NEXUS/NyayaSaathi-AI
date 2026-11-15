# ADR-007: Pecuniary Jurisdiction Determination in Complaint Engine

## Status
Accepted

## Context
Under the Consumer Protection Act, 2019 Section 34(1) and the Consumer Protection (Jurisdiction of District Commission, State Commission and National Commission) Rules, 2021 (G.S.R. 888(E)), pecuniary jurisdiction is determined strictly by the **value of consideration paid for the goods or services**, NOT by the total claim amount inclusive of compensation for mental harassment or punitive damages. Many legal tools incorrectly calculate forum based on total claim, leading to jurisdictional dismissal in consumer courts.

## Decision
Encode statutory pecuniary thresholds explicitly inside `ComplaintEngine`:
- Consideration $\le \text{₹}50,00,000$ (₹50 Lakhs): **District Consumer Disputes Redressal Commission** (Rule 2(a)).
- Consideration $> \text{₹}50,00,000$ up to $\text{₹}2,00,00,000$ (₹2 Crores): **State Consumer Disputes Redressal Commission** (Rule 2(b)).
- Consideration $> \text{₹}2,00,00,000$ (₹2 Crores): **National Consumer Disputes Redressal Commission (NCDRC)** (Rule 2(c)).
- Additional claims for mental agony, punitive damages, and litigation expenses are documented as reliefs sought under Section 39, without shifting pecuniary jurisdiction.

## Consequences
- **Positive:** Guarantees complaints are drafted for the legally correct forum under prevailing 2021 gazette notification.
- **Positive:** Complies with Supreme Court precedents on consideration-based jurisdiction.
