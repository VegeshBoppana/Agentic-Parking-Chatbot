import re
import uuid

from stage1_rag_chatbot.agent import agent as stage1_agent
from stage1_rag_chatbot.db.sql_store import get_reservation_by_id
from stage4_orchestration.state import OrchestratorState


def user_interaction_node(state: OrchestratorState) -> OrchestratorState:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = stage1_agent.invoke({"messages": state["messages"]}, config=config)
    new_messages = result["messages"]

    reservation = None
    for msg in new_messages:
        if getattr(msg, "name", None) == "submit_reservation_request":
            match = re.search(r"ID: (\w+)", msg.content)
            if match:
                reservation = get_reservation_by_id(match.group(1))

    return {"messages": new_messages, "reservation": reservation, "decision": None}