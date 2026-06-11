"""Application configuration helpers."""

from dataclasses import dataclass, field
from os import getenv

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - package dependency may be absent before setup
    load_dotenv = None


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings loaded from local environment variables."""

    app_env: str = "local"
    log_level: str = "INFO"
    openai_api_key: str | None = field(default=None, repr=False)
    pinecone_api_key: str | None = field(default=None, repr=False)
    pinecone_index_name: str | None = None
    pinecone_namespace: str = "customer-support-simple-rag"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 512
    chunk_size: int = 500
    chunk_overlap: int = 100

    def missing_connection_settings(self) -> list[str]:
        """Return required connection settings that are absent."""

        required_values = {
            "OPENAI_API_KEY": self.openai_api_key,
            "PINECONE_API_KEY": self.pinecone_api_key,
            "PINECONE_INDEX_NAME": self.pinecone_index_name,
        }
        return [name for name, value in required_values.items() if not value]


def _get_int(name: str, default: int) -> int:
    raw_value = getenv(name)
    if raw_value is None or raw_value == "":
        return default
    return int(raw_value)


def load_config(load_env_file: bool = True) -> AppConfig:
    """Load local environment values into a typed config object."""

    if load_env_file and load_dotenv is not None:
        load_dotenv()

    return AppConfig(
        app_env=getenv("APP_ENV", "local"),
        log_level=getenv("LOG_LEVEL", "INFO"),
        openai_api_key=getenv("OPENAI_API_KEY"),
        pinecone_api_key=getenv("PINECONE_API_KEY"),
        pinecone_index_name=getenv("PINECONE_INDEX_NAME"),
        pinecone_namespace=getenv("PINECONE_NAMESPACE", "customer-support-simple-rag"),
        embedding_model=getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        embedding_dimensions=_get_int("EMBEDDING_DIMENSIONS", 512),
        chunk_size=_get_int("CHUNK_SIZE", 500),
        chunk_overlap=_get_int("CHUNK_OVERLAP", 100),
    )
