from apps.notifications.constants import ChannelTypeChoices

from . import BaseStratergy, notification_stratergy_registry


class EmailStratergy(BaseStratergy):
    REGISTERY_KEY = ChannelTypeChoices.EMAIL.value


notification_stratergy_registry.register(EmailStratergy)
