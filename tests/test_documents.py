import json

import pytest

from customer_support_bot.documents import (
    load_knowledge_base,
    normalize_content,
    parse_records_json,
    records_to_documents,
)


def test_normalize_content_collapses_extra_blank_lines():
    assert normalize_content(" hello\r\n\r\n\r\nworld ") == "hello\n\nworld"


def test_load_knowledge_base_preserves_metadata(tmp_path):
    source = tmp_path / "kb.json"
    source.write_text(
        json.dumps(
            [
                {
                    "id": "faq-test-001",
                    "content": "Question: Test?\n\nAnswer: Yes.",
                    "metadata": {
                        "title": "Test?",
                        "doc_type": "faq",
                        "product_area": "account_management",
                        "priority": "P2",
                        "platform": "web",
                        "customer_tier": "all",
                        "status": "active",
                        "source": "unit-test",
                        "topic_section": "Account Management",
                        "topic_description": "Unit test topic.",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    documents = load_knowledge_base(source)

    assert len(documents) == 1
    assert documents[0].page_content == "Question: Test?\n\nAnswer: Yes."
    assert documents[0].metadata["record_id"] == "faq-test-001"
    assert documents[0].metadata["topic_section"] == "Account Management"


def test_load_knowledge_base_rejects_missing_metadata(tmp_path):
    source = tmp_path / "kb.json"
    source.write_text(
        json.dumps([{"id": "bad", "content": "Missing metadata.", "metadata": {}}]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="metadata missing fields"):
        load_knowledge_base(source)


def test_parse_records_json_accepts_single_record_object():
    raw_records = parse_records_json(
        json.dumps(
            {
                "id": "faq-test-001",
                "content": "Question: Test?\n\nAnswer: Yes.",
                "metadata": {
                    "title": "Test?",
                    "doc_type": "faq",
                    "product_area": "account_management",
                    "priority": "P2",
                    "platform": "web",
                    "customer_tier": "all",
                    "status": "active",
                    "source": "unit-test",
                    "topic_section": "Account Management",
                    "topic_description": "Unit test topic.",
                },
            }
        )
    )

    documents = records_to_documents(raw_records)

    assert len(documents) == 1
    assert documents[0].metadata["record_id"] == "faq-test-001"


def test_parse_records_json_rejects_non_record_json():
    with pytest.raises(ValueError, match="list of records"):
        parse_records_json('"not a record"')
