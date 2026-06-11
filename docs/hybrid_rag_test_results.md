# Hybrid RAG Test Results

## Scope

This document captures a manual showcase test of the current Stage 2B hybrid RAG system.

Topic: **Hybrid RAG with semantic retrieval + BM25 keyword retrieval using weighted RRF fusion**

Current behavior:

- Retrieval method: Pinecone semantic similarity search plus BM25 keyword search
- Fusion method: LangChain `EnsembleRetriever` using weighted reciprocal rank fusion
- Hybrid defaults:
  - semantic `k=3`
  - BM25 `k=3`
  - weights `[0.5, 0.5]`
- Embedding model: `text-embedding-3-small`
- Embedding dimensions: `512`
- Chat model: `gpt-4.1-mini`
- Knowledge base namespace: `customer-support-simple-rag`
- Corpus: `data/raw/banking_support_kb.json`
- Citation trace: hybrid results can include both Pinecone chunk-level citations and BM25 source-record-level citations

Limitations intentionally left for later stages:

- No separate cross-encoder, LLM, or external reranking model
- No explicit confidence score
- No automated human-escalation fallback
- No official first-contact resolution metric yet

## Test Summary

The test set reuses the same 20 real-world-style banking support questions from the simple RAG showcase.

| # | Question | Hybrid Answer Summary | Hybrid Citations | Notes |
|---|---|---|---|---|
| 1 | How do I dispute a charge on my card? | Explains how to use Account Activity, choose Dispute this transaction, submit a reason/documents, and gives expected resolution/provisional credit timing. | `faq-cards-004`, `faq-cards-002`, `faq-loans_mortgages-004`, `manual-cards-001`, `faq-cards-001` | Exact FAQ is first. Some unrelated keyword matches appear after the strongest citation. |
| 2 | My debit card is declined while traveling internationally. What should I check? | Checks active/frozen status, international transaction controls, travel notice, spending limit, and fraud block support. | `faq-cards-002`, `manual-cards-001`, `ticket-cards-1001` | Strong result. Hybrid combines FAQ, card manual, and past ticket evidence. |
| 3 | How long do ACH transfers take? | States ACH transfers usually take 1-3 business days and mentions same-day ACH availability/cost/limit. | `faq-transfers_payments-002`, `faq-transfers_payments-003`, `manual-transfers-payments-001`, `faq-transfers_payments-005` | Improvement over simple RAG: exact ACH timing FAQ is first. |
| 4 | What is the difference between ACH and wire transfers? | Compares timing, cost, limits, reversibility, and when to use ACH versus wire. | `faq-transfers_payments-003`, `faq-loans_mortgages-005`, `faq-transfers_payments-002`, `faq-account_management-004`, `manual-transfers-payments-001`, `faq-transfers_payments-005` | Exact comparison FAQ is first. Some unrelated source-record matches show why confidence/reranking still matters. |
| 5 | I clicked a suspicious bank text link and entered my password. What should I do? | Advises official password reset, fraud support call, card freeze, transaction review, avoiding links, and Fraud Operations escalation. | `faq-security_fraud-002`, `faq-digital_banking-002`, `faq-security_fraud-001`, `ticket-security-fraud-1004`, `ticket-transfers-payments-1003` | Strong operational answer. Includes phishing FAQ plus escalated fraud ticket, with a few keyword-adjacent sources. |
| 6 | Can I pay off my personal loan early without a penalty? | Confirms no prepayment penalty and explains payoff as principal plus accrued interest; includes online/phone payoff options. | `faq-loans_mortgages-004`, `ticket-loans-mortgages-1006`, `faq-account_management-005` | Strong match. Past ticket supports the exact FAQ. |
| 7 | How do I deposit a check using the mobile app? | Gives step-by-step mobile deposit flow, endorsement requirement, availability timing, and rejection troubleshooting. | `faq-digital_banking-005`, `manual-digital-banking-001`, `ticket-digital-banking-1002`, `faq-digital_banking-004` | Strong result. Hybrid retrieves FAQ, manual, and past ticket evidence. |
| 8 | Why was my account frozen or restricted? | Lists suspected fraud, negative balance, legal hold, and identity verification as reasons; gives branch/phone next steps. | `faq-account_management-006`, `ticket-cards-1001`, `ticket-account-management-1007`, `ticket-atm-branch-1008` | Exact frozen-account FAQ is first, with useful account ticket context and some less relevant ticket noise. |
| 9 | What are the overdraft fees and how can I avoid them? | Lists overdraft, daily maximum, extended overdraft, linked-savings transfer fee, and avoidance options. | `faq-fees_interest-002`, `policy-fees-interest-001`, `ticket-fees-interest-1005` | Strong result. Hybrid pulls exact FAQ, policy, and past fee ticket. |
| 10 | How do I set up two-factor authentication? | Provides the Security menu path, method choices, verification steps, and notes where 2FA is required. | `faq-digital_banking-003`, `faq-security_fraud-002`, `faq-transfers_payments-004`, `faq-security_fraud-004`, `policy-transfers-payments-001` | Exact 2FA FAQ is first. Later citations are related security/payment context. |
| 11 | What documents are required to open a personal account? | Lists photo ID, SSN/ITIN, proof of address, and deposit details; includes online/mobile/branch next steps. | `faq-account_management-002`, `faq-account_management-001`, `faq-account_management-004` | Strong result. Exact account-opening requirements are first. |
| 12 | How do I update my address or phone number? | Gives online, mobile, phone, and branch options plus digital and physical-mail timing. | `faq-account_management-003`, `faq-digital_banking-002`, `faq-cards-002`, `faq-digital_banking-001` | Exact FAQ is first. Extra login/card citations are adjacent but not essential. |
| 13 | How do I report a lost or stolen card? | Gives mobile, online, and phone reporting options, immediate card block, replacement timing, and address-verification note. | `faq-cards-003`, `faq-cards-010`, `ticket-cards-1009`, `manual-cards-001`, `faq-cards-004` | Strong result. Also retrieved the new UI-ingested replacement-card address record. |
| 14 | What are the daily transfer limits? | Lists own-account, ACH, same-day ACH, domestic wire, Zelle, and Bill Pay limits plus support contact for higher limits. | `faq-transfers_payments-005`, `manual-digital-banking-001`, `faq-fees_interest-001`, `faq-transfers_payments-001`, `faq-cards-002` | Exact limits FAQ is first. Some unrelated citations remain in the tail. |
| 15 | How do I set up direct deposit? | Explains routing/account numbers, employer form, pre-filled form download, and 1-2 pay-cycle timing. | `faq-transfers_payments-004`, `faq-digital_banking-003`, `faq-cards-001`, `faq-loans_mortgages-001` | Exact direct-deposit FAQ is first. Additional keyword matches are not needed for the final answer. |
| 16 | What is a HELOC and how does it work? | Defines HELOC, borrowing against home equity, 85% appraised-value formula, variable rate, draw period, repayment period, and tax note. | `faq-loans_mortgages-005`, `faq-transfers_payments-003`, `faq-loans_mortgages-001`, `policy-fees-interest-001` | Exact HELOC FAQ is first. Keyword overlap pulls in some unrelated finance records later. |
| 17 | What mobile app features are available? | Lists balances, history, mobile deposit, transfers, Zelle, Bill Pay, card management, loans/mortgages, locator, insights, documents, and secure messaging. | `faq-digital_banking-004`, `faq-security_fraud-004`, `manual-cards-001`, `faq-fees_interest-002` | Strong answer from exact FAQ. Tail citations show broad keyword matches. |
| 18 | What is the Zero Liability Policy? | Defines zero liability and explains debit/credit timing differences and reporting urgency. | `faq-security_fraud-003`, `faq-security_fraud-002`, `faq-cards-003` | Strong result. Exact policy FAQ is first and repeated through chunk/source evidence. |
| 19 | How do I find a fee-free ATM? | Gives mobile locator, website locator, text option, and out-of-network fee warning. | `faq-atm_branch-001`, `ticket-atm-branch-1008`, `faq-cards-004`, `ticket-fees-interest-1005` | Exact ATM FAQ is first. Fee-related ticket adds context; card dispute FAQ is noise. |
| 20 | What services are available at a branch? | Lists account services, notary, safe deposit boxes, medallion guarantee, cashier's checks, currency exchange, advisor appointments, loan applications, and hours. | `faq-atm_branch-002`, `faq-cards-002`, `faq-account_management-001`, `faq-transfers_payments-002` | Exact branch-services FAQ is first. Tail citations are keyword-adjacent but not necessary. |

