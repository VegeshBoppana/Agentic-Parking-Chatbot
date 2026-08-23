# Stage 3 - MCP Server (Confirmed Reservation Writer)

## Setup

1. Requires Node.js/npm installed (used to run the pre-built `@modelcontextprotocol/server-filesystem` MCP server via `npx`).
2. Install project dependencies (from the project root):
```powershell
   poetry install
```

## Usage

Stage 3 isn't run standalone in normal use — it's triggered automatically by Stage 2 (or Stage 4's orchestrator) the moment an admin approves a reservation, via `write_confirmed_reservation(...)`.

To test it in isolation:
```powershell
poetry run python -c "from stage3_mcp_server.agent import write_confirmed_reservation; write_confirmed_reservation(name='Test User', car_number='TS00AB0000', reservation_period='2026-08-25 10:00 to 2026-08-25 12:00', approval_time='2026-08-25T09:00:00')"
```

Check the result:
```powershell
Get-Content stage3_mcp_server\data\confirmed_reservations.txt
```

## Structure
**`agent.py`** — a real LangChain agent that composes and writes confirmed reservations using the pre-built filesystem MCP server's own tools (`read_text_file`, `write_file`), reached over the actual MCP protocol via `MultiServerMCPClient`.