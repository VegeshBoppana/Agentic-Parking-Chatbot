from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from stage2_hitl_agent.notify import send_email
from stage2_hitl_agent.tools import wait_for_decision_tool
from stage2_hitl_agent.tools.send_admin_notification_tool import AdminNotificationContent, send_admin_notification


def _sample_reservation(reservation_id="abc123"):
    return {
        "reservation_id": reservation_id, "name": "Test", "surname": "User",
        "car_number": "TS00AB0000", "zone": "A",
        "start_time": "2026-09-01T10:00:00", "end_time": "2026-09-01T12:00:00",
    }


def test_urls_are_built_in_code_not_from_llm_input():
    with patch("stage2_hitl_agent.tools.send_admin_notification_tool.send_email") as mock_send:
        send_admin_notification.invoke({
            "reservation_id": "abc123", "subject": "Test subject",
            "greeting": "Hello", "reservation_summary": "Test summary", "closing": "Thanks",
        })
    body = mock_send.call_args.args[1]
    assert "reservations/abc123/approve" in body
    assert "reservations/abc123/reject" in body


def test_schema_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        AdminNotificationContent(reservation_id="abc123", subject="s", greeting="g", reservation_summary="r")


def test_approve_updates_status_and_writes_confirmed_file(monkeypatch):
    monkeypatch.setattr(wait_for_decision_tool, "interrupt", lambda payload: "approve")
    status_calls = []
    monkeypatch.setattr(wait_for_decision_tool, "update_reservation_status",
                         lambda rid, status: status_calls.append((rid, status)))
    monkeypatch.setattr(wait_for_decision_tool, "get_reservation_by_id",
                         lambda rid: _sample_reservation(rid))
    write_calls = []
    monkeypatch.setattr(wait_for_decision_tool, "write_confirmed_reservation",
                         lambda **kwargs: write_calls.append(kwargs))

    wait_for_decision_tool.wait_for_admin_decision.invoke({"reservation_id": "abc123"})

    assert status_calls == [("abc123", "approved")]
    assert len(write_calls) == 1


def test_reject_updates_status_without_writing_file(monkeypatch):
    monkeypatch.setattr(wait_for_decision_tool, "interrupt", lambda payload: "reject")
    status_calls = []
    monkeypatch.setattr(wait_for_decision_tool, "update_reservation_status",
                         lambda rid, status: status_calls.append((rid, status)))
    write_calls = []
    monkeypatch.setattr(wait_for_decision_tool, "write_confirmed_reservation",
                         lambda **kwargs: write_calls.append(kwargs))

    wait_for_decision_tool.wait_for_admin_decision.invoke({"reservation_id": "abc123"})

    assert status_calls == [("abc123", "rejected")]
    assert write_calls == []


def test_send_email_calls_smtp_login_and_send():
    with patch("stage2_hitl_agent.notify.smtplib.SMTP_SSL") as mock_smtp_cls:
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_server
        send_email("Test subject", "Test body")
    mock_server.login.assert_called_once()
    mock_server.send_message.assert_called_once()