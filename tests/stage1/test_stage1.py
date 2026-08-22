import tempfile
from pathlib import Path

import pytest
from langchain_core.documents import Document

from stage1_rag_chatbot.db import sql_store
from stage1_rag_chatbot.db.sql_store import (
    find_overlapping_reservations,
    get_reservation_by_id,
    insert_reservation,
    update_reservation_status,
)
from stage1_rag_chatbot.guardrails.pii_filter import redact_pii
from stage1_rag_chatbot.ingestion.chunking_strategies import chunk_documents
from stage1_rag_chatbot.tools.check_reservation_status_tool import _format


@pytest.fixture
def temp_db(monkeypatch):
    """Points sql_store at a throwaway SQLite file for the duration of one test."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = str(Path(tmp_dir) / "test_parking.db")
        monkeypatch.setattr(sql_store, "SQLITE_DB_PATH", db_path)
        sql_store.create_tables()
        yield

#just creating a sample reservation
def _sample_reservation(**overrides):
    reservation = {
        "name": "Test", "surname": "User", "car_number": "TS00AB0000", "zone": "A",
        "start_time": "2026-09-01T10:00:00", "end_time": "2026-09-01T12:00:00",
        "status": "pending", "created_at": "2026-08-22T00:00:00+00:00",
    }
    reservation.update(overrides)
    return reservation

#Seeing how the overlap reservation is working or not
def test_find_overlapping_reservations_detects_true_overlap(temp_db):
    insert_reservation(_sample_reservation())
    conflicts = find_overlapping_reservations("TS00AB0000", "2026-09-01T11:00:00", "2026-09-01T13:00:00")
    assert len(conflicts) == 1

#Seeing whether the resrvation table status is changing for the column or not
def test_update_reservation_status_persists_change(temp_db):
    reservation_id = insert_reservation(_sample_reservation())
    update_reservation_status(reservation_id, "approved")
    assert get_reservation_by_id(reservation_id)["status"] == "approved"

# testing whether the LLM is not leaking the personal info or not
def test_redact_pii_respects_allowlist():
    text = "Reservation confirmed for John Carter. Admin contact: admin@skypark-parking.com."
    result = redact_pii(text, allowlist={"John Carter"})
    assert "John Carter" in result
    assert "admin@skypark-parking.com" not in result

# testing the chunking strategy
def test_chunk_documents_splits_long_text_into_multiple_chunks():
    long_text = "This is a sentence about parking rules. " * 30
    doc = Document(page_content=long_text, metadata={"policy_name": "rules_and_guidelines"})
    chunks = chunk_documents([doc], chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(c.metadata["policy_name"] == "rules_and_guidelines" for c in chunks)


def test_format_translates_awaiting_approval_to_friendly_text():
    reservation = {
        "reservation_id": "abc123", "status": "awaiting_approval",
        "name": "Test", "surname": "User", "car_number": "TS00AB0000", "zone": "A",
        "start_time": "2026-09-01T10:00:00", "end_time": "2026-09-01T12:00:00",
    }
    result = _format(reservation)
    assert "waiting for administrator review" in result
    assert "awaiting_approval" not in result