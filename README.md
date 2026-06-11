# Customer Support Bot

This is the starter workspace for the Week 2 customer support knowledge-base project.

Current state: Stage 1D Streamlit UI for simple RAG.

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
support-bot ingest
support-bot ask "How do I dispute a charge on my card?"
streamlit run src/customer_support_bot/ui.py
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

### Stage 1: Simple RAG

Goal: build the complete simple RAG system before introducing hybrid retrieval.

#### Stage 1A: Setup and Connection Verification

- Added OpenAI + Pinecone dependencies matching the Week 2 notebook direction.
- Added `.env.example` entries for OpenAI, Pinecone, namespace, and embedding defaults.
- Added `support-bot check-connections` to verify:
  - required environment variables are present
  - OpenAI embeddings are reachable
  - Pinecone index exists and is reachable
- No ingestion, retrieval, generation, reranking, or RAG logic was added in this sub-step.

#### Stage 1B: Offline Ingestion

- Added a structured banking support JSON knowledge base at `data/raw/banking_support_kb.json`.
- Corpus includes FAQs, past tickets, product manuals, policies, and a fraud escalation runbook.
- Each record uses course-style `content` + `metadata`, including `doc_type`, `product_area`, `topic_section`, and `topic_description`.
- Added offline ingestion command:

```bash
support-bot ingest
```

- The command loads JSON records, preserves metadata, chunks documents with `RecursiveCharacterTextSplitter`, embeds with OpenAI, and writes chunks to Pinecone.
- Default chunk settings follow the Week 2 notebook pattern:
  - `CHUNK_SIZE=500`
  - `CHUNK_OVERLAP=100`
- By default, ingestion clears the target namespace first for reproducible runs. Use `--append` to upsert without clearing.
- Verified live ingestion result:
  - `source_documents=53`
  - `chunks=100`
  - `namespace=customer-support-simple-rag`
- Confirmed the Pinecone portal shows loaded chunk records with text and metadata; raw vectors are stored but not normally displayed in the portal.

#### Stage 1C: Online Retrieval and Generation

Added simple semantic RAG over the Pinecone namespace populated by offline ingestion.

```bash
support-bot ask "How do I dispute a charge on my card?"
```

- Uses Pinecone semantic similarity search with `RETRIEVAL_TOP_K=5`.
- Uses `CHAT_MODEL=gpt-4.1-mini`, matching the Week 2 notebook pattern.
- Builds a prompt from retrieved chunks and asks the LLM to answer only from context.
- Prints the generated answer plus retrieved source chunk citations, including the original JSON `record_id`.
- Does not add BM25, custom reranking, or confidence fallback yet.
- Verified live query:
  - `support-bot ask "How do I dispute a charge on my card?"`
  - returned a grounded answer with five source chunks from the banking support KB.

#### Stage 1D: Streamlit UI

Added a simple local Streamlit interface over the Stage 1 backend.

```bash
streamlit run src/customer_support_bot/ui.py
```

- Ingestion tab: accepts one pasted JSON record or a JSON list of records, then appends those chunks without clearing the namespace.
- Chat tab: asks questions against the simple semantic RAG namespace and displays source chunks with original JSON `record_id`.
- The UI intentionally supports only the current JSON schema for now; Markdown, CSV, PDF, and multi-format uploads are later enhancements.
- Full rebuild/reset ingestion remains available through the CLI with `support-bot ingest`.

### Stage 2: Hybrid RAG

Planned next stage after simple RAG works end to end: add BM25 keyword retrieval and a user-selectable simple vs. hybrid retrieval mode.

### Stage 3: Fallback and Evaluation

Planned final stage: add confidence-based human escalation and measure first-contact resolution rate across the 20-query evaluation set.
