from __future__ import annotations

from dataclasses import dataclass
import re


HUNGARIAN_TOKEN_PATTERN = re.compile(
    r"\b("
    r"a|az|és|vagy|mi|mit|melyik|hogyan|hol|mikor|miért|lehet|kell|függvény|"
    r"osztály|mező|táblázat|dokumentum|fejlesztő|üzleti|nyelv|válasz"
    r")\b",
    re.IGNORECASE,
)
HUNGARIAN_ACCENT_PATTERN = re.compile(r"[áéíóöőúüűÁÉÍÓÖŐÚÜŰ]")


@dataclass(slots=True)
class AnswerLanguage:
    code: str
    label: str
    response_instruction: str
    no_evidence_message: str
    provider_failure_message: str
    deterministic_prefix: str


ENGLISH = AnswerLanguage(
    code="en",
    label="English",
    response_instruction="Respond in English.",
    no_evidence_message="Not enough evidence in retrieved context.",
    provider_failure_message="Answer provider failed to produce a grounded answer.",
    deterministic_prefix="Based on the retrieved context,",
)

HUNGARIAN = AnswerLanguage(
    code="hu",
    label="Hungarian",
    response_instruction="Respond in Hungarian.",
    no_evidence_message="Nincs elegendo bizonyitek a visszakeresett kontextusban.",
    provider_failure_message="A valaszado modell nem tudott forrashu valaszt adni.",
    deterministic_prefix="A visszakeresett kontextus alapjan,",
)


def detect_answer_language(query_text: str) -> AnswerLanguage:
    if HUNGARIAN_ACCENT_PATTERN.search(query_text):
        return HUNGARIAN

    if HUNGARIAN_TOKEN_PATTERN.search(query_text):
        return HUNGARIAN

    return ENGLISH
