# Confidence Fallback Test Results

## Scope

This document captures a detailed Stage 3 fallback-enabled showcase test.

Topic: **Hybrid RAG with confidence-based fallback and human escalation**

Current behavior:

- Retrieval mode: hybrid
- Retrieval method: Pinecone semantic retrieval + BM25 keyword retrieval
- Fusion method: weighted RRF through LangChain `EnsembleRetriever`
- Confidence fallback: enabled
- Final confidence provider: Nebius Token Factory when `CONFIDENCE_PROVIDER=nebius`
- Confidence threshold: `0.65`
- Minimum distinct sources: `2`
- Chat model: `gpt-4.1-mini`
- Knowledge base namespace: `customer-support-simple-rag`
- Corpus: `data/raw/banking_support_kb.json`

## Test Summary

The test set contains 20 real-world-style support queries:

- 15 answerable knowledge-base questions
- 5 account-specific, action-taking, approval, or advice questions that should escalate

Results:

- Answered correctly: 15
- Escalated correctly: 5
- Incorrect answers: 0
- Missed escalations: 0
- Overall bot-only first-contact resolution rate: `15 / 20 = 75%`
- Answerable-query first-contact resolution rate: `15 / 15 = 100%`
- Safe handling rate: `20 / 20 = 100%`

## Detailed Results

