# Design Notes

## Framework

- Use case: customer support assistant for a banking-style support knowledge base.
- Corpus: structured JSON records in `data/raw/banking_support_kb.json`, covering FAQs, past support tickets, product manuals, policies, and escalation runbooks.
- Ingestion and cleaning: source records use `content` plus metadata. The ingestion flow loads the JSON, preserves metadata, chunks the content, embeds chunks, and writes them to Pinecone.
- Ingestion freshness: CLI ingestion resets the namespace by default for reproducible rebuilds. UI ingestion appends pasted JSON records without clearing the namespace.
- Chunking and embedding: `RecursiveCharacterTextSplitter` with `CHUNK_SIZE=500` and `CHUNK_OVERLAP=100`; OpenAI `text-embedding-3-small` with 512 dimensions.
- Retrieval:
  - Simple mode uses Pinecone semantic similarity search.
  - Hybrid mode combines Pinecone semantic retrieval with BM25 keyword retrieval using LangChain `EnsembleRetriever`.
  - Hybrid defaults follow the Week 2 notebook pattern: semantic `k=3`, BM25 `k=3`, weights `[0.5, 0.5]`.
- Generation: OpenAI chat model `gpt-4.1-mini` answers from retrieved context and cites source chunks/records.
- Confidence fallback: Stage 3A adds a context-sufficiency check before answer generation. The bot escalates when fewer than `CONFIDENCE_MIN_SOURCES=2` distinct source records are retrieved, when the assessed confidence is below `CONFIDENCE_THRESHOLD=0.65`, or when the request needs personal account data, transaction changes, approvals, legal advice, or human support action.
- Evaluation: Stage 1 simple RAG tests are documented in `docs/simple_rag_test_results.md`; Stage 2 hybrid retrieval tests are documented in `docs/hybrid_rag_test_results.md`; Stage 3B fallback and first-contact resolution metrics are documented in `docs/evaluation.md`.
- Latency target: local demo should return answers in a few seconds for a small support corpus.
