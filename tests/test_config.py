from customer_support_bot.config import AppConfig, load_config


def test_load_config_returns_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_INDEX_NAME", raising=False)
    monkeypatch.delenv("PINECONE_NAMESPACE", raising=False)
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    monkeypatch.delenv("EMBEDDING_DIMENSIONS", raising=False)
    monkeypatch.delenv("CHAT_MODEL", raising=False)
    monkeypatch.delenv("RETRIEVAL_TOP_K", raising=False)
    monkeypatch.delenv("HYBRID_SEMANTIC_K", raising=False)
    monkeypatch.delenv("HYBRID_BM25_K", raising=False)
    monkeypatch.delenv("HYBRID_SEMANTIC_WEIGHT", raising=False)
    monkeypatch.delenv("HYBRID_BM25_WEIGHT", raising=False)
    monkeypatch.delenv("CONFIDENCE_THRESHOLD", raising=False)
    monkeypatch.delenv("CONFIDENCE_MIN_SOURCES", raising=False)

    config = load_config(load_env_file=False)

    assert config == AppConfig(
        app_env="local",
        log_level="INFO",
        openai_api_key=None,
        pinecone_api_key=None,
        pinecone_index_name=None,
        pinecone_namespace="customer-support-simple-rag",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=512,
        chat_model="gpt-4.1-mini",
        retrieval_top_k=5,
        hybrid_semantic_k=3,
        hybrid_bm25_k=3,
        hybrid_semantic_weight=0.5,
        hybrid_bm25_weight=0.5,
        confidence_threshold=0.65,
        confidence_min_sources=2,
        chunk_size=500,
        chunk_overlap=100,
    )


def test_missing_connection_settings(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("PINECONE_API_KEY", raising=False)
    monkeypatch.delenv("PINECONE_INDEX_NAME", raising=False)

    config = load_config(load_env_file=False)

    assert config.missing_connection_settings() == [
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
    ]
