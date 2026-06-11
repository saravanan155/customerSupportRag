# Week 2 Project Submission Writeup

## Project Overview

This project implements **Project 4: Customer Support Knowledge Base with Hybrid Search**.

The application is a banking-style customer support RAG bot that answers support questions from a structured knowledge base and escalates when the retrieved evidence is not safe enough to answer. It supports both CLI usage and a local Streamlit UI.

One-liner:

> My app helps support agents or customers answer banking support questions from FAQs, past tickets, product manuals, policies, and runbooks in a CLI or Streamlit chat UI with grounded citations, confidence-based human escalation, 75% bot-only first-contact resolution, and 100% safe handling on the 20-query evaluation set.

## Dataset

The knowledge base is stored in `data/raw/banking_support_kb.json`.

It includes:

- FAQs
- past support tickets
- product manuals
- policies
- escalation runbooks

The corpus covers account management, cards, transfers, loans, digital banking, security/fraud, fees, and ATM/branch services. Each record contains `content` plus metadata such as `doc_type`, `product_area`, `topic_section`, `priority`, `platform`, and `record_id`.

## Architecture

Offline ingestion:

1. Load structured JSON support records.
2. Convert records to LangChain `Document` objects.
3. Chunk with `RecursiveCharacterTextSplitter`.
4. Embed chunks with OpenAI `text-embedding-3-small`.
5. Store vectors and metadata in Pinecone.

Online RAG:

1. User asks a support question.
2. The app retrieves context using either simple semantic retrieval or hybrid retrieval.
3. Hybrid retrieval combines Pinecone semantic search with BM25 keyword search using weighted RRF.
4. A confidence check decides whether the retrieved context is sufficient.
5. If confident, the app generates a grounded answer with citations.
6. If not confident, the app escalates to a human support agent.

## Model Calls

- OpenAI embeddings are used during ingestion.
- OpenAI embeddings are used during semantic retrieval.
- Nebius Token Factory is used for the confidence/fallback model call when `CONFIDENCE_PROVIDER=nebius`.
- OpenAI chat generation is used for the final answer when the confidence check allows an answer.

This satisfies the Week 2 requirement to use Nebius Token Factory for at least one model call while keeping the tested retrieval and answer-generation behavior stable.

## User Interface

The Streamlit UI supports:

- append-only JSON ingestion into Pinecone
- simple vs hybrid retrieval selection
- customer question input
- answer display
- answered vs escalated status
- confidence provider display
- confidence reason and citations

## Evaluation

The final fallback-enabled evaluation uses 20 real-world-style support questions:

- 15 answerable questions
- 5 escalation-required questions

Results:

- Answered correctly: 15
- Escalated correctly: 5
- Incorrect answers: 0
- Missed escalations: 0
- Overall bot-only first-contact resolution rate: 75%
- Answerable-query first-contact resolution rate: 100%
- Safe handling rate: 100%

Detailed results are documented in:

- `docs/evaluation.md`
- `docs/fallback_rag_test_results.md`

## Iterations

Stage 1 built a complete simple RAG pipeline:

- setup and connection checks
- JSON knowledge base
- ingestion, cleanup, chunking, embedding, and Pinecone loading
- semantic retrieval
- grounded answer generation
- Streamlit UI

Stage 2 added hybrid retrieval:

- BM25 keyword search
- Pinecone semantic search
- weighted RRF fusion through `EnsembleRetriever`
- simple vs hybrid selection in the UI
- hybrid retrieval evaluation

Stage 3 added safety and evaluation:

- confidence-based fallback
- human escalation logic
- first-contact resolution metrics
- detailed 20-query fallback results
- Nebius Token Factory for the confidence model call

## AI Coding Workflow

The project was built through pair-programming prompts focused on learning rather than copying a finished solution.

Prompt themes included:

- choosing the RAG project and design approach
- creating a staged implementation plan
- building a JSON knowledge base from a starter Markdown FAQ
- implementing offline ingestion first
- implementing online retrieval and generation next
- adding Streamlit only after the CLI path worked
- comparing simple and hybrid retrieval
- adding confidence fallback and escalation behavior
- documenting evaluation results and final metrics
- checking the handout for missing submission requirements

## Learnings

- Hybrid retrieval improves exact-term matching for support phrases such as ACH, HELOC, and policy names.
- Hybrid fusion can still include noisy tail citations, so retrieval ranking alone is not enough for customer support safety.
- Confidence fallback is essential because some user requests require account access, approvals, or human judgment.
- First-contact resolution and safe handling are different metrics. Escalating correctly may reduce bot-only FCR, but it protects customer trust.
- Keeping the work in staged commits made it easier to preserve working checkpoints and explain the system evolution.

## Demo Recording Outline

Suggested 5-minute demo flow:

1. Show the README and project one-liner.
2. Run `support-bot check-connections`.
3. Show the Streamlit ingestion tab and JSON schema.
4. Ask an answerable question, such as `How do I dispute a charge on my card?`.
5. Show the answer, citations, confidence provider, and confidence reason.
6. Ask an escalation question, such as `What is my account balance?`.
7. Show the human escalation response.
8. Open `docs/evaluation.md` and summarize the FCR and safe handling metrics.
