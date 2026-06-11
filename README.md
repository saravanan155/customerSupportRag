# Customer Support Bot

This is the starter workspace for the Week 2 customer support knowledge-base project.

Current state: Stage 1 setup and connection verification.

## Project One-Liner Draft

My app helps support agents or customers answer support questions from tickets, FAQs, and product manuals in a chat or internal support UI with grounded answers and human escalation when confidence is low.

## Local Setup

```bash
source .venv/bin/activate
python --version
```

Expected Python version: `3.12.x`.

Copy `.env.example` to `.env` and fill in your local values:

```bash
cp .env.example .env
```

Required for Stage 1:

- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`
- `PINECONE_NAMESPACE`, optional; defaults to `customer-support-simple-rag`

## Run CLI

```bash
support-bot --version
support-bot check-connections
```

## Planned Docs

- `docs/design.md`: RAG framework decisions.
- `docs/evaluation.md`: 20-query test set, resolution metrics, and failure notes.
- `data/raw/`: source support documents.
- `data/processed/`: cleaned/intermediate data artifacts.

## Development Stages

### Stage 0: Project Scaffold

- Created Python package layout under `src/customer_support_bot`.
- Added CLI placeholder, typed config loader, docs placeholders, tests, and `.gitignore`.
- Created first checkpoint commit.

### Stage 1: Setup and Connection Verification

- Added OpenAI + Pinecone dependencies matching the Week 2 notebook direction.
- Added `.env.example` entries for OpenAI, Pinecone, namespace, and embedding defaults.
- Added `support-bot check-connections` to verify:
  - required environment variables are present
  - OpenAI embeddings are reachable
  - Pinecone index exists and is reachable
- No ingestion, retrieval, generation, reranking, or RAG logic has been added yet.
