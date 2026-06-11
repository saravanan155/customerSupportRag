from customer_support_bot.config import AppConfig
from customer_support_bot.connection_checks import check_required_settings


def test_check_required_settings_reports_missing_values():
    config = AppConfig()

    result = check_required_settings(config)

    assert result.ok is False
    assert result.name == "environment"
    assert "OPENAI_API_KEY" in result.detail
    assert "PINECONE_API_KEY" in result.detail
    assert "PINECONE_INDEX_NAME" in result.detail


def test_check_required_settings_passes_when_values_exist():
    config = AppConfig(
        openai_api_key="test-openai-key",
        pinecone_api_key="test-pinecone-key",
        pinecone_index_name="test-index",
    )

    result = check_required_settings(config)

    assert result.ok is True
    assert result.name == "environment"
