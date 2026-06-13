from apps.notifications.constants import ChannelTypeChoices

from . import BaseStratergy, notification_stratergy_registry


class WebhookStratergy(BaseStratergy):
    REGISTERY_KEY = ChannelTypeChoices.WEBHOOK.value


notification_stratergy_registry.register(WebhookStratergy)
