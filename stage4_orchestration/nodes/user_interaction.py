import re
import uuid

from langchain_core.runnables import RunnableConfig

from stage1_rag_chatbot.agent import agent as stage1_agent
from stage1_rag_chatbot.db.sql_store import get_reservation_by_id, set_orchestrator_thread
from stage4_orchestration.state import OrchestratorState


def user_interaction_node(state: OrchestratorState, config: RunnableConfig) -> OrchestratorState:
    thread_id = config["configurable"]["thread_id"]

    stage1_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = stage1_agent.invoke({"messages": state["messages"]}, config=stage1_config)
    new_messages = result["messages"]

    reservation = None
    for msg in new_messages:
        if getattr(msg, "name", None) == "submit_reservation_request":
            match = re.search(r"ID: (\w+)", msg.content)
            if match:
                reservation = get_reservation_by_id(match.group(1))
                set_orchestrator_thread(reservation["reservation_id"], thread_id)

    return {"messages": new_messages, "reservation": reservation, "decision": None}