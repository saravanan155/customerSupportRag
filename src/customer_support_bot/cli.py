"""Command-line entrypoint for local project checks."""

import argparse
from pathlib import Path

from customer_support_bot import __version__
from customer_support_bot.connection_checks import run_connection_checks
from customer_support_bot.config import load_config
from customer_support_bot.indexing import ingest_knowledge_base
from customer_support_bot.rag import answer_question, format_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Customer support bot project CLI.")
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the project version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser(
        "check-connections",
        help="Verify OpenAI and Pinecone setup without running RAG.",
    )
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Run offline ingestion: load, chunk, embed, and write KB to Pinecone.",
    )
    ingest_parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/raw/banking_support_kb.json"),
        help="Path to the JSON knowledge base.",
    )
    ingest_parser.add_argument(
        "--namespace",
        default=None,
        help="Pinecone namespace. Defaults to PINECONE_NAMESPACE.",
    )
    ingest_parser.add_argument(
        "--chunk-size",
        type=int,
        default=None,
        help="Chunk size. Defaults to CHUNK_SIZE.",
    )
    ingest_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=None,
        help="Chunk overlap. Defaults to CHUNK_OVERLAP.",
    )
    ingest_parser.add_argument(
        "--append",
        action="store_true",
        help="Append/upsert without clearing the namespace first.",
    )
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a question using simple semantic RAG.",
    )
    ask_parser.add_argument("question", help="Customer/support question to answer.")
    ask_parser.add_argument(
        "--namespace",
        default=None,
        help="Pinecone namespace. Defaults to PINECONE_NAMESPACE.",
    )
    ask_parser.add_argument(
        "--k",
        type=int,
        default=None,
        help="Number of chunks to retrieve. Defaults to RETRIEVAL_TOP_K.",
    )
    ask_parser.add_argument(
        "--retrieval",
        choices=["simple", "hybrid"],
        default="simple",
        help="Retrieval mode. Hybrid uses semantic + BM25 fusion.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    config = load_config()

    if args.command == "check-connections":
        results = run_connection_checks(config)
        for result in results:
            status = "OK" if result.ok else "FAIL"
            print(f"[{status}] {result.name}: {result.detail}")
        if not all(result.ok for result in results):
            raise SystemExit(1)
        return

    if args.command == "ingest":
        result = ingest_knowledge_base(
            config,
            args.source,
            namespace=args.namespace,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            reset_namespace=not args.append,
        )
        reset_label = "reset" if result.reset_namespace else "append"
        print(
            "Ingestion complete: "
            f"source_documents={result.source_documents}, "
            f"chunks={result.chunks}, "
            f"namespace='{result.namespace}', "
            f"mode={reset_label}"
        )
        return

    if args.command == "ask":
        result = answer_question(
            config,
            args.question,
            namespace=args.namespace,
            k=args.k,
            retrieval_mode=args.retrieval,
        )
        print(f"Retrieval mode: {result.retrieval_mode}")
        print(f"Status: {result.confidence.status}")
        print(
            "Confidence: "
            f"{result.confidence.score:.2f} "
            f"(threshold={result.confidence.threshold:.2f}, "
            f"sources={result.confidence.unique_source_count})"
        )
        print(f"Reason: {result.confidence.reason}")
        print()
        print(result.answer)
        print()
        print(format_sources(result.sources))
        return

    print(f"Project scaffold ready. env={config.app_env} log_level={config.log_level}")


if __name__ == "__main__":
    main()
