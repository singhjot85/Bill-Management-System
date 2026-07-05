from apps.notifications.constants import ChannelTypeChoices

from . import BaseStratergy


class WebhookStratergy(BaseStratergy):
    REGISTERY_KEY = ChannelTypeChoices.WEBHOOK.value
