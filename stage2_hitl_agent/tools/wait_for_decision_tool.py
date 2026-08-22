from datetime import datetime, timezone

from langchain.tools import tool
from langgraph.types import interrupt

from shared.logging_utils import get_logger
from stage1_rag_chatbot.db.sql_store import get_reservation_by_id, update_reservation_status
from stage3_mcp_server.client import write_confirmed_reservation

logger = get_logger(__name__)


@tool
def wait_for_admin_decision(reservation_id: str) -> str:
    """Pauses and waits for the administrator's approve/reject decision on this reservation."""
    decision = interrupt({"reservation_id": reservation_id, "message": "Awaiting admin decision"})
    new_status = "approved" if decision == "approve" else "rejected"
    update_reservation_status(reservation_id, new_status)
    logger.info(f"Reservation {reservation_id} -> {new_status}")

    if new_status == "approved":
        reservation = get_reservation_by_id(reservation_id)
        if reservation:
            try:
                write_confirmed_reservation(
                    name=f"{reservation['name']} {reservation['surname']}",
                    car_number=reservation["car_number"],
                    reservation_period=f"{reservation['start_time']} to {reservation['end_time']}",
                    approval_time=datetime.now(timezone.utc).isoformat(),
                )
            except Exception as e:
                logger.error(f"Failed to write confirmed reservation {reservation_id} to file: {e}")
        else:
            logger.error(f"Reservation {reservation_id} approved but missing from DB - skipped file write.")

    return f"Admin decision recorded: {decision}"