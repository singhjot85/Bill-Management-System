from dataclasses import dataclass

from apps.notifications.constants import ChannelTypeChoices, NotificationTemplateChoices
from apps.notifications.workflow.resolvers import (
    BaseResolver,
    ChannelInstruction,
    NotificationResolverException,
    resolver_registry,
)


@dataclass(frozen=True)
class EmailInstructions(ChannelInstruction):
    """Channel Instructions specific to Email Channel"""

    template_name: str

    def validate_template_name(self):
        if not self.template_name:
            raise NotificationResolverException("Template name is required")

        if self.template_name not in NotificationTemplateChoices.values:
            raise NotificationTemplateChoices(f"Invalid Template name: {self.template_name}")

    def __post_init__(self):
        super().__post_init__()
        self.validate_template_name()


class EmailResolver(BaseResolver):
    _channel_type = ChannelTypeChoices.EMAIL.value
    REGISTERY_KEY = _channel_type

    def _get_instruction_dataclass(self, *args, **kwargs):
        """Instuctions Dataclass for email channel"""
        return EmailInstructions

    def _get_dataclass_data(self, *args, **kwargs):
        """
        Instuctions Dataclass's data for email channel
        TODO: Figure out a better way to pass template_name to reolver.
        """
        data = super()._get_dataclass_data(*args, **kwargs)
        data.update({"template_name": self._event.data.get("template_name")})


resolver_registry.register(EmailResolver)
