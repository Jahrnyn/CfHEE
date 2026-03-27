from cfhee_backend.context_builder import (
    DEFAULT_CONTEXT_CHUNK_LIMIT,
    BuiltContext,
    DroppedContextChunk,
    build_context,
)

DEFAULT_ANSWER_CONTEXT_LIMIT = DEFAULT_CONTEXT_CHUNK_LIMIT
AnswerContext = BuiltContext


def build_answer_context(
    retrieved_chunks,
    retrieval_top_k: int,
    answer_context_limit: int = DEFAULT_ANSWER_CONTEXT_LIMIT,
) -> AnswerContext:
    return build_context(
        retrieved_chunks=retrieved_chunks,
        retrieval_top_k=retrieval_top_k,
        context_chunk_limit=answer_context_limit,
    )
