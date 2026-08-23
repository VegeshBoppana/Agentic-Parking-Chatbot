# Parking Reservation Chatbot

An intelligent chatbot for a parking facility (SkyPark), built across 4 stages:

1. **Stage 1 - RAG Chatbot** (`stage1_rag_chatbot/`): answers parking questions via RAG over
   policy documents (Milvus), checks live availability/price (SQLite), collects reservations,
   and lets customers check reservation status. Traced with LangSmith, evaluated with RAG
   Triad + IR metrics.
2. **Stage 2 - Human-in-the-Loop Agent** (`stage2_hitl_agent/`): a second agent that composes
   and sends an admin approval email, then pauses until the admin responds.
3. **Stage 3 - MCP Server** (`stage3_mcp_server/`): writes approved reservations to a file via
   the Model Context Protocol.
4. **Stage 4 - LangGraph Orchestration** (`stage4_orchestration/`): wires Stages 1-3 into one
   unified `StateGraph` pipeline - this is the main entry point for the finished system.

## Setup

```powershell
poetry install
copy .env.example .env   # fill in OpenAI key, LangSmith key, Gmail credentials
docker compose up -d etcd minio standalone   # Milvus, for Stage 1's policy search
poetry run python -m stage1_rag_chatbot.bootstrap   # one-time: DB tables, fake data, policy PDFs into Milvus
```

## Usage - Web UI (recommended)

The whole system (Stages 1-4 wired together) is reachable through a simple browser chat window.

```powershell
poetry run uvicorn stage4_orchestration.api:app --port 8001
```

Then open **http://localhost:8001** in your browser and chat directly - book a reservation,
check its status, ask about parking policies. When a reservation is submitted, an email is
sent to the administrator with Approve/Reject links; clicking one completes the flow and
writes the confirmed reservation to `stage3_mcp_server/data/confirmed_reservations.txt`.

## Usage - CLI (alternative)

```powershell
poetry run uvicorn stage4_orchestration.api:app --port 8001   # still needed for approve/reject links
poetry run python -m stage4_orchestration.main
```

## Usage - individual stages

Each stage can also be run and tested independently - see that stage's own `README.md`
(`stage1_rag_chatbot/README.md`, `stage2_hitl_agent/README.md`, `stage3_mcp_server/README.md`,
`stage4_orchestration/README.md`) for setup/usage specific to it.

## Tests

```powershell
poetry run pytest tests/ -v
```
