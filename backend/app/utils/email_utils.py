import smtplib
import sys
from email.message import EmailMessage
from app.core.config import settings
import logging
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@contextmanager
def smtp_connection():
    """Context manager to yield an SMTP or SMTP_SSL connection."""
    use_ssl = getattr(settings, "SMTP_USE_SSL", None)
    port = settings.SMTP_PORT or (465 if use_ssl else 587)

    try:
        if use_ssl or port == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, port, timeout=10)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, port, timeout=10)
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except smtplib.SMTPNotSupportedError:
                logger.warning("STARTTLS not supported by server, continuing without TLS.")

        if getattr(settings, "SMTP_USER", None):
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
        yield server

    except Exception as e:
        logger.error(
            f"Error establishing SMTP connection to {settings.SMTP_HOST}:{port}: {e}"
        )
        raise
    finally:
        try:
            server.quit()
        except Exception:
            pass


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Send an email via configured SMTP.
    Falls back to logging the message if no SMTP is configured.
    """
    if not getattr(settings, "SMTP_HOST", None):
        logger.info(
            "SMTP not configured. Simulating email:\nTo: %s\nSubject: %s\nBody:\n%s",
            to_email, subject, body
        )
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = getattr(settings, "FROM_EMAIL", settings.SMTP_USER or "no-reply@example.com")
    msg["To"] = ", ".join(to_email) if isinstance(to_email, list) else to_email
    msg.set_content(body)
    msg.add_alternative(f"<p>{body}</p>", subtype="html")

    logger.info("Sending email to %s - %s", to_email, subject)

    try:
        with smtp_connection() as server:
            server.send_message(msg)
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
