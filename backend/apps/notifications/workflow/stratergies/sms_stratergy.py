from apps.notifications.constants import ChannelTypeChoices

from . import BaseStratergy


class SMSStratergy(BaseStratergy):
    REGISTERY_KEY = ChannelTypeChoices.SMS.value
