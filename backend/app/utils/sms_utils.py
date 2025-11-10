import logging
logger = logging.getLogger(__name__)

def send_sms(phone: str, message: str):
    logger.info("Sending SMS to %s: %s", phone, message)