## Simple vs Hybrid Observations

| Question Type | Simple RAG Behavior | Hybrid RAG Behavior | Takeaway |
|---|---|---|---|
| Exact product acronyms, such as ACH and HELOC | Usually answered correctly, but exact source was not always first. | Often promoted exact keyword-bearing FAQ records earlier. | BM25 helps with product acronyms and policy terms. |
| Operational support flows, such as disputes, fraud, mobile deposit, and overdraft | Retrieved strong semantic matches and useful supporting evidence. | Retrieved similar strong matches, often with source-record and chunk-level duplicates. | Hybrid maintains answer quality, but citations can be noisier. |
| Policy or fee questions | Good answers when semantic match was clear. | Pulled policy/ticket records more consistently for some questions. | Hybrid can improve evidence diversity. |
| Broad questions, such as mobile app features or branch services | Usually retrieved the exact FAQ first. | Exact FAQ stayed first, but keyword overlap added unrelated tail citations. | Stage 3 should avoid treating every retrieved citation as equally trustworthy. |

## Stage 2B Conclusion

Hybrid retrieval is working and is useful for the showcase because it combines semantic meaning with exact keyword matching. It especially helped the ACH timing question by moving the exact ACH FAQ to the top citation.

The main limitation is that weighted RRF is a fusion ranking method, not a dedicated reranker or confidence model. It can still include unrelated tail citations. Stage 3 should use evidence quality signals to decide whether to answer confidently or escalate to a human support agent.
