"""Streamlit UI for the customer support RAG system."""

import streamlit as st

from customer_support_bot.config import load_config
from customer_support_bot.indexing import ingest_json_text
from customer_support_bot.rag import answer_question


SCHEMA_EXAMPLE = """[
  {
    "id": "faq-cards-004",
    "content": "Question: How do I dispute a charge on my card?\\n\\nAnswer:\\n...",
    "metadata": {
      "title": "How do I dispute a charge on my card?",
      "doc_type": "faq",
      "product_area": "cards",
      "priority": "P1",
      "platform": "web_mobile",
      "customer_tier": "all",
      "status": "active",
      "source": "banking_support_kb.md",
      "topic_section": "Debit & Credit Cards",
      "topic_description": "Activation, disputes, limits, and declined transactions."
    }
  }
]"""


def render_sidebar() -> None:
    config = load_config()
    st.sidebar.header("Configuration")
    st.sidebar.caption("Values are read from your local `.env`; secrets are not shown.")
    st.sidebar.text_input("Pinecone index", value=config.pinecone_index_name or "", disabled=True)
    st.sidebar.text_input("Namespace", value=config.pinecone_namespace, disabled=True)
    st.sidebar.text_input("Embedding model", value=config.embedding_model, disabled=True)
    st.sidebar.text_input("Chat model", value=config.chat_model, disabled=True)


def render_ingestion_tab() -> None:
    st.subheader("Ingestion")
    st.caption("Paste JSON records, chunk them, embed them, and append them to Pinecone.")

    with st.expander("Required JSON format", expanded=False):
        st.code(SCHEMA_EXAMPLE, language="json")
        st.markdown(
            "Required top-level fields: `id`, `content`, `metadata`. "
            "Required metadata fields: `title`, `doc_type`, `product_area`, `priority`, "
            "`platform`, `customer_tier`, `status`, `source`, `topic_section`, "
            "`topic_description`."
        )

    config = load_config()
    namespace = st.text_input("Pinecone namespace", value=config.pinecone_namespace)

    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.number_input(
            "Chunk size",
            min_value=100,
            max_value=2000,
            value=config.chunk_size,
            step=50,
        )
    with col2:
        chunk_overlap = st.number_input(
            "Chunk overlap",
            min_value=0,
            max_value=500,
            value=config.chunk_overlap,
            step=25,
        )

    st.markdown("#### Add knowledge base records")
    st.caption("Paste one JSON record or a JSON list of records. Existing vectors are not cleared.")
    pasted_json = st.text_area(
        "JSON records to append",
        value="",
        height=260,
        placeholder=SCHEMA_EXAMPLE,
    )

    if st.button("Append to vector database", type="primary"):
        if not pasted_json.strip():
            st.warning("Paste a JSON record or list of records first.")
            return
        try:
            with st.spinner("Appending pasted records to Pinecone..."):
                result = ingest_json_text(
                    config,
                    pasted_json,
                    namespace=namespace,
                    chunk_size=int(chunk_size),
                    chunk_overlap=int(chunk_overlap),
                )
            st.success("Append complete")
            m1, m2 = st.columns(2)
            m1.metric("Appended source docs", result.source_documents)
            m2.metric("Appended chunks", result.chunks)
            st.caption(f"Namespace: `{result.namespace}`")
        except Exception as exc:
            st.error(f"Append failed: {exc}")


def render_chat_tab() -> None:
    st.subheader("Chat")
    st.caption("Ask questions against the support RAG index.")

    config = load_config()
    namespace = st.text_input(
        "Namespace",
        value=config.pinecone_namespace,
        key="chat_namespace",
    )
    retrieval_mode = st.radio(
        "Retrieval mode",
        options=["simple", "hybrid"],
        horizontal=True,
        help="Hybrid uses semantic search plus BM25 keyword search with RRF fusion.",
    )
    k = None
    if retrieval_mode == "simple":
        k = st.slider(
            "Retrieved chunks",
            min_value=1,
            max_value=10,
            value=config.retrieval_top_k,
        )
    else:
        st.caption(
            "Hybrid defaults: semantic k=3, BM25 k=3, weights=[0.5, 0.5]."
        )

    question = st.text_area(
        "Question",
        value="How do I dispute a charge on my card?",
        height=100,
    )

    if st.button("Ask", type="primary"):
        if not question.strip():
            st.warning("Enter a question first.")
            return
        try:
            with st.spinner("Retrieving context and generating answer..."):
                result = answer_question(
                    config,
                    question.strip(),
                    namespace=namespace,
                    k=k,
                    retrieval_mode=retrieval_mode,
                )
            st.caption(f"Retrieval mode: `{result.retrieval_mode}`")
            if result.confidence.status == "answered":
                st.success(
                    f"Answered with confidence {result.confidence.score:.2f} "
                    f"(threshold {result.confidence.threshold:.2f})"
                )
            else:
                st.warning(
                    f"Escalated with confidence {result.confidence.score:.2f} "
                    f"(threshold {result.confidence.threshold:.2f})"
                )
            st.caption(
                f"Confidence reason: {result.confidence.reason} "
                f"| Distinct sources: {result.confidence.unique_source_count}"
            )
            st.markdown("#### Answer")
            st.write(result.answer)

            st.markdown("#### Sources")
            for index, source in enumerate(result.sources, start=1):
                chunk_label = ""
                if source.chunk_index is not None:
                    chunk_label = f" · chunk {int(source.chunk_index)}"
                with st.expander(
                    f"{index}. {source.title} "
                    f"({source.record_id}{chunk_label})",
                    expanded=index == 1,
                ):
                    st.caption(
                        f"{source.doc_type} / {source.product_area} / "
                        f"{source.topic_section}"
                    )
                    st.write(source.text)
        except Exception as exc:
            st.error(f"Question failed: {exc}")


def main() -> None:
    st.set_page_config(page_title="Customer Support RAG", layout="wide")
    st.title("Customer Support RAG")
    st.caption("Hybrid retrieval with confidence-based fallback.")

    render_sidebar()
    ingestion_tab, chat_tab = st.tabs(["Ingestion", "Chat"])
    with ingestion_tab:
        render_ingestion_tab()
    with chat_tab:
        render_chat_tab()


if __name__ == "__main__":
    main()
