"""
The Webhook integration is currently incomplete,
this need to be revisited and implemented properly and tested
TODO: Webhook research and implementation.
"""

from dataclasses import dataclass

from apps.notifications.constants import ChannelTypeChoices
from apps.notifications.workflow.resolvers import (
    BaseResolver,
    ChannelInstruction,
    resolver_registry,
)


@dataclass
class WebhookInstructions(ChannelInstruction):
    """Webhook Instuctions dataclass for webhook channel"""

    pass


class WebHookResolver(BaseResolver):
    _channel_type = ChannelTypeChoices.WEBHOOK.value
    REGISTERY_KEY = _channel_type

    def _get_instruction_dataclass(self, *args, **kwargs):
        """Instuctions Dataclass for webhook channel"""
        return WebhookInstructions

    def _get_dataclass_data(self, *args, **kwargs):
        """
        Instuctions Dataclass's data for webhook channel
        """
        return super()._get_dataclass_data(*args, **kwargs)


resolver_registry.register(WebHookResolver)
