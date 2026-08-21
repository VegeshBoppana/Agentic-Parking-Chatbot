import smtplib
from email.mime.text import MIMEText

from shared.config import ADMIN_EMAIL, GMAIL_APP_PASSWORD, GMAIL_SENDER_EMAIL
from shared.logging_utils import get_logger

logger = get_logger(__name__)


def send_email(subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_SENDER_EMAIL
    msg["To"] = ADMIN_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)

    logger.info(f"Email sent to admin ({ADMIN_EMAIL}): {subject}")