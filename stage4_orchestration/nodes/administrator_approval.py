from shared.config import ORCHESTRATOR_API_BASE_URL
from shared.llm import get_chat_model
from stage1_rag_chatbot.db.sql_store import update_reservation_status
from stage2_hitl_agent.notify import send_email
from stage2_hitl_agent.tools.send_admin_notification_tool import AdminNotificationContent
from stage4_orchestration.state import OrchestratorState


def administrator_approval_node(state: OrchestratorState) -> OrchestratorState:
    reservation = state["reservation"]
    reservation_id = reservation["reservation_id"]

    update_reservation_status(reservation_id, "awaiting_approval")

    content = get_chat_model().with_structured_output(AdminNotificationContent).invoke(
        f"Compose an admin notification email.\n"
        f"reservation_id: {reservation_id}\n"
        f"Name: {reservation['name']} {reservation['surname']}\n"
        f"Car Number: {reservation['car_number']}\n"
        f"Zone: {reservation['zone']}\n"
        f"Period: {reservation['start_time']} to {reservation['end_time']}"
    )

    approve_url = f"{ORCHESTRATOR_API_BASE_URL}/orchestration/{reservation_id}/approve"
    reject_url = f"{ORCHESTRATOR_API_BASE_URL}/orchestration/{reservation_id}/reject"
    body = (
        f"{content.greeting}\n\n{content.reservation_summary}\n\n"
        f"Approve: {approve_url}\nReject: {reject_url}\n\n{content.closing}"
    )
    send_email(content.subject, body)

    return state