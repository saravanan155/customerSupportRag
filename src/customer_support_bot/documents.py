"""Knowledge-base document loading utilities."""

import json
import re
from pathlib import Path
from typing import Any

from langchain_core.documents import Document


REQUIRED_METADATA_FIELDS = {
    "title",
    "doc_type",
    "product_area",
    "priority",
    "platform",
    "customer_tier",
    "status",
    "source",
    "topic_section",
    "topic_description",
}


def normalize_content(content: str) -> str:
    """Normalize whitespace while preserving paragraph and list structure."""

    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized


def _validate_record(record: dict[str, Any], index: int) -> None:
    if not record.get("id"):
        raise ValueError(f"Record {index} is missing required field: id")
    if not record.get("content"):
        raise ValueError(f"Record {index} is missing required field: content")
    metadata = record.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"Record {index} is missing required object: metadata")
    missing = REQUIRED_METADATA_FIELDS - set(metadata)
    if missing:
        missing_fields = ", ".join(sorted(missing))
        raise ValueError(f"Record {index} metadata missing fields: {missing_fields}")


def load_knowledge_base(path: Path) -> list[Document]:
    """Load the project JSON knowledge base into LangChain documents."""

    raw_records = json.loads(path.read_text(encoding="utf-8"))
    return records_to_documents(raw_records)


def parse_records_json(raw_json: str) -> list[dict[str, Any]]:
    """Parse pasted JSON as either one record object or a list of records."""

    raw_records = json.loads(raw_json)
    if isinstance(raw_records, dict):
        raw_records = [raw_records]
    if not isinstance(raw_records, list):
        raise ValueError("Knowledge base JSON must contain a list of records.")
    return raw_records


def records_to_documents(raw_records: list[dict[str, Any]]) -> list[Document]:
    """Convert validated knowledge-base records into LangChain documents."""

    documents = []
    for index, record in enumerate(raw_records):
        if not isinstance(record, dict):
            raise ValueError(f"Record {index} must be a JSON object.")
        _validate_record(record, index)
        metadata = dict(record["metadata"])
        metadata["record_id"] = record["id"]
        documents.append(
            Document(
                page_content=normalize_content(record["content"]),
                metadata=metadata,
            )
        )
    return documents