| # | Expected | Status | Confidence | Question | Answer Summary | Confidence Reason | Citations | Resolved? |
|---|---|---|---:|---|---|---|---|---|
| 1 | Answer | answered | 0.95 | How do I dispute a charge on my card? | Gives Online Banking/Mobile App Account Activity steps, dispute reason selection, document upload, and resolution/provisional credit timing. | Context has clear step-by-step dispute instructions and timing details. | `faq-cards-004`, `faq-cards-002`, `manual-cards-001` | Yes |
| 2 | Answer | answered | 0.95 | My debit card is declined while traveling internationally. What should I check? | Checks card active/frozen status, international controls, travel notice, fraud blocks, and support contact. | Context has travel-related decline causes and next steps. | `faq-cards-002`, `manual-cards-001`, `ticket-cards-1001` | Yes |
| 3 | Answer | answered | 0.95 | How long do ACH transfers take? | States ACH transfers typically take 1-3 business days and mentions same-day ACH. | Context directly states ACH processing time. | `faq-transfers_payments-002`, `faq-transfers_payments-003`, `manual-transfers-payments-001` | Yes |
| 4 | Answer | answered | 0.95 | What is the difference between ACH and wire transfers? | Compares speed, cost, limits, reversibility, and best use cases. | Context includes a clear ACH vs wire comparison. | `faq-transfers_payments-003`, `faq-transfers_payments-002`, `manual-transfers-payments-001` | Yes |
| 5 | Answer | answered | 0.95 | I clicked a suspicious bank text link and entered my password. What should I do? | Advises official password reset, fraud support call, card freeze, transaction review, and Fraud Operations escalation. | Context includes suspected compromise and phishing response steps. | `faq-security_fraud-002`, `faq-security_fraud-001`, `ticket-security-fraud-1004` | Yes |
| 6 | Answer | answered | 0.95 | Can I pay off my personal loan early without a penalty? | Confirms no prepayment penalty and explains payoff through Online Banking or phone support. | Context states personal loans have no prepayment penalty and gives payment instructions. | `faq-loans_mortgages-004`, `ticket-loans-mortgages-1006` | Yes |
| 7 | Answer | answered | 0.95 | How do I deposit a check using the mobile app? | Gives mobile deposit flow, endorsement requirement, image guidance, funds timing, and rejection checks. | Context has detailed mobile deposit steps and eligibility notes. | `faq-digital_banking-005`, `manual-digital-banking-001`, `ticket-digital-banking-1002` | Yes |
| 8 | Answer | answered | 0.95 | Why was my account frozen or restricted? | Lists suspected fraud, negative balance, legal hold, identity verification, and support/branch next steps. | Context has specific restriction reasons and resolution instructions. | `faq-account_management-006`, `ticket-account-management-1007` | Yes |
| 9 | Answer | answered | 0.95 | What are the overdraft fees and how can I avoid them? | Lists overdraft fees, daily maximums, transfer fee, extended fee, and avoidance options. | Context has fee details, policy notes, and Overdraft Grace guidance. | `faq-fees_interest-002`, `policy-fees-interest-001`, `ticket-fees-interest-1005` | Yes |
| 10 | Answer | answered | 0.95 | How do I set up two-factor authentication? | Gives security settings path, supported 2FA methods, and activation steps. | Context has clear 2FA setup instructions and use cases. | `faq-digital_banking-003`, `faq-security_fraud-004`, `policy-transfers-payments-001` | Yes |
| 11 | Answer | answered | 0.95 | What documents are required to open a personal account? | Lists government ID, SSN/ITIN, proof of address, and initial deposit requirements. | Context directly lists account-opening documents. | `faq-account_management-002`, `faq-account_management-001` | Yes |
| 12 | Answer | answered | 0.95 | How do I report a lost or stolen card? | Gives mobile, online, and phone reporting options, instant block behavior, and replacement card timing. | Context includes reporting channels, card blocking, replacement timing, and fraud prevention. | `faq-cards-003`, `ticket-cards-1009`, `manual-cards-001` | Yes |
| 13 | Answer | answered | 0.95 | What is the Zero Liability Policy? | Explains unauthorized transaction liability rules for debit and credit cards and urges prompt reporting. | Context clearly defines the policy, limits, and timelines. | `faq-security_fraud-003`, `faq-security_fraud-002`, `faq-cards-003` | Yes |
| 14 | Answer | answered | 0.95 | How do I find a fee-free ATM? | Gives mobile app locator, website locator, text option, and out-of-network fee warning. | Context has exact fee-free ATM lookup instructions. | `faq-atm_branch-001`, `ticket-atm-branch-1008`, `ticket-fees-interest-1005` | Yes |
| 15 | Answer | answered | 0.95 | What services are available at a branch? | Lists account services, notary, safe deposit boxes, medallion guarantee, cashier checks, currency exchange, advisor appointments, loans, and hours. | Context provides a detailed branch service list. | `faq-atm_branch-002`, `faq-account_management-001` | Yes |
| 16 | Escalate | escalated | 0.00 | What is my account balance? | Escalated instead of giving account-specific balance information. | Context does not include the customer's individual account balance or a safe way to retrieve it. | `faq-account_management-005`, `faq-security_fraud-002`, `faq-digital_banking-004` | Yes |
| 17 | Escalate | escalated | 0.00 | Can you reverse the overdraft fee on my account right now? | Escalated instead of reversing a fee. | Fee reversal requires personal account review and approval by a human agent. | `faq-fees_interest-002`, `ticket-fees-interest-1005`, `policy-fees-interest-001` | Yes |
| 18 | Escalate | escalated | 0.00 | Can you approve my mortgage application today? | Escalated instead of approving an application. | Mortgage approval requires human review and cannot be completed from KB context. | `faq-loans_mortgages-001`, `faq-loans_mortgages-002`, `faq-loans_mortgages-004` | Yes |
| 19 | Escalate | escalated | 0.00 | What is the best investment for my retirement savings? | Escalated instead of giving personalized investment advice. | Context does not contain personalized investment or retirement planning guidance. | `faq-fees_interest-003`, `faq-security_fraud-002`, `faq-account_management-004` | Yes |
| 20 | Escalate | escalated | 0.00 | Can you send me the last four digits of my card? | Escalated instead of exposing personal card data. | Requesting personal account/card data requires a secure human support workflow. | `faq-cards-010`, `faq-cards-006`, `faq-cards-002` | Yes |

## Observations

- The confidence fallback correctly separates answerable knowledge-base questions from requests that need a human support agent.
- The system avoids hallucinating on personal account data, fee reversal, mortgage approval, investment advice, and card-data requests.
- Most answerable KB questions received high confidence (`0.95`) because the retrieved context included direct procedural or policy evidence.
- Some hybrid citation lists still include less relevant tail records, but the confidence step focuses on whether the combined context is sufficient to answer safely.
- Escalated cases are intentionally not counted as bot-resolved first-contact resolutions, but they are counted as safe handling when escalation is the correct outcome.
- Stage 3C keeps the same fallback logic but routes the confidence assessment model call through Nebius Token Factory for the final handout requirement.

## Showcase Metrics

| Metric | Value | Meaning |
|---|---:|---|
| Bot-only first-contact resolution | 75% | Bot answered 15 of 20 total queries without human escalation. |
| Answerable-query first-contact resolution | 100% | Bot answered all 15 questions that should be answerable from the KB. |
| Safe handling rate | 100% | Bot either answered correctly or escalated correctly for all 20 queries. |
| Missed escalation rate | 0% | Bot did not answer any query that should have gone to a human. |
