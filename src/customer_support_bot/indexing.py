"""Offline ingestion pipeline for Pinecone-backed simple RAG."""

from dataclasses import dataclass
from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone
from pinecone.exceptions import NotFoundException

from customer_support_bot.config import AppConfig
from customer_support_bot.documents import load_knowledge_base, parse_records_json, records_to_documents


@dataclass(frozen=True)
class IngestionResult:
    """Summary of an offline ingestion run."""

    source_path: Path
    namespace: str
    source_documents: int
    chunks: int
    reset_namespace: bool


def chunk_documents(
    documents: list[Document],
    chunk_size: int,
    chunk_overlap: int,
) -> list[Document]:
    """Split source documents into focused chunks using notebook defaults."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index
    return chunks


def _chunk_ids(chunks: list[Document]) -> list[str]:
    ids = []
    for chunk in chunks:
        record_id = chunk.metadata["record_id"]
        chunk_index = chunk.metadata["chunk_index"]
        ids.append(f"{record_id}::chunk-{chunk_index:04d}")
    return ids


def ingest_knowledge_base(
    config: AppConfig,
    source_path: Path,
    *,
    namespace: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    reset_namespace: bool = True,
) -> IngestionResult:
    """Load, chunk, embed, and write the knowledge base to Pinecone."""

    documents = load_knowledge_base(source_path)
    return ingest_documents(
        config,
        documents,
        source_path=source_path,
        namespace=namespace,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        reset_namespace=reset_namespace,
    )


def ingest_json_text(
    config: AppConfig,
    raw_json: str,
    *,
    namespace: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> IngestionResult:
    """Append pasted JSON records to Pinecone without clearing the namespace."""

    documents = records_to_documents(parse_records_json(raw_json))
    return ingest_documents(
        config,
        documents,
        source_path=Path("pasted-json"),
        namespace=namespace,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        reset_namespace=False,
    )


def ingest_documents(
    config: AppConfig,
    documents: list[Document],
    *,
    source_path: Path,
    namespace: str | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    reset_namespace: bool = True,
) -> IngestionResult:
    """Chunk, embed, and write already-loaded documents to Pinecone."""

    missing = config.missing_connection_settings()
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")

    active_namespace = namespace or config.pinecone_namespace
    active_chunk_size = chunk_size or config.chunk_size
    active_chunk_overlap = chunk_overlap or config.chunk_overlap

    chunks = chunk_documents(
        documents,
        chunk_size=active_chunk_size,
        chunk_overlap=active_chunk_overlap,
    )

    pc = Pinecone(api_key=config.pinecone_api_key)
    index = pc.Index(config.pinecone_index_name)
    if reset_namespace:
        try:
            index.delete(delete_all=True, namespace=active_namespace)
        except NotFoundException:
            pass

    embeddings = OpenAIEmbeddings(
        model=config.embedding_model,
        dimensions=config.embedding_dimensions,
        api_key=config.openai_api_key,
    )
    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=active_namespace,
    )
    vector_store.add_documents(chunks, ids=_chunk_ids(chunks))

    return IngestionResult(
        source_path=source_path,
        namespace=active_namespace,
        source_documents=len(documents),
        chunks=len(chunks),
        reset_namespace=reset_namespace,
    )
