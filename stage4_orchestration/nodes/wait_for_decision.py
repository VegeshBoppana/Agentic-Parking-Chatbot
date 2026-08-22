from langgraph.types import interrupt

from stage1_rag_chatbot.db.sql_store import update_reservation_status
from stage4_orchestration.state import OrchestratorState


def wait_for_decision_node(state: OrchestratorState) -> OrchestratorState:
    reservation_id = state["reservation"]["reservation_id"]
    decision = interrupt({"reservation_id": reservation_id, "message": "Awaiting admin decision"})
    update_reservation_status(reservation_id, "approved" if decision == "approve" else "rejected")
    return {**state, "decision": decision}