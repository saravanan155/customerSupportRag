# Evaluation Notes

We will use this for the 20 real-world-style support queries and first-contact resolution metrics.

## Stage 3A Fallback Criteria

Current answer status values:

- `answered`: retrieved context appears sufficient and confidence is at or above threshold.
- `escalated`: retrieved context is insufficient, confidence is below threshold, or the request requires a human support agent.

Current confidence settings:

- `CONFIDENCE_THRESHOLD=0.65`
- `CONFIDENCE_MIN_SOURCES=2`

First-contact resolution rate will be calculated in Stage 3B as:

```text
answered_and_correct / total_test_queries
```

## Stage 3A Smoke Tests

| # | Query | Retrieval | Expected outcome | Bot status | Notes |
|---|---|---|---|---|---|
| 1 | How do I dispute a charge on my card? | hybrid | Answer from KB | answered | Returned confidence `0.95` with clear dispute procedure evidence. |
| 2 | What is my account balance? | hybrid | Escalate to human | escalated | Returned confidence `0.00` because retrieved context did not contain personal account data. |

## Query Set

| # | Query | Expected outcome | Bot status | Resolved? | Notes |
|---|---|---|---|---|---|
