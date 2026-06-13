from apps.notifications.constants import ChannelTypeChoices

from . import BaseStratergy, notification_stratergy_registry


class SMSStratergy(BaseStratergy):
    REGISTERY_KEY = ChannelTypeChoices.SMS.value


notification_stratergy_registry.register(SMSStratergy)
