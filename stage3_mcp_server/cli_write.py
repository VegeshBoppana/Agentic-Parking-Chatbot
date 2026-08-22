import asyncio
import json
import sys

from stage3_mcp_server.agent import _write_confirmed_reservation_async


def main() -> None:
    payload = json.loads(sys.argv[1])
    asyncio.run(_write_confirmed_reservation_async(**payload))


if __name__ == "__main__":
    main()