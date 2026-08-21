from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from shared.logging_utils import get_logger

logger = get_logger(__name__)

POLICIES_DIR = Path(__file__).resolve().parent.parent / "data" / "policies"


def load_policy_documents() -> list[Document]:
    """Loads every PDF from policies folder and tags each page with its source doc name."""
    docs: list[Document] = []

    pdf_files = sorted(POLICIES_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDFs found in {POLICIES_DIR}")

    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        for page in pages:
            page.metadata["policy_name"] = pdf_path.stem
        docs.extend(pages)
        logger.info(f"Loaded {pdf_path.name} ({len(pages)} page(s))")

    return docs