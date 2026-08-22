from typing import TypedDict

from langchain_core.messages import BaseMessage


class OrchestratorState(TypedDict):
    messages: list[BaseMessage]
    reservation: dict | None
    decision: str | None