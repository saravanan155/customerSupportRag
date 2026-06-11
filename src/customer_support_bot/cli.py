"""Command-line entrypoint for local project checks."""

import argparse

from customer_support_bot import __version__
from customer_support_bot.connection_checks import run_connection_checks
from customer_support_bot.config import load_config


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

    print(f"Project scaffold ready. env={config.app_env} log_level={config.log_level}")


if __name__ == "__main__":
    main()
