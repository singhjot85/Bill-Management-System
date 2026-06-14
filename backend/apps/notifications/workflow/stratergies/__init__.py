from utils.registry_utils import ClassRegistry

from .base_stratergy import BaseStratergy  # noqa: F401
from .email_stratergy import EmailStratergy  # noqa: F401
from .sms_stratergy import SMSStratergy  # noqa: F401
from .stratergy_mixins import TemplateHelperMixin  # noqa: F401
from .webhook_stratergy import WebhookStratergy  # noqa: F401

notification_stratergy_registry = ClassRegistry()


class NotificationStratergyException(Exception):
    """General Exception for any issue(s) in Stratergy"""

    pass
