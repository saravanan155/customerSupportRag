"""Simple semantic RAG retrieval and generation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from customer_support_bot.config import AppConfig
from customer_support_bot.documents import load_knowledge_base


RAG_TEMPLATE = """You are a customer-support assistant for a banking and finance company.
Use the following pieces of retrieved internal knowledge-base context to help resolve the customer's issue.
If the context does not contain the answer, say you do not have that information rather than guessing.
Be concise and practical: state the likely answer and the next step the customer or support agent should take.

Context:
{context}

Customer issue: {question}

Support guidance:"""

RAG_PROMPT = PromptTemplate.from_template(RAG_TEMPLATE)


@dataclass(frozen=True)
class SourceChunk:
    """Small citation-friendly view of a retrieved chunk."""

    title: str
    doc_type: str
    product_area: str
    topic_section: str
    record_id: str
    chunk_index: int | None
    text: str


@dataclass(frozen=True)
class RagAnswer:
    """Generated answer plus the retrieved chunks used as context."""

    question: str
    answer: str
    sources: list[SourceChunk]
    retrieval_mode: str


RetrievalMode = Literal["simple", "hybrid"]


def format_context(documents: list[Document]) -> str:
    """Join retrieved documents into the context format used by the prompt."""

    return "\n\n".join(document.page_content for document in documents)


def source_from_document(document: Document) -> SourceChunk:
    metadata = document.metadata
    return SourceChunk(
        title=metadata.get("title", "(untitled)"),
        doc_type=metadata.get("doc_type", ""),
        product_area=metadata.get("product_area", ""),
        topic_section=metadata.get("topic_section", ""),
        record_id=metadata.get("record_id", ""),
        chunk_index=metadata.get("chunk_index"),
        text=document.page_content,
    )


def format_sources(sources: list[SourceChunk]) -> str:
    """Render sources for CLI output."""

    if not sources:
        return "Sources: none"

    lines = ["Sources:"]
    for index, source in enumerate(sources, start=1):
        chunk_label = ""
        if source.chunk_index is not None:
            chunk_index = int(source.chunk_index)
            chunk_label = f", chunk={chunk_index}"
        lines.append(
            f"{index}. {source.title} "
            f"[id={source.record_id}, {source.doc_type} / "
            f"{source.product_area}{chunk_label}]"
        )
    return "\n".join(lines)


def build_vector_store(config: AppConfig, namespace: str | None = None) -> PineconeVectorStore:
    """Connect to the Pinecone vector store populated by offline ingestion."""

    missing = config.missing_connection_settings()
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")

    pc = Pinecone(api_key=config.pinecone_api_key)
    index = pc.Index(config.pinecone_index_name)
    embeddings = OpenAIEmbeddings(
        model=config.embedding_model,
        dimensions=config.embedding_dimensions,
        api_key=config.openai_api_key,
    )
    return PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=namespace or config.pinecone_namespace,
    )


def build_simple_retriever(
    config: AppConfig,
    *,
    namespace: str | None = None,
    k: int | None = None,
):
    """Build the simple semantic retriever used in Stage 1."""

    vector_store = build_vector_store(config, namespace=namespace)
    return vector_store.as_retriever(
        search_kwargs={"k": k or config.retrieval_top_k},
        search_type="similarity",
    )


def build_hybrid_retriever(
    config: AppConfig,
    *,
    namespace: str | None = None,
    source_path: Path = Path("data/raw/banking_support_kb.json"),
):
    """Build semantic + BM25 hybrid retriever using notebook RRF defaults."""

    vector_store = build_vector_store(config, namespace=namespace)
    vector_retriever = vector_store.as_retriever(
        search_kwargs={"k": config.hybrid_semantic_k},
        search_type="similarity",
    )

    source_docs = load_knowledge_base(source_path)
    bm25_retriever = BM25Retriever.from_documents(source_docs)
    bm25_retriever.k = config.hybrid_bm25_k

    return EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[config.hybrid_semantic_weight, config.hybrid_bm25_weight],
    )


def retrieve_documents(
    config: AppConfig,
    question: str,
    *,
    namespace: str | None = None,
    k: int | None = None,
    retrieval_mode: RetrievalMode = "simple",
) -> list[Document]:
    """Retrieve context documents using the selected retrieval strategy."""

    if retrieval_mode == "simple":
        retriever = build_simple_retriever(config, namespace=namespace, k=k)
    elif retrieval_mode == "hybrid":
        retriever = build_hybrid_retriever(config, namespace=namespace)
    else:
        raise ValueError(f"Unsupported retrieval mode: {retrieval_mode}")

    return retriever.invoke(question)


def answer_question(
    config: AppConfig,
    question: str,
    *,
    namespace: str | None = None,
    k: int | None = None,
    retrieval_mode: RetrievalMode = "simple",
) -> RagAnswer:
    """Retrieve semantically similar chunks and generate a grounded answer."""

    retrieved_docs = retrieve_documents(
        config,
        question,
        namespace=namespace,
        k=k,
        retrieval_mode=retrieval_mode,
    )

    prompt = RAG_PROMPT.invoke(
        {
            "question": question,
            "context": format_context(retrieved_docs),
        }
    )
    llm = ChatOpenAI(
        model=config.chat_model,
        api_key=config.openai_api_key,
        temperature=0,
    )
    response = llm.invoke(prompt)

    return RagAnswer(
        question=question,
        answer=response.content,
        sources=[source_from_document(document) for document in retrieved_docs],
        retrieval_mode=retrieval_mode,
    )
