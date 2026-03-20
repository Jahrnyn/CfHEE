from cfhee_backend.answers.base import GroundedAnswerInput, GroundedAnswerProvider, GroundedAnswerResult
from cfhee_backend.answers.deterministic_provider import DeterministicLocalAnswerProvider

_answer_provider = DeterministicLocalAnswerProvider()


def get_answer_provider() -> DeterministicLocalAnswerProvider:
    return _answer_provider


__all__ = [
    "GroundedAnswerInput",
    "GroundedAnswerProvider",
    "GroundedAnswerResult",
    "DeterministicLocalAnswerProvider",
    "get_answer_provider",
]
