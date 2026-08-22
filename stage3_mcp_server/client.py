import asyncio
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

from shared.logging_utils import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
RESERVATIONS_FILE = DATA_DIR / "confirmed_reservations.txt"

def _mcp_server_config() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        command, args = "cmd", ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", str(DATA_DIR)]
    else:
        command, args = "npx", ["-y", "@modelcontextprotocol/server-filesystem", str(DATA_DIR)]
    return {"filesystem": {"transport": "stdio", "command": command, "args": args}}

def _extract_text(result) -> str:
    """Tool results are lists of content blocks - extract the actual text."""
    if isinstance(result, list) and result and isinstance(result[0], dict):
        return result[0].get("text", "")
    return str(result)


def _sanitize(value: str) -> str:
    """Strips newlines so a malformed field can't inject a fake extra line into the log."""
    return value.replace("\n", " ").replace("\r", " ").strip()


async def _write_confirmed_reservation_async(name: str, car_number: str, reservation_period: str, approval_time: str) -> None:
    if not all([name, car_number, reservation_period, approval_time]):
        raise ValueError("All fields are required to write a confirmed reservation.")

    line = (
        f"{_sanitize(name)} | {_sanitize(car_number)} | "
        f"{_sanitize(reservation_period)} | {_sanitize(approval_time)}\n"
    )

    client = MultiServerMCPClient(_mcp_server_config())
    tools = await client.get_tools()
    write_tool = next(t for t in tools if t.name == "write_file")
    read_tool = next(t for t in tools if t.name == "read_text_file")

    existing_raw = await read_tool.ainvoke({"path": str(RESERVATIONS_FILE)})
    existing = _extract_text(existing_raw)
    if "ENOENT" in existing or "no such file" in existing:
        existing = ""  # first-ever write - file doesn't exist yet

    await write_tool.ainvoke({"path": str(RESERVATIONS_FILE), "content": existing + line})
    logger.info(f"Wrote confirmed reservation to {RESERVATIONS_FILE}: {line.strip()}")


def write_confirmed_reservation(name: str, car_number: str, reservation_period: str, approval_time: str) -> None:
    """Sync wrapper - call this from anywhere, including sync LangChain tools."""
    asyncio.run(_write_confirmed_reservation_async(name, car_number, reservation_period, approval_time))