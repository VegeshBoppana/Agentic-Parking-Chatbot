from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from shared.config import HITL_CHECKPOINT_DB_PATH
from shared.llm import get_chat_model
from stage1_rag_chatbot.db.sql_store import update_reservation_status
from stage2_hitl_agent.tools.send_admin_notification_tool import send_admin_notification
from stage2_hitl_agent.tools.wait_for_decision_tool import wait_for_admin_decision

SYSTEM_PROMPT = """You are SkyPark's administrator-notification agent.

You will be given a pending reservation's details. You must:
1. Call send_admin_notification with the reservation_id (copied exactly), a
   concise subject, a brief greeting, a clear reservation_summary (name, car
   number, zone, period), and a short closing line asking the admin to review
   and respond. Do not include any links yourself - they are added automatically.
2. Immediately after, call wait_for_admin_decision with the same reservation_id
   to pause and wait for the administrator's decision.
3. Once you receive the decision, reply with one short sentence confirming the
   final status. Do not call any more tools after that.
"""

def get_checkpointer():
    """Context manager - use as `with get_checkpointer() as cp:`."""
    return SqliteSaver.from_conn_string(HITL_CHECKPOINT_DB_PATH)


def _build_agent(checkpointer):
    return create_agent(
        model=get_chat_model(),
        tools=[send_admin_notification, wait_for_admin_decision],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )

def escalate_reservation(reservation: dict) -> None:
    """Called directly by Stage 1's reservation tool."""
    reservation_id = reservation["reservation_id"]
    update_reservation_status(reservation_id, "awaiting_approval")

    prompt = (
        f"Reservation ID: {reservation_id}\n"
        f"Name: {reservation['name']} {reservation['surname']}\n"
        f"Car Number: {reservation['car_number']}\n"
        f"Zone: {reservation['zone']}\n"
        f"Period: {reservation['start_time']} to {reservation['end_time']}"
    )

    with get_checkpointer() as checkpointer:
        checkpointer.setup()
        agent = _build_agent(checkpointer)
        config = {"configurable": {"thread_id": f"approval-{reservation_id}"}}
        agent.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)

def resume_approval(reservation_id: str, decision: str) -> None:
    """Called by the FastAPI endpoint when the admin clicks approve/reject."""
    with get_checkpointer() as checkpointer:
        checkpointer.setup()
        agent = _build_agent(checkpointer)
        config = {"configurable": {"thread_id": f"approval-{reservation_id}"}}
        agent.invoke(Command(resume=decision), config=config)
