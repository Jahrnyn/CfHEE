from cfhee_backend.embeddings.hash_embedding import HashEmbeddingService

_embedding_service = HashEmbeddingService()


def get_embedding_service() -> HashEmbeddingService:
    return _embedding_service
