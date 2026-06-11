# Simple RAG Test Results

## Scope

This document captures a manual showcase test of the current Stage 1C simple RAG system.

Topic: **Simple RAG without confidence score, custom reranking, hybrid retrieval, or fallback escalation**

Current behavior:

- Retrieval method: Pinecone semantic similarity search only
- Embedding model: `text-embedding-3-small`
- Embedding dimensions: `512`
- Chat model: `gpt-4.1-mini`
- Knowledge base namespace: `customer-support-simple-rag`
- Corpus: `data/raw/banking_support_kb.json`
- Corpus size: 53 source records, ingested as 100 chunks
- Citation trace: source citations include the original JSON `record_id`

Limitations intentionally left for later stages:

- No BM25 keyword retrieval
- No RRF or custom reranking
- No confidence score
- No automated human-escalation fallback
- No first-contact resolution metric yet

## Test Summary

The test set uses 20 real-world-style banking support questions:

- 10 questions with `k=5`
- 10 questions with `k=3`
- Each result records the generated answer summary and the retrieved citation record IDs.

| # | Retrieval K | Question | Generated Answer Summary | Citations | Notes |
|---|---:|---|---|---|---|
| 1 | 5 | How do I dispute a charge on my card? | Log in to Online Banking or Mobile App, go to Account Activity, find the transaction, select Dispute this transaction, choose a reason, and submit supporting documents if available. | `faq-cards-004`, `faq-cards-002`, `manual-cards-001`, `faq-cards-003`, `faq-security_fraud-002` | Strong match. Top citation is the exact FAQ. |
| 2 | 5 | My debit card is declined while traveling internationally. What should I check? | Check that the card is active, not frozen, travel notice is set, international transactions are enabled, and no fraud block is active. Contact support or Card Fraud Support if needed. | `faq-cards-002`, `manual-cards-001`, `ticket-cards-1001`, `ticket-cards-1001`, `faq-cards-002` | Strong match. Retrieves FAQ, manual, and past ticket evidence. |
| 3 | 5 | How long do ACH transfers take? | ACH transfers typically take 1-3 business days. Same-day ACH can complete same day when available and within limits. | `faq-transfers_payments-003`, `faq-transfers_payments-002`, `manual-transfers-payments-001`, `faq-transfers_payments-005`, `faq-transfers_payments-001` | Good answer. Top citation is related comparison FAQ; exact ACH FAQ is second. |
| 4 | 5 | What is the difference between ACH and wire transfers? | ACH is slower, lower-cost, lower-limit, and reversible within a short window. Wire transfers are faster, higher-cost, higher-limit, and generally final. | `faq-transfers_payments-003`, `faq-transfers_payments-002`, `manual-transfers-payments-001`, `faq-transfers_payments-005`, `faq-transfers_payments-003` | Strong match. Top citation is exact FAQ. |
| 5 | 5 | I clicked a suspicious bank text link and entered my password. What should I do? | Change password using the official app/site, call fraud support, review transactions, freeze cards if needed, avoid suspicious links, and have support lock/escalate the account. | `faq-security_fraud-002`, `faq-security_fraud-001`, `faq-security_fraud-001`, `ticket-security-fraud-1004`, `manual-security-fraud-001` | Strong match. Good use of FAQ, past escalated ticket, and runbook. |
| 6 | 5 | Can I pay off my personal loan early without a penalty? | Yes. Personal loans can be paid off early without a prepayment penalty. Customer pays principal plus accrued interest through payoff date. | `faq-loans_mortgages-004`, `ticket-loans-mortgages-1006`, `ticket-loans-mortgages-1006`, `faq-loans_mortgages-002`, `faq-loans_mortgages-001` | Strong match. Exact FAQ plus past ticket. |
| 7 | 5 | How do I deposit a check using the mobile app? | Open the app, go to Deposit / Mobile Check Deposit, select account, enter amount, photograph front/back, endorse correctly, submit, and confirm. | `faq-digital_banking-005`, `manual-digital-banking-001`, `ticket-digital-banking-1002`, `manual-digital-banking-001`, `faq-digital_banking-004` | Strong match. Answer includes both process and rejection guidance. |
| 8 | 5 | Why was my account frozen or restricted? | Account may be frozen due to suspected fraud, negative balance, legal hold, or identity verification. Next step is identity verification or support/branch follow-up. | `faq-account_management-006`, `faq-account_management-006`, `ticket-account-management-1007`, `faq-security_fraud-002`, `faq-security_fraud-002` | Strong match. Includes exact FAQ and escalated ticket. |
| 9 | 5 | What are the overdraft fees and how can I avoid them? | Overdraft fee is $35 per item, up to three per day; extended overdraft fees may apply. Avoid fees with linked savings, Overdraft Grace, and low-balance alerts. | `faq-fees_interest-002`, `faq-fees_interest-002`, `ticket-fees-interest-1005`, `policy-fees-interest-001`, `faq-fees_interest-001` | Strong match. FAQ plus policy and ticket evidence. |
| 10 | 5 | How do I set up two-factor authentication? | Log in, go to Profile & Settings / Security / Two-Factor Authentication, choose SMS, authenticator app, or email, then complete verification. | `faq-digital_banking-003`, `faq-security_fraud-002`, `faq-security_fraud-004`, `faq-digital_banking-002`, `faq-digital_banking-001` | Strong match. Exact FAQ first; related security docs follow. |
| 11 | 3 | What documents are required to open a personal account? | Personal account opening requires government photo ID, SSN or ITIN, proof of address, and initial deposit details depending on account type. | `faq-account_management-002`, `faq-account_management-002`, `faq-account_management-001` | Strong match. Exact FAQ retrieved first. |
| 12 | 3 | How do I update my address or phone number? | Update via Online Banking, Mobile App, phone support, or branch. Digital communication changes take effect immediately; physical mail may take 1-2 billing cycles. | `faq-account_management-003`, `faq-account_management-003`, `faq-cards-002` | Good answer. Third citation is off-topic, showing lower `k` still can include some noise. |
| 13 | 3 | How do I report a lost or stolen card? | Report immediately through Mobile App, Online Banking, or phone support to block the card and prevent unauthorized charges. | `faq-cards-003`, `manual-cards-001`, `faq-cards-002` | Strong match. Exact FAQ first. |
| 14 | 3 | What are the daily transfer limits? | Lists daily limits for own-account transfers, ACH, same-day ACH, domestic wires, Zelle, and Bill Pay; advises calling support for higher limits. | `faq-transfers_payments-005`, `manual-digital-banking-001`, `faq-transfers_payments-001` | Good answer. Exact FAQ first; one unrelated mobile deposit manual appears. |
| 15 | 3 | How do I set up direct deposit? | Provide employer with routing/account number, complete employer direct deposit form, or download a pre-filled form from Online Banking. Allow 1-2 pay cycles. | `faq-transfers_payments-004`, `faq-transfers_payments-004`, `faq-cards-001` | Strong answer. Third citation is unrelated activation FAQ. |
| 16 | 3 | What is a HELOC and how does it work? | HELOC lets customers borrow against home equity, with borrowing based on appraised value minus mortgage balance, a draw period, repayment period, and variable rate. | `faq-loans_mortgages-005`, `faq-loans_mortgages-005`, `faq-loans_mortgages-001` | Strong match. Exact FAQ retrieved in top two chunks. |
| 17 | 3 | What mobile app features are available? | Mobile app supports balances, history, mobile deposit, transfers, Zelle, Bill Pay, card management, loan/mortgage management, locator, insights, documents, and secure messaging. | `faq-digital_banking-004`, `faq-digital_banking-004`, `manual-cards-001` | Strong answer. Related card controls manual appears as third citation. |
| 18 | 3 | What is the Zero Liability Policy? | Customer is not responsible for unauthorized transactions when reported promptly, credentials were not shared, and account is in good standing; debit and credit card rules differ. | `faq-security_fraud-003`, `faq-security_fraud-002`, `faq-security_fraud-003` | Strong match. Exact FAQ appears first and third. |
| 19 | 3 | How do I find a fee-free ATM? | Use the mobile app ATM/Branch Locator with Fee-Free filter, the website locator, or text ATM plus zip code. Only listed network ATMs are fee-free. | `faq-atm_branch-001`, `ticket-atm-branch-1008`, `ticket-fees-interest-1005` | Good answer. Exact FAQ first; third citation is unrelated fee ticket. |
| 20 | 3 | What services are available at a branch? | Branch services include account opening/closing, notary, safe deposit boxes, medallion signature guarantee, cashier's checks, currency exchange, advisor appointments, and loan applications. | `faq-atm_branch-002`, `faq-atm_branch-002`, `faq-account_management-001` | Strong answer. Exact FAQ first two chunks. |

