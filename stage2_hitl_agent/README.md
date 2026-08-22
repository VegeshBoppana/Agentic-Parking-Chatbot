# Stage 2 - Human-in-the-Loop Agent

## Setup

1. Generate a Gmail App Password (a normal password won't work for SMTP):
   - Enable 2-Step Verification: https://myaccount.google.com/security
   - Create an app password: https://myaccount.google.com/apppasswords
2. Add to `.env` (project root):
GMAIL_SENDER_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx
ADMIN_EMAIL=your.email@gmail.com
HITL_CHECKPOINT_DB_PATH=./stage2_hitl_agent/hitl_checkpoints.db
HITL_API_BASE_URL=http://localhost:8000

3. Install dependencies (from project root):
```powershell
   poetry install
```

## Usage

Start the approval API server (must be running for the "Approve"/"Reject" email links to work):
```powershell
poetry run uvicorn stage2_hitl_agent.api:app --port 8000
```

Escalation itself is automatic - it's triggered directly from Stage 1 the moment a customer submits a reservation (`stage1_rag_chatbot.main`). Nothing needs to be run manually to start it.

The administrator approves or rejects by clicking the corresponding link in the notification email.

Run the tests:
```powershell
poetry run pytest tests/stage2 -v
```

## Structure

**`agent.py`** — builds the second agent (`create_agent` with the two tools below) and exposes `escalate_reservation()` (called by Stage 1) and `resume_approval()` (called by the API).

**`api.py`** — the FastAPI server behind the email's Approve/Reject links; resumes the paused agent when clicked.

**`notify.py`** — sends the actual email over Gmail SMTP (raw sending only; content is composed by the agent).

**`tools/send_admin_notification_tool.py`** — the tool the agent calls to compose (Pydantic-structured) and send the notification email.

**`tools/wait_for_decision_tool.py`** — the tool that pauses the agent until a decision arrives, then records it and triggers Stage 3's file write on approval.