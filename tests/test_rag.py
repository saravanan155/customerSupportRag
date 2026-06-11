from langchain_core.documents import Document

from customer_support_bot.rag import (
    RAG_PROMPT,
    format_context,
    format_sources,
    source_from_document,
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
