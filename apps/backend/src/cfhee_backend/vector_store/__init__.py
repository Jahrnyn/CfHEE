from cfhee_backend.vector_store.chroma_adapter import ChromaVectorStore

_vector_store = ChromaVectorStore()


def get_vector_store() -> ChromaVectorStore:
    return _vector_store
