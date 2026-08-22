import asyncio
import subprocess
import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import json

from shared.llm import get_chat_model
from shared.logging_utils import get_logger
import threading

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
RESERVATIONS_FILE = DATA_DIR / "confirmed_reservations.txt"

SYSTEM_PROMPT = f"""You are SkyPark's reservation-recording agent. You record confirmed
reservations into a log file using your file tools.

The file path is exactly: {RESERVATIONS_FILE}

You will be given one confirmed reservation's details. Follow these steps in order:

1. Call read_text_file on the file path above to get its current content. If it
   does not exist yet, that is expected for the very first reservation ever
   written - treat its content as empty in that case.
2. Format exactly one new line, no header, no extra text, in this exact format:
   Name | Car Number | Reservation Period | Approval Time
3. Call write_file with the file's ENTIRE previous content, followed by your new
   line. THIS IS THE MOST IMPORTANT RULE: never call write_file with only the new
   line - doing so destroys every previously recorded reservation. Always include
   everything read in step 1 first.
4. Reply with one short sentence confirming the write succeeded.
"""


def _mcp_config() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        return {
            "filesystem": {
                "transport": "stdio", "command": "cmd",
                "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", str(DATA_DIR)],
            }
        }
    return {
        "filesystem": {
            "transport": "stdio", "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(DATA_DIR)],
        }
    }


async def _write_confirmed_reservation_async(name: str, car_number: str, reservation_period: str, approval_time: str) -> None:
    client = MultiServerMCPClient(_mcp_config())
    tools = await client.get_tools()
    agent = create_agent(model=get_chat_model(), tools=tools, system_prompt=SYSTEM_PROMPT)

    prompt = (
        f"Name: {name}\n"
        f"Car Number: {car_number}\n"
        f"Reservation Period: {reservation_period}\n"
        f"Approval Time: {approval_time}"
    )
    result = await agent.ainvoke({"messages": [HumanMessage(content=prompt)]})
    logger.info(f"Stage 3 agent result: {result['messages'][-1].content}")


def write_confirmed_reservation(
    name: str, car_number: str, reservation_period: str, approval_time: str
) -> None:
    """Runs Stage 3's agent in a completely separate OS process - required because
    LangSmith's tracing wrapper re-applies a captured contextvars.Context on every
    traced call, leaking Stage 2's sync checkpointer state even across a fresh
    thread. A new process has zero shared context, guaranteeing isolation."""
    payload = json.dumps({
        "name": name, "car_number": car_number,
        "reservation_period": reservation_period, "approval_time": approval_time,
    })
    project_root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, "-m", "stage3_mcp_server.cli_write", payload],
        capture_output=True, text=True, cwd=str(project_root),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Stage 3 write failed: {result.stderr}")