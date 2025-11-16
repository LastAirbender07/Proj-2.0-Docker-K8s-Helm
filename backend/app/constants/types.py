from enum import Enum

class NotificationEventType(str, Enum):
    USER_SIGNUP = "user.signup"
    PAYMENT_FAILED = "payment.failed"
    PAYMEBT_SUCCESS = "payment.success"
    PASSWORD_EXPIRY = "password.expiry"
    USER_UNSUBSCRIBE = "user.unsubscribe"
    CUSTOM = "custom"
