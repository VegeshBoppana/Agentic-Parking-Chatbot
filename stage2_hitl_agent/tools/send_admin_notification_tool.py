from langchain.tools import tool
from pydantic import BaseModel, Field

from shared.config import HITL_API_BASE_URL
from stage2_hitl_agent.notify import send_email

class AdminNotificationContent(BaseModel):
    """Structured content for the administrator notification email."""

    reservation_id: str = Field(description="The reservation ID, copied exactly as given")
    subject: str = Field(description="A concise email subject line")
    greeting: str = Field(description="A brief professional greeting")
    reservation_summary: str = Field(description="Clear summary: name, car number, zone, period")
    closing: str = Field(description="A brief closing line asking the admin to review and respond")


@tool(args_schema=AdminNotificationContent)
def send_admin_notification(
    reservation_id: str, subject: str, greeting: str, reservation_summary: str, closing: str
) -> str:
    """Sends the reservation notification email to the administrator."""
    approve_url = f"{HITL_API_BASE_URL}/reservations/{reservation_id}/approve"
    reject_url = f"{HITL_API_BASE_URL}/reservations/{reservation_id}/reject"
    body = (
        f"{greeting}\n\n"
        f"{reservation_summary}\n\n"
        f"Approve: {approve_url}\n"
        f"Reject: {reject_url}\n\n"
        f"{closing}"
    )
    send_email(subject, body)
    return "Notification sent."