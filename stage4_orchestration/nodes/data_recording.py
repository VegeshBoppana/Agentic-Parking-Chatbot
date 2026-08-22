from datetime import datetime, timezone

from shared.logging_utils import get_logger
from stage3_mcp_server.agent import write_confirmed_reservation
from stage4_orchestration.state import OrchestratorState

logger = get_logger(__name__)


def data_recording_node(state: OrchestratorState) -> OrchestratorState:
    if state["decision"] != "approve":
        return state

    reservation = state["reservation"]
    try:
        write_confirmed_reservation(
            name=f"{reservation['name']} {reservation['surname']}",
            car_number=reservation["car_number"],
            reservation_period=f"{reservation['start_time']} to {reservation['end_time']}",
            approval_time=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as e:
        logger.error(f"Stage 3 write failed for {reservation['reservation_id']}: {e}")

    return state