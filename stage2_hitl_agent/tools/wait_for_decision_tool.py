from langchain.tools import tool
from langgraph.types import interrupt

from shared.logging_utils import get_logger
from stage1_rag_chatbot.db.sql_store import update_reservation_status

logger = get_logger(__name__)


@tool
def wait_for_admin_decision(reservation_id: str) -> str:
    """Pauses and waits for the administrator's approve/reject decision on this reservation."""
    decision = interrupt({"reservation_id": reservation_id, "message": "Awaiting admin decision"})
    update_reservation_status(reservation_id, "approved" if decision == "approve" else "rejected")
    logger.info(f"Reservation {reservation_id} -> {decision}")
    return f"Admin decision recorded: {decision}"

## Here the entire agent stops and waits for the approval , and the apporval will look like below
""" 
result = agent.invoke(
    Command(resume="approve"),
    config={"configurable": {"thread_id": f"approval-{reservation_id}"}},
)
"""
## So this function/logic we write in another file and it gets triggered when the user hits the approve/reject  api end point.