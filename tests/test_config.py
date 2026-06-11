from customer_support_bot.config import AppConfig, load_config


def test_load_config_returns_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    config = load_config()

    assert config == AppConfig(app_env="local", log_level="INFO")

