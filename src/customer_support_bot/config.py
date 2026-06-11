"""Application configuration helpers."""

from dataclasses import dataclass
from os import getenv

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - package dependency may be absent before setup
    load_dotenv = None


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings that are independent of the RAG design."""

    app_env: str = "local"
    log_level: str = "INFO"


def load_config() -> AppConfig:
    """Load local environment values into a typed config object."""

    if load_dotenv is not None:
        load_dotenv()

    return AppConfig(
        app_env=getenv("APP_ENV", "local"),
        log_level=getenv("LOG_LEVEL", "INFO"),
    )

