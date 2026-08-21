## This file consists of Milvus connection, collection, insert, search

from langchain_milvus import Milvus

from shared.config import MILVUS_URI
from shared.llm import get_embedding_model

COLLECTION_NAME = "parking_policies"

_vector_store: Milvus | None = None


def get_vector_store(drop_old: bool = False) -> Milvus:
    """Cached connection for normal use. drop_old=True rebuilds the collection
    from scratch - only used for a one-off re-ingestion, bypasses the cache."""
    global _vector_store
    if drop_old:
        return Milvus(
            embedding_function=get_embedding_model(),
            collection_name=COLLECTION_NAME,
            connection_args={"uri": MILVUS_URI},
            auto_id=True,
            drop_old=True,
        )
    if _vector_store is None:
        _vector_store = Milvus(
            embedding_function=get_embedding_model(),
            collection_name=COLLECTION_NAME,
            connection_args={"uri": MILVUS_URI},
            auto_id=True,
        )
    return _vector_store


def insert_chunks(chunks: list, overwrite: bool = False) -> None:
    get_vector_store(drop_old=overwrite).add_documents(chunks)


def search(query: str, top_k: int = 5):
    """Returns real Document objects - the plain similarity_search() call is
    what TruLens recognizes and auto-tags as a retrieval span."""
    return get_vector_store().similarity_search(query=query, k=top_k)