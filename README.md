# Customer Support Bot

This is the starter workspace for the Week 2 customer support knowledge-base project.

Current state: generic Python scaffold only. Retrieval, generation, escalation logic, and evaluation will be added after the design choices are agreed.

## Project One-Liner Draft

My app helps support agents or customers answer support questions from tickets, FAQs, and product manuals in a chat or internal support UI with grounded answers and human escalation when confidence is low.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run Placeholder CLI

```bash
support-bot --help
```

## Planned Docs

- `docs/design.md`: RAG framework decisions.
- `docs/evaluation.md`: 20-query test set, resolution metrics, and failure notes.
- `data/raw/`: source support documents.
- `data/processed/`: cleaned/intermediate data artifacts.

