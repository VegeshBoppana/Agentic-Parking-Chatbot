from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from shared.logging_utils import get_logger
from stage2_hitl_agent.agent import resume_approval

from shared.logging_utils import get_logger
from stage2_hitl_agent.agent import resume_approval

logger = get_logger(__name__)
app = FastAPI(title="SkyPark Admin Approval API")

@app.get("/reservations/{reservation_id}/approve", response_class=HTMLResponse)
def approve(reservation_id: str):
    try:
        resume_approval(reservation_id, "approve")
    except Exception as e:
        logger.error(f"Failed to approve {reservation_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not process approval.")
    return f"<h3>Reservation {reservation_id} approved.</h3>"

@app.get("/reservations/{reservation_id}/reject", response_class=HTMLResponse)
def reject(reservation_id: str):
    try:
        resume_approval(reservation_id, "reject")
    except Exception as e:
        logger.error(f"Failed to reject {reservation_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not process rejection.")
    return f"<h3>Reservation {reservation_id} rejected.</h3>"