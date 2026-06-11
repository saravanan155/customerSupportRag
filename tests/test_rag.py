from langchain_core.documents import Document

from customer_support_bot.rag import (
    CONFIDENCE_PROMPT,
    RAG_PROMPT,
    format_context,
    format_sources,
    parse_json_object,
    parse_confidence_response,
    retrieve_documents,
    source_from_document,
    unique_source_count,
)


def test_format_context_joins_document_content():
    documents = [
        Document(page_content="First chunk.", metadata={}),
        Document(page_content="Second chunk.", metadata={}),
    ]

    assert format_context(documents) == "First chunk.\n\nSecond chunk."


def test_source_from_document_uses_metadata():
    document = Document(
        page_content="Chunk text.",
        metadata={
            "title": "Dispute a charge",
            "doc_type": "faq",
            "product_area": "cards",
            "topic_section": "Debit & Credit Cards",
            "record_id": "faq-cards-004",
            "chunk_index": 20,
        },
    )

    source = source_from_document(document)

    assert source.title == "Dispute a charge"
    assert source.doc_type == "faq"
    assert source.product_area == "cards"
    assert source.topic_section == "Debit & Credit Cards"
    assert source.record_id == "faq-cards-004"
    assert source.chunk_index == 20
    assert source.text == "Chunk text."


def test_format_sources_renders_citation_list():
    source = source_from_document(
        Document(
            page_content="Chunk text.",
            metadata={
                "title": "Dispute a charge",
                "doc_type": "faq",
                "product_area": "cards",
                "record_id": "faq-cards-004",
                "chunk_index": 20,
            },
        )
    )

    rendered = format_sources([source])

    assert "Sources:" in rendered
    assert "Dispute a charge [id=faq-cards-004, faq / cards, chunk=20]" in rendered


def test_format_sources_renders_float_chunk_indexes_as_ints():
    source = source_from_document(
        Document(
            page_content="Chunk text.",
            metadata={
                "title": "Dispute a charge",
                "doc_type": "faq",
                "product_area": "cards",
                "record_id": "faq-cards-004",
                "chunk_index": 20.0,
            },
        )
    )

    assert "chunk=20]" in format_sources([source])


def test_rag_prompt_includes_context_and_question():
    prompt = RAG_PROMPT.invoke(
        {
            "context": "Known policy text.",
            "question": "What is the policy?",
        }
    )

    prompt_text = prompt.text
    assert "Known policy text." in prompt_text
    assert "What is the policy?" in prompt_text
    assert "rather than guessing" in prompt_text


def test_confidence_prompt_requests_json_assessment():
    prompt = CONFIDENCE_PROMPT.invoke(
        {
            "context": "Known policy text.",
            "question": "What is the policy?",
        }
    )

    prompt_text = prompt.text
    assert "Return only valid JSON" in prompt_text
    assert "answerable" in prompt_text
    assert "confidence" in prompt_text


def test_unique_source_count_uses_distinct_record_ids():
    documents = [
        Document(page_content="Chunk A", metadata={"record_id": "faq-1"}),
        Document(page_content="Chunk B", metadata={"record_id": "faq-1"}),
        Document(page_content="Chunk C", metadata={"record_id": "manual-1"}),
    ]

    assert unique_source_count(documents) == 2


def test_parse_confidence_response_returns_answered_status():
    assessment = parse_confidence_response(
        '{"answerable": true, "confidence": 0.82, "reason": "Enough policy context."}',
        unique_sources=3,
        threshold=0.65,
        min_sources=2,
    )

    assert assessment.status == "answered"
    assert assessment.answerable is True
    assert assessment.score == 0.82
    assert assessment.unique_source_count == 3


def test_parse_confidence_response_handles_fenced_json():
    assessment = parse_confidence_response(
        '```json\n{"answerable": true, "confidence": 0.9, "reason": "Enough."}\n```',
        unique_sources=2,
        threshold=0.65,
        min_sources=2,
    )

    assert assessment.status == "answered"
    assert assessment.score == 0.9


def test_parse_confidence_response_escalates_below_threshold():
    assessment = parse_confidence_response(
        '{"answerable": true, "confidence": 0.42, "reason": "Weak context."}',
        unique_sources=2,
        threshold=0.65,
        min_sources=2,
    )

    assert assessment.status == "escalated"
    assert assessment.score == 0.42


def test_parse_confidence_response_treats_false_string_as_false():
    assessment = parse_confidence_response(
        '{"answerable": "false", "confidence": 0.95, "reason": "Needs account data."}',
        unique_sources=2,
        threshold=0.65,
        min_sources=2,
    )

    assert assessment.status == "escalated"
    assert assessment.answerable is False
    assert assessment.score == 0


def test_parse_confidence_response_escalates_on_invalid_json():
    assessment = parse_confidence_response(
        "not json",
        unique_sources=2,
        threshold=0.65,
        min_sources=2,
    )

    assert assessment.status == "escalated"
    assert assessment.score == 0
    assert assessment.answerable is False


def test_parse_json_object_rejects_non_object_json():
    try:
        parse_json_object("[1, 2, 3]")
    except ValueError as exc:
        assert "JSON object" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-object JSON.")


def test_retrieve_documents_rejects_unknown_mode():
    try:
        retrieve_documents(None, "question", retrieval_mode="unknown")
    except ValueError as exc:
        assert "Unsupported retrieval mode" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown retrieval mode.")
