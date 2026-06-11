"""Connection checks for external services used by the RAG project."""

from dataclasses import dataclass

from customer_support_bot.config import AppConfig


@dataclass(frozen=True)
class ConnectionCheckResult:
    """Result of a single setup check."""

    name: str
    ok: bool
    detail: str


def check_required_settings(config: AppConfig) -> ConnectionCheckResult:
    missing = config.missing_connection_settings()
    if missing:
        return ConnectionCheckResult(
            name="environment",
            ok=False,
            detail=f"Missing required settings: {', '.join(missing)}",
        )
    return ConnectionCheckResult(
        name="environment",
        ok=True,
        detail="Required settings are present.",
    )


def check_openai_embeddings(config: AppConfig) -> ConnectionCheckResult:
    """Verify the OpenAI embedding model can produce the expected vector size."""

    try:
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(
            model=config.embedding_model,
            dimensions=config.embedding_dimensions,
            api_key=config.openai_api_key,
        )
        vector = embeddings.embed_query("connection check")
    except Exception as exc:  # pragma: no cover - covered by live CLI use
        return ConnectionCheckResult(
            name="openai",
            ok=False,
            detail=f"Embedding check failed: {exc}",
        )

    vector_size = len(vector)
    if vector_size != config.embedding_dimensions:
        return ConnectionCheckResult(
            name="openai",
            ok=False,
            detail=(
                f"Expected {config.embedding_dimensions} dimensions, "
                f"received {vector_size}."
            ),
        )

    return ConnectionCheckResult(
        name="openai",
        ok=True,
        detail=f"Embedding model reachable; vector size={vector_size}.",
    )


def check_pinecone_index(config: AppConfig) -> ConnectionCheckResult:
    """Verify the configured Pinecone index exists and is reachable."""

    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=config.pinecone_api_key)
        index_names = [index.name for index in pc.list_indexes()]
    except Exception as exc:  # pragma: no cover - covered by live CLI use
        return ConnectionCheckResult(
            name="pinecone",
            ok=False,
            detail=f"Pinecone check failed: {exc}",
        )

    if config.pinecone_index_name not in index_names:
        return ConnectionCheckResult(
            name="pinecone",
            ok=False,
            detail=(
                f"Index '{config.pinecone_index_name}' was not found. "
                f"Available indexes: {', '.join(index_names) or '(none)'}."
            ),
        )

    return ConnectionCheckResult(
        name="pinecone",
        ok=True,
        detail=(
            f"Index '{config.pinecone_index_name}' reachable; "
            f"namespace='{config.pinecone_namespace}'."
        ),
    )


def check_nebius_confidence_model(config: AppConfig) -> ConnectionCheckResult:
    """Verify the Nebius confidence model is reachable when configured."""

    if config.confidence_provider.lower() != "nebius":
        return ConnectionCheckResult(
            name="nebius",
            ok=True,
            detail="Skipped; CONFIDENCE_PROVIDER is not 'nebius'.",
        )

    if not config.nebius_api_key:
        return ConnectionCheckResult(
            name="nebius",
            ok=False,
            detail="NEBIUS_API_KEY is required when CONFIDENCE_PROVIDER=nebius.",
        )

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=config.nebius_api_key,
            base_url=config.nebius_base_url,
        )
        response = client.chat.completions.create(
            model=config.nebius_confidence_model,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Return only JSON: "
                        '{"answerable": true, "confidence": 1, "reason": "ok"}'
                    ),
                }
            ],
            temperature=0,
        )
    except Exception as exc:  # pragma: no cover - covered by live CLI use
        return ConnectionCheckResult(
            name="nebius",
            ok=False,
            detail=f"Nebius confidence check failed: {exc}",
        )

    content = response.choices[0].message.content or ""
    return ConnectionCheckResult(
        name="nebius",
        ok=True,
        detail=(
            "Confidence model reachable via Nebius Token Factory; "
            f"response_preview={content[:80]!r}."
        ),
    )


def run_connection_checks(config: AppConfig) -> list[ConnectionCheckResult]:
    """Run setup checks in dependency order."""

    results = [check_required_settings(config)]
    if not results[-1].ok:
        return results

    results.append(check_openai_embeddings(config))
    results.append(check_pinecone_index(config))
    results.append(check_nebius_confidence_model(config))
    return results
