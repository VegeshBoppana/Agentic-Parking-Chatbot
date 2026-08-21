"""Centralized environment and config loader for the whole project."""

from pathlib import Path
from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _get_env(key: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(key, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


OPENAI_API_KEY = _get_env("OPENAI_API_KEY", required=True)
OPENAI_CHAT_MODEL = _get_env("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDING_MODEL = _get_env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_MAX_TOKENS = int(_get_env("OPENAI_MAX_TOKENS", "400"))


MILVUS_URI = _get_env("MILVUS_URI", "http://localhost:19530")
SQLITE_DB_PATH = str(PROJECT_ROOT / _get_env("SQLITE_DB_PATH", "stage1_rag_chatbot/db/parking.db"))


TRULENS_DB_PATH = str(PROJECT_ROOT / _get_env("TRULENS_DB_PATH", "stage1_rag_chatbot/observability/trulens.db"))

ENV = _get_env("ENV", "development")

GMAIL_SENDER_EMAIL = _get_env("GMAIL_SENDER_EMAIL", required=True)
GMAIL_APP_PASSWORD = _get_env("GMAIL_APP_PASSWORD", required=True)
ADMIN_EMAIL = _get_env("ADMIN_EMAIL", required=True)

HITL_CHECKPOINT_DB_PATH = str(PROJECT_ROOT / _get_env("HITL_CHECKPOINT_DB_PATH", "stage2_hitl_agent/hitl_checkpoints.db"))
HITL_API_BASE_URL = _get_env("HITL_API_BASE_URL", "http://localhost:8000")