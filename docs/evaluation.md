# Evaluation Notes

This document captures Stage 3B fallback-enabled evaluation for the customer support RAG bot.

## Stage 3A Fallback Criteria

Current answer status values:

- `answered`: retrieved context appears sufficient and confidence is at or above threshold.
- `escalated`: retrieved context is insufficient, confidence is below threshold, or the request requires a human support agent.

Current confidence settings:

- `CONFIDENCE_PROVIDER=nebius` for final submission
- `CONFIDENCE_THRESHOLD=0.65`
- `CONFIDENCE_MIN_SOURCES=2`

Stage 3C note: the confidence assessment step now supports Nebius Token Factory through its OpenAI-compatible API. Earlier Stage 3B metrics remain valid for fallback behavior; after adding a local `NEBIUS_API_KEY` and setting `CONFIDENCE_PROVIDER=nebius`, rerun `support-bot check-connections` and the smoke tests to verify the same answer/escalation behavior with Nebius as the confidence provider.

First-contact resolution rate is calculated as:

```text
answered_and_correct / total_test_queries
```

## Stage 3A Smoke Tests

| # | Query | Retrieval | Expected outcome | Bot status | Notes |
|---|---|---|---|---|---|
| 1 | How do I dispute a charge on my card? | hybrid | Answer from KB | answered | Returned confidence `0.95` with clear dispute procedure evidence. |
| 2 | What is my account balance? | hybrid | Escalate to human | escalated | Returned confidence `0.00` because retrieved context did not contain personal account data. |

## Stage 3B Metrics

Evaluation setup:

- Retrieval mode: hybrid
- Confidence fallback: enabled
- Test size: 20 real-world-style support queries
- Answerable KB questions: 15
- Expected escalation questions: 5

Results:

- Answered correctly: 15
- Escalated correctly: 5
- Incorrect answers: 0
- Missed escalations: 0
- Overall bot-only first-contact resolution rate: `15 / 20 = 75%`
- Answerable-query first-contact resolution rate: `15 / 15 = 100%`
- Safe handling rate: `(15 correct answers + 5 correct escalations) / 20 = 100%`

Detailed answer summaries, confidence reasons, and citations are documented in `docs/fallback_rag_test_results.md`.

Interpretation:

- The bot resolved all answerable KB questions at first contact.
- The bot avoided hallucinating for account-specific, action-taking, approval, and advice requests.
- Overall FCR is lower than safe handling because escalated cases are intentionally handed to a human instead of being resolved by the bot.

## Query Set

| # | Query | Expected outcome | Bot status | Confidence | Citations | Resolved? | Notes |
|---|---|---|---|---:|---|---|---|
| 1 | How do I dispute a charge on my card? | Answer from KB | answered | 0.95 | `faq-cards-004`, `faq-cards-002`, `manual-cards-001` | Yes | Correct dispute steps and timeline. |
| 2 | My debit card is declined while traveling internationally. What should I check? | Answer from KB | answered | 0.95 | `faq-cards-002`, `manual-cards-001`, `ticket-cards-1001` | Yes | Correct travel notice, international controls, limit, and fraud-block checks. |
| 3 | How long do ACH transfers take? | Answer from KB | answered | 0.95 | `faq-transfers_payments-002`, `faq-transfers_payments-003`, `manual-transfers-payments-001` | Yes | Correct 1-3 business day ACH timing and same-day ACH note. |
| 4 | What is the difference between ACH and wire transfers? | Answer from KB | answered | 0.95 | `faq-transfers_payments-003`, `faq-transfers_payments-002`, `manual-transfers-payments-001` | Yes | Correct comparison of speed, cost, limits, reversibility, and use cases. |
| 5 | I clicked a suspicious bank text link and entered my password. What should I do? | Answer from KB | answered | 0.95 | `faq-security_fraud-002`, `faq-security_fraud-001`, `ticket-security-fraud-1004` | Yes | Correct urgent fraud response and escalation guidance. |
| 6 | Can I pay off my personal loan early without a penalty? | Answer from KB | answered | 0.95 | `faq-loans_mortgages-004`, `ticket-loans-mortgages-1006` | Yes | Correct no-prepayment-penalty answer and payoff method. |
| 7 | How do I deposit a check using the mobile app? | Answer from KB | answered | 0.95 | `faq-digital_banking-005`, `manual-digital-banking-001`, `ticket-digital-banking-1002` | Yes | Correct mobile deposit steps, endorsement, and availability guidance. |
| 8 | Why was my account frozen or restricted? | Answer from KB | answered | 0.95 | `faq-account_management-006`, `ticket-account-management-1007` | Yes | Correct reasons and next steps for restrictions. |
| 9 | What are the overdraft fees and how can I avoid them? | Answer from KB | answered | 0.95 | `faq-fees_interest-002`, `policy-fees-interest-001`, `ticket-fees-interest-1005` | Yes | Correct fee amounts and avoidance options. |
| 10 | How do I set up two-factor authentication? | Answer from KB | answered | 0.95 | `faq-digital_banking-003`, `faq-security_fraud-004`, `policy-transfers-payments-001` | Yes | Correct 2FA setup path and supported methods. |
| 11 | What documents are required to open a personal account? | Answer from KB | answered | 0.95 | `faq-account_management-002`, `faq-account_management-001` | Yes | Correct ID, SSN/ITIN, address proof, and deposit requirements. |
| 12 | How do I report a lost or stolen card? | Answer from KB | answered | 0.95 | `faq-cards-003`, `ticket-cards-1009`, `manual-cards-001` | Yes | Correct reporting channels, instant block, and replacement note. |
| 13 | What is the Zero Liability Policy? | Answer from KB | answered | 0.95 | `faq-security_fraud-003`, `faq-security_fraud-002`, `faq-cards-003` | Yes | Correct unauthorized-transaction liability explanation. |
| 14 | How do I find a fee-free ATM? | Answer from KB | answered | 0.95 | `faq-atm_branch-001`, `ticket-atm-branch-1008`, `ticket-fees-interest-1005` | Yes | Correct app, website, and text locator options. |
| 15 | What services are available at a branch? | Answer from KB | answered | 0.95 | `faq-atm_branch-002`, `faq-account_management-001` | Yes | Correct branch service list and hours note. |
| 16 | What is my account balance? | Escalate to human | escalated | 0.00 | `faq-account_management-005`, `faq-security_fraud-002`, `faq-digital_banking-004` | No | Correctly escalated because specific account balance requires account access. |
| 17 | Can you reverse the overdraft fee on my account right now? | Escalate to human | escalated | 0.00 | `faq-fees_interest-002`, `ticket-fees-interest-1005`, `policy-fees-interest-001` | No | Correctly escalated because fee reversal requires account review and approval. |
| 18 | Can you approve my mortgage application today? | Escalate to human | escalated | 0.00 | `faq-loans_mortgages-001`, `faq-loans_mortgages-002`, `faq-loans_mortgages-004` | No | Correctly escalated because approval requires human underwriting/review. |
| 19 | What is the best investment for my retirement savings? | Escalate to human | escalated | 0.00 | `faq-fees_interest-003`, `faq-security_fraud-002`, `faq-account_management-004` | No | Correctly escalated because personalized investment advice is outside the KB. |
| 20 | Can you send me the last four digits of my card? | Escalate to human | escalated | 0.00 | `faq-cards-010`, `faq-cards-006`, `faq-cards-002` | No | Correctly escalated because personal card data requires secure human/account workflow. |
