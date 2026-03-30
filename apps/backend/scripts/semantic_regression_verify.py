from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

from cfhee_backend.embeddings import get_embedding_runtime_summary, reset_embedding_service
from cfhee_backend.embeddings.ollama_embedding import OllamaEmbeddingService
from cfhee_backend.ingestion.models import DocumentCreate
from cfhee_backend.ingestion.service import create_document, delete_document
from cfhee_backend.persistence.database import get_connection
from cfhee_backend.vector_store import reset_vector_store
from retrieval_regression_check import load_cases, run_case


DOCUMENT_SOURCE_REF_PREFIX = "semantic-regression/"


@dataclass(slots=True)
class VerificationDocument:
    source_type: str
    title: str
    language: str | None
    source_ref: str
    workspace: str
    domain: str
    raw_text: str


def main() -> int:
    args = parse_args()
    configure_embedding_defaults()

    ensure_semantic_embedding_runtime()
    cleanup_existing_verification_documents()
    created_document_ids = ingest_verification_documents()

    try:
        failures = run_regression_pack()
    finally:
        if args.keep_data:
            print("")
            print("Verification data kept in local dev storage.")
            print(f"source_ref prefix={DOCUMENT_SOURCE_REF_PREFIX!r}")
            print(f"document_ids={created_document_ids}")
        else:
            cleanup_existing_verification_documents()

    return 0 if failures == 0 else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a tiny semantic verification corpus, run the existing retrieval regression pack, and optionally clean up.",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        help="Keep the ingested semantic verification documents instead of deleting them after the run.",
    )
    return parser.parse_args()


def configure_embedding_defaults() -> None:
    os.environ.setdefault("EMBEDDING_PROVIDER", "ollama")
    os.environ.setdefault("EMBEDDING_MODEL", "bge-m3")
    reset_embedding_service()
    reset_vector_store()


def ensure_semantic_embedding_runtime() -> None:
    runtime_summary = get_embedding_runtime_summary()
    print("Embedding runtime summary:")
    print(runtime_summary)

    if runtime_summary.get("provider_selection") != "ollama":
        raise RuntimeError(
            f"Semantic verification requires EMBEDDING_PROVIDER=ollama, got {runtime_summary.get('provider_selection')!r}."
        )

    if runtime_summary.get("model") != "bge-m3":
        raise RuntimeError(
            f"Semantic verification requires EMBEDDING_MODEL='bge-m3', got {runtime_summary.get('model')!r}."
        )

    provider = OllamaEmbeddingService()
    is_available, reason = provider.is_available()
    if not is_available:
        raise RuntimeError(reason or "Ollama embedding runtime is unavailable.")

    print("Ollama embedding runtime is reachable and bge-m3 is available.")
    print("")


def ingest_verification_documents() -> list[int]:
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "semantic_regression_documents.json"
    documents = [
        VerificationDocument(**item)
        for item in json.loads(fixture_path.read_text(encoding="utf-8"))
    ]

    print(f"Semantic verification corpus: {fixture_path}")
    print(f"Documents: {len(documents)}")

    created_document_ids: list[int] = []
    for document in documents:
        created = create_document(
            DocumentCreate(
                workspace=document.workspace,
                domain=document.domain,
                project=None,
                client=None,
                module=None,
                source_type=document.source_type,
                title=document.title,
                raw_text=document.raw_text,
                language=document.language,
                source_ref=document.source_ref,
            )
        )
        created_document_ids.append(created.id)
        print(f"  ingested document_id={created.id} title={created.title!r}")

    print("")
    return created_document_ids


def cleanup_existing_verification_documents() -> None:
    document_ids = find_existing_verification_document_ids()
    if not document_ids:
        return

    print(f"Cleaning semantic verification documents: {document_ids}")
    for document_id in document_ids:
        delete_document(document_id)

    reset_vector_store()
    print("")


def find_existing_verification_document_ids() -> list[int]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM documents
                WHERE source_ref LIKE %(source_ref_prefix)s
                ORDER BY id ASC
                """,
                {"source_ref_prefix": f"{DOCUMENT_SOURCE_REF_PREFIX}%"},
            )
            rows = cursor.fetchall()

    return [int(row["id"]) for row in rows]


def run_regression_pack() -> int:
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "retrieval_regression_cases.json"
    cases = load_cases(fixture_path)
    failures = 0

    print(f"Retrieval regression pack: {fixture_path}")
    print(f"Cases: {len(cases)}")
    print("")

    for case in cases:
        passed, details = run_case(case)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {case.name}")
        for line in details:
            print(f"  {line}")
        print("")
        if not passed:
            failures += 1

    print(f"Summary: {len(cases) - failures}/{len(cases)} passed")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
