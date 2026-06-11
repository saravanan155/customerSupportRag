# Customer Support Bot

This is the completed workspace for the Week 2 customer support knowledge-base project.

Current state: Stage 3C Nebius-backed confidence fallback for the support RAG bot.

## Project One-Liner Draft

My app helps support agents or customers answer banking support questions from FAQs, past tickets, product manuals, policies, and runbooks in a CLI or Streamlit chat UI with grounded citations, confidence-based human escalation, 75% bot-only first-contact resolution, and 100% safe handling on the 20-query evaluation set.

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

Required for the core RAG pipeline:

- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`
- `PINECONE_NAMESPACE`, optional; defaults to `customer-support-simple-rag`

Required for final submission:

- `NEBIUS_API_KEY`, used for the Stage 3 confidence/fallback model call
- set `CONFIDENCE_PROVIDER=nebius` after adding the Nebius key

## Run CLI

```bash
support-bot --version
support-bot check-connections
support-bot ingest
support-bot ask "How do I dispute a charge on my card?"
support-bot ask "How do I dispute a charge on my card?" --retrieval hybrid
support-bot ask "What is my account balance?" --retrieval hybrid
streamlit run src/customer_support_bot/ui.py
```

## Project Docs

- `docs/design.md`: RAG framework decisions.
- `docs/submission_writeup.md`: final project narrative for submission.
- `docs/simple_rag_test_results.md`: Stage 1 simple RAG showcase results.
- `docs/hybrid_rag_test_results.md`: Stage 2 hybrid RAG showcase results.
- `docs/fallback_rag_test_results.md`: detailed Stage 3 fallback showcase results.
- `docs/evaluation.md`: Stage 3 confidence fallback results, resolution metrics, and failure notes.
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

Added hybrid retrieval using the Week 2 hybrid RAG notebook pattern.

```bash
support-bot ask "How long do ACH transfers take?" --retrieval hybrid
```

- Simple mode keeps Pinecone semantic similarity retrieval.
- Hybrid mode combines Pinecone semantic retrieval with BM25 keyword retrieval.
- Fusion uses LangChain `EnsembleRetriever` with weighted RRF.
- Defaults follow the training notebook:
  - semantic `k=3`
  - BM25 `k=3`
  - weights `[0.5, 0.5]`
- Streamlit Chat tab uses a radio button to choose `simple` or `hybrid`.
- BM25 is built from the source JSON records to match the notebook pattern, while Pinecone retrieves stored chunks. Because of that, hybrid citations may include both chunk-level citations and source-record-level citations.
- Stage 2B validation is documented in `docs/hybrid_rag_test_results.md` using the same 20 support questions from the simple RAG showcase.

### Stage 3: Fallback and Evaluation

#### Stage 3A: Confidence-Based Fallback

Added a context-sufficiency check before answer generation.

- Retrieves sources using the selected simple or hybrid retrieval mode.
- Counts distinct source records as a basic evidence signal.
- Uses the chat model to assess whether the retrieved context is sufficient to answer safely.
- Returns an escalation response instead of generating an answer when:
  - fewer than `CONFIDENCE_MIN_SOURCES=2` distinct source records are retrieved
  - the assessed confidence is below `CONFIDENCE_THRESHOLD=0.65`
  - the question requires personal account data, transaction changes, approvals, legal advice, or human support action
- CLI output now includes status, confidence score, threshold, source count, and reason.
- Streamlit Chat tab shows answered vs escalated status above the response.

#### Stage 3B: Resolution Metrics

Ran the 20-query evaluation set with hybrid retrieval and confidence fallback enabled.

- 15 answerable support questions were answered correctly.
- 5 account-specific, action-taking, or advice requests were escalated safely.
- Overall bot-only first-contact resolution rate: `15 / 20 = 75%`.
- Answerable-query first-contact resolution rate: `15 / 15 = 100%`.
- Safe handling rate, counting correct answers and correct escalations: `20 / 20 = 100%`.
- Full metrics are documented in `docs/evaluation.md`; detailed answer/citation results are documented in `docs/fallback_rag_test_results.md`.

#### Stage 3C: Nebius Token Factory Confidence Call

Added Nebius Token Factory as the model provider for the confidence assessment step.

- The main RAG pipeline still uses OpenAI embeddings, Pinecone retrieval, and OpenAI answer generation.
- The confidence/fallback check can now use Nebius through its OpenAI-compatible API.
- Configure with:
  - `CONFIDENCE_PROVIDER=nebius`
  - `NEBIUS_API_KEY`
  - `NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/`
  - `NEBIUS_CONFIDENCE_MODEL=Qwen/Qwen3-235B-A22B-Instruct-2507`
- Run `support-bot check-connections` after adding `NEBIUS_API_KEY`; it now verifies the Nebius confidence model when `CONFIDENCE_PROVIDER=nebius`.
- This satisfies the Week 2 handout requirement to use Nebius Token Factory for at least one model call while keeping the tested retrieval and answer-generation path stable.
