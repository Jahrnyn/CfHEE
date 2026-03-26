from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from cfhee_backend.retrieval.models import RetrievalQueryRequest, RetrievedChunkMatch
from cfhee_backend.retrieval.service import execute_retrieval


@dataclass(slots=True)
class RegressionCase:
    name: str
    query_text: str
    workspace: str
    domain: str
    top_k: int
    project: str | None = None
    client: str | None = None
    module: str | None = None
    expected_primary_title_substring: str | None = None
    expected_top_title_substring: str | None = None
    expected_text_substring: str | None = None
    match_within_top_n: int = 1


def main() -> int:
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

    passed_count = len(cases) - failures
    print(f"Summary: {passed_count}/{len(cases)} passed")
    return 0 if failures == 0 else 1


def load_cases(fixture_path: Path) -> list[RegressionCase]:
    raw_cases = json.loads(fixture_path.read_text(encoding="utf-8"))
    return [RegressionCase(**raw_case) for raw_case in raw_cases]


def run_case(case: RegressionCase) -> tuple[bool, list[str]]:
    payload = RetrievalQueryRequest(
        query_text=case.query_text,
        workspace=case.workspace,
        domain=case.domain,
        project=case.project,
        client=case.client,
        module=case.module,
        top_k=case.top_k,
    )
    execution = execute_retrieval(payload)
    results = execution.response.results
    inspected_results = results[: max(1, case.match_within_top_n)]
    details = [
        f"query={case.query_text!r}",
        f"scope={case.workspace}/{case.domain}",
        f"returned_results={execution.response.returned_results}",
        f"candidate_count={execution.candidate_count}",
        f"reranking_applied={execution.reranking_applied}",
        f"original_order={execution.original_ranked_chunk_ids}",
        f"reranked_order={execution.reranked_chunk_ids}",
        f"top_results={format_top_results(results)}",
    ]

    if not results:
        details.append("expected=non-empty retrieval result set")
        return False, details

    passed = True

    if case.expected_primary_title_substring:
        top_title = results[0].document.title
        expected = case.expected_primary_title_substring
        matched = expected.lower() in top_title.lower()
        details.append(
            f"check=top1 title contains {expected!r} -> {matched} (top1={top_title!r})"
        )
        passed = passed and matched

    if case.expected_top_title_substring:
        expected = case.expected_top_title_substring
        matched = any(expected.lower() in result.document.title.lower() for result in inspected_results)
        details.append(
            f"check=top{case.match_within_top_n} title contains {expected!r} -> {matched}"
        )
        passed = passed and matched

    if case.expected_text_substring:
        expected = case.expected_text_substring
        matched = any(expected.lower() in result.text.lower() for result in inspected_results)
        details.append(
            f"check=top{case.match_within_top_n} text contains {expected!r} -> {matched}"
        )
        passed = passed and matched

    return passed, details


def format_top_results(results: list[RetrievedChunkMatch], limit: int = 3) -> str:
    top_results = results[:limit]
    if not top_results:
        return "[]"

    parts: list[str] = []
    for result in top_results:
        title = result.document.title.replace("\n", " ")
        parts.append(
            f"#{result.rank} chunk={result.chunk_id} doc={result.document_id} "
            f"title={title!r} distance={result.distance!r} "
            f"vector={result.vector_score!r} lexical={result.lexical_score!r} final={result.final_score!r}"
        )

    return " | ".join(parts)


if __name__ == "__main__":
    raise SystemExit(main())