## Observations

- Simple semantic RAG works well for direct FAQ-style questions when the knowledge base has close matching content.
- `k=5` often retrieves richer supporting evidence, including past tickets, policies, manuals, and runbooks.
- `k=3` is concise but sometimes includes an unrelated third citation; this is a useful observation for later hybrid retrieval and reranking.
- The system currently produces helpful answers, but it does not yet decide when evidence is insufficient. That belongs in Stage 3.
- Citation record IDs make every answer traceable to `data/raw/banking_support_kb.json`.

## Same-Question K=5 vs K=3 Comparison

This paired comparison uses the same question with both retrieval depths. It helps show how much additional context `k=5` contributes compared with the more compact `k=3` setting.

| # | Question | K=5 Answer Summary | K=5 Citations | K=3 Answer Summary | K=3 Citations | Comparison Notes |
|---|---|---|---|---|---|---|
| 1 | My debit card is declined while traveling internationally. What should I check? | Checks card active/frozen status, travel notice, international transaction controls, and possible fraud blocks. Recommends Card Fraud Support if still blocked. | `faq-cards-002`, `manual-cards-001`, `ticket-cards-1001`, `ticket-cards-1001`, `faq-cards-002` | Similar guidance, slightly shorter. Includes card status, travel notice, international transactions, and fraud support. | `faq-cards-002`, `manual-cards-001`, `ticket-cards-1001` | Both are strong. `k=5` adds duplicate supporting chunks from the exact FAQ/ticket; `k=3` is cleaner and sufficient. |
| 2 | How do I deposit a check using the mobile app? | Gives step-by-step mobile deposit instructions and adds delayed/rejected deposit checks such as eligibility, app version, endorsement, image quality, and limits. | `faq-digital_banking-005`, `manual-digital-banking-001`, `ticket-digital-banking-1002`, `manual-digital-banking-001`, `faq-digital_banking-004` | Gives core deposit steps and basic troubleshooting for account eligibility and app version. | `faq-digital_banking-005`, `manual-digital-banking-001`, `ticket-digital-banking-1002` | Both answer correctly. `k=5` adds broader troubleshooting detail; `k=3` is concise and still well grounded. |
| 3 | What are the overdraft fees and how can I avoid them? | Lists fee amounts, daily maximum, extended fee, transfer fee, and avoidance methods including linked savings, Overdraft Grace, and low-balance alerts. | `faq-fees_interest-002`, `faq-fees_interest-002`, `ticket-fees-interest-1005`, `policy-fees-interest-001`, `faq-fees_interest-001` | Similar fee and avoidance answer, with less policy/ticket context. | `faq-fees_interest-002`, `faq-fees_interest-002`, `ticket-fees-interest-1005` | `k=5` is better for policy support because it retrieves the Overdraft Grace policy. `k=3` still answers the direct FAQ. |
| 4 | I clicked a suspicious bank text link and entered my password. What should I do? | Advises official password reset, fraud support call, transaction review, card freeze, avoiding suspicious links, and escalation to Fraud Operations. | `faq-security_fraud-002`, `faq-security_fraud-001`, `faq-security_fraud-001`, `ticket-security-fraud-1004`, `manual-security-fraud-001` | Advises password change, fraud support, transaction review, card freeze, 2FA, and phishing reporting. | `faq-security_fraud-002`, `faq-security_fraud-001`, `faq-security_fraud-001` | `k=5` is stronger for high-risk fraud because it retrieves the escalated past ticket and runbook. This is a good example where more context improves operational safety. |
| 5 | How long do ACH transfers take? | States ACH is 1-3 business days and same-day ACH is available for a fee within limits. | `faq-transfers_payments-003`, `faq-transfers_payments-002`, `manual-transfers-payments-001`, `faq-transfers_payments-005`, `faq-transfers_payments-001` | States ACH is 1-3 business days, mentions same-day ACH, and suggests wire transfer if faster movement is needed. | `faq-transfers_payments-003`, `faq-transfers_payments-002`, `manual-transfers-payments-001` | Both answer the timing question. `k=5` adds transfer limit context; `k=3` is direct. Top citation is related comparison FAQ rather than exact ACH FAQ in both runs. |
| 6 | How do I update my address or phone number? | Provides online, mobile, phone, and branch update options, plus timing for digital communications and physical mail. | `faq-account_management-003`, `faq-account_management-003`, `faq-cards-002`, `faq-cards-006`, `faq-account_management-001` | Provides the same core update options and timing. | `faq-account_management-003`, `faq-account_management-003`, `faq-cards-002` | `k=3` is cleaner here. `k=5` adds extra unrelated card/account-opening citations, showing simple semantic retrieval can add noise without reranking/filtering. |

### Comparison Takeaways

- `k=3` often gives enough context for simple FAQ questions and can produce cleaner citation lists.
- `k=5` is useful when the answer benefits from richer operational context, especially for fraud, policy, or past-ticket examples.
- Additional chunks can also introduce duplicate or off-topic citations. This motivates Stage 2 hybrid retrieval and later reranking/evidence scoring.
- For the current simple RAG stage, `k=5` remains a reasonable default because it gives the LLM more context, but the paired tests show why evaluation matters.

## Next Improvements

- Stage 2A has now added hybrid retrieval with BM25 plus semantic retrieval through weighted RRF fusion.
- Stage 3: add confidence-based fallback and calculate first-contact resolution rate across the evaluation set.
