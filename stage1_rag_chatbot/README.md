# Stage 1 - RAG Chatbot

## Setup

1. Install dependencies:
```powershell
   poetry install
```
2. Copy the environment template and fill in your values (OpenAI key, LangSmith key, Gmail credentials):
```powershell
   copy .env.example .env
```
3. Start Milvus (Docker):
```powershell
   docker compose up -d etcd minio standalone
```
   Wait for `docker compose ps` to show all three as `(healthy)`.
4. Run one-time setup (creates DB tables, fake parking spaces, loads policy PDFs into Milvus):
```powershell
   poetry run python -m stage1_rag_chatbot.bootstrap
```

## Usage

Run the chatbot:
```powershell
poetry run python -m stage1_rag_chatbot.main
```
Type a message, get a reply. Type `exit` or `quit` to leave.

Run the tests:
```powershell
poetry run pytest tests/stage1 -v
```

Run the quality evaluation (Groundedness, Answer Relevance, Retrieval Relevance):
```powershell
poetry run python -m stage1_rag_chatbot.eval.rag_triad_eval
```
## Structure

**`agent.py`** — builds the chatbot: the LLM, its 4 tools, and its system prompt, wired together with `create_agent`.

**`bootstrap.py`** — one-time setup script. Creates DB tables, generates fake parking spaces, loads the policy PDFs into Milvus.

**`main.py`** — the CLI chat loop you actually run to talk to the bot.

**`data/generate_fake_data.py`** — creates 200 fake parking spaces (zone, floor, price, availability) in SQLite.

**`data/policies/*.pdf`** — the 5 source documents (general info, hours/pricing, locations, booking process, rules) the chatbot searches for answers.

**`ingestion/loaders.py`** — reads the policy PDFs into LangChain `Document` objects.

**`ingestion/chunking_strategies.py`** — splits long documents into smaller searchable pieces.

**`ingestion/ingest_documents.py`** — CLI that ties loading + chunking + storing into Milvus into one step.

**`db/sql_store.py`** — all SQLite access: parking spaces, reservations, conflict checks, status updates.

**`db/vector_store.py`** — the Milvus connection used for storing and searching policy text.

**`tools/search_policies_tool.py`** — lets the chatbot search the policy documents for an answer.

**`tools/availability_tool.py`** — lets the chatbot check live space availability and pricing.

**`tools/reservation_tool.py`** — collects reservation details, checks for conflicts, saves it as `pending`.

**`tools/check_reservation_status_tool.py`** — lets a customer check an existing reservation's current status.

**`guardrails/pii_filter.py`** — detects and can redact personal information (name, email, phone) from text.

**`eval/rag_triad_eval.py`** — scores the chatbot's answers on Groundedness, Answer Relevance, and Retrieval Relevance using LangSmith.