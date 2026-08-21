"""One-time (or on-demand) setup: DB tables + fake parking data + policy doc ingestion. """

from stage1_rag_chatbot.db.sql_store import create_tables
from stage1_rag_chatbot.data.generate_fake_data import generate_fake_spaces
from stage1_rag_chatbot.ingestion.ingest_documents import run_ingestion
from shared.logging_utils import get_logger

logger = get_logger(__name__)


def run_bootstrap(force_reingest: bool = False) -> None:
    logger.info("Running Stage 1 bootstrap...")
    create_tables()
    generate_fake_spaces()
    run_ingestion(overwrite=force_reingest)
    logger.info("Bootstrap complete - ready to run main.py")


if __name__ == "__main__":
    run_bootstrap()