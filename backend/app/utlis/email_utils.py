import smtplib
from email.message import EmailMessage
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str):
    # If SMTP configured, use it; otherwise print for dev
    if settings.SMTP_HOST and settings.SMTP_USER:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = to_email
        msg.set_content(body)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT or 587) as s:
            s.starttls()
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
            s.send_message(msg)
    else:
        logger.info("Sending email (dev) to %s - %s\n%s", to_email, subject, body)
