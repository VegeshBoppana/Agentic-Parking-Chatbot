from stage1_rag_chatbot.ingestion.loaders import load_policy_documents
from stage1_rag_chatbot.ingestion.chunking_strategies import chunk_documents
from stage1_rag_chatbot.db.vector_store import insert_chunks
from shared.logging_utils import get_logger

logger = get_logger(__name__)


def run_ingestion(overwrite: bool = True) -> None:
    documents = load_policy_documents()
    logger.info(f"Loaded {len(documents)} document page(s)")

    chunks = chunk_documents(documents)
    logger.info(f"Split into {len(chunks)} chunk(s)")

    insert_chunks(chunks, overwrite=overwrite)
    logger.info("Ingestion complete")


if __name__ == "__main__":
    run_ingestion()