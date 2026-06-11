from langchain_core.documents import Document

from customer_support_bot.indexing import chunk_documents


def test_chunk_documents_adds_start_and_chunk_indexes():
    documents = [
        Document(
            page_content="alpha beta gamma " * 30,
            metadata={"record_id": "doc-001", "title": "Chunk test"},
        )
    ]

    chunks = chunk_documents(documents, chunk_size=80, chunk_overlap=10)

    assert len(chunks) > 1
    assert chunks[0].metadata["record_id"] == "doc-001"
    assert chunks[0].metadata["chunk_index"] == 0
    assert "start_index" in chunks[0].metadata
