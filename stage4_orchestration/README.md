# Stage 4 - Orchestration (Unified Pipeline)

## Setup

1. Add to `.env` (project root):

ORCHESTRATOR_CHECKPOINT_DB_PATH=./stage4_orchestration/orchestrator_checkpoints.db
ORCHESTRATOR_API_BASE_URL=http://localhost:8001

2. Install dependencies (from the project root):
```powershell
   poetry install
```
3. Make sure Milvus is running (Stage 1 dependency):
```powershell
   docker compose up -d etcd minio standalone
```

## Usage

Start the approval API server (must be running for the email's Approve/Reject links to work):
```powershell
poetry run uvicorn stage4_orchestration.api:app --port 8001
```

In a separate terminal, start the chat loop:
```powershell
poetry run python -m stage4_orchestration.main
```

Chat naturally, and book a reservation in one message, e.g.:
Book a reservation for John Doe, car number TS01AB1234, Zone A, from 2026-08-25 10:00 to 2026-08-25 11:00


The administrator approves/rejects by clicking the link in the notification email. Approval automatically triggers Stage 3's file write.

**Visualizing the graph (optional):** `poetry run langgraph dev` opens LangGraph Studio, showing all 4 nodes and their routing. Note: Studio uses its own internal state storage, separate from `orchestrator_checkpoints.db` - it's for inspecting graph structure and logic only, not for testing the real end-to-end email-approval flow (use `main.py` + `api.py` for that).

## Structure

**`state.py`** — `OrchestratorState`: the shared state (`messages`, `reservation`, `decision`) that flows through every node.

**`graph.py`** — builds the actual `StateGraph`: wires all 4 nodes together, defines routing, compiles with the persistent checkpointer.

**`main.py`** — the customer-facing CLI chat loop, entry point for real end-to-end testing.

**`api.py`** — FastAPI server behind the email's Approve/Reject links; resumes the paused orchestrator graph when clicked.

**`studio_graph.py`** — exposes the graph for LangGraph Studio visualization only (no custom checkpointer - Studio manages its own).

**`nodes/user_interaction.py`** — Node 1: runs Stage 1's chatbot, detects if a reservation was just submitted, saves the thread ID against it for later resume.

**`nodes/administrator_approval.py`** — Node 2: composes and sends the admin notification email (reused logic from Stage 2).

**`nodes/wait_for_decision.py`** — Node 3: pauses (`interrupt()`) until the admin's decision arrives, then records it.

**`nodes/data_recording.py`** — Node 4: on approval, writes the confirmed reservation via Stage 3's MCP agent.