import abc
import typing
from dataclasses import dataclass, field
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

from apps.customer_management.models import Customer
from apps.notifications.constants import (
    ChannelTypeChoices,
    EventPreferences,
    LogStatusChoices,
)
from apps.notifications.exceptions import NotificationResolverException
from apps.notifications.models import NotificationLog
from apps.setup.constants import ConfigurationInterfaceChoices as InterfaceType
from apps.setup.models import Configurations
from utils.registry_utils import ClassRegistry

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.trigger import NotificationEvent

User = get_user_model()

resolver_registry = ClassRegistry()


@dataclass
class ChannelInstruction:
    log_id: str
    user_id: str
    channel_type: str
    context_data: dict = field(default_factory=dict)

    @staticmethod
    def _validate_id(id):
        if not id:
            return

        if isinstance(id, (int, UUID)):
            return

        if isinstance(id, str):
            if id.isdigit():
                return
            try:
                UUID(id)
                return
            except ValueError:
                pass

        raise NotificationResolverException(f"Invalid id: {id}")

    def validate_user_id(self):
        """User id Validations"""
        self._validate_id(self.user_id)

    def validate_log_id(self):
        """Log id Validations"""
        self._validate_id(self.log_id)

    def validate_channel_type(self):
        """Channel Type Validations"""
        if not self.channel_type:
            raise NotificationResolverException("Channel Type not give, its required")

        if self.channel_type not in ChannelTypeChoices.values:
            raise NotificationResolverException(f"Channel type is not valid: [{self.channel_type}]")

    def __post_init__(self):
        """Post intialization validation for dataclass"""
        self.validate_channel_type()
        self.validate_log_id()
        self.validate_user_id()


class ResolverFactory:
    _preferences = ChannelTypeChoices.values

    def __init__(
        self,
        event: "NotificationEvent",
        party: typing.Optional[typing.Union[str, "UUID"]] = None,
        *args,
        **kwargs,
    ):
        """
        Resolver init, the job of an initializer is to consume an event and resolve preferences,
        It Checks what all channels the user or event are allowed and generate instructions for same.
        Args:
            event (NotificationEvent): event for which we need to resolve channel instructions.
            party (str, UUID, optional): The Customer or user to be attached with the channel.
                TODO: Currently we are allowing party=None, but we need to revisit this
        """
        self._party_id = party
        self._event = event

        self._load_tenant_preferences()
        if not self.skip_user_pref:
            self._load_user_preferences()

    @property
    def skip_user_pref(self):
        if hasattr(self, "_party_id"):
            return not self._party_id
        return False

    @property
    def user_preferences(self) -> typing.Optional[list]:
        if hasattr(self, "_user_preferences"):
            return self._user_preferences
        return None

    @property
    def tenant_preferences(self) -> typing.Optional[list]:
        if hasattr(self, "_tenant_pref"):
            return self._tenant_pref
        return None

    @property
    def preferences(self) -> set:
        """
        Resolved preferences based on tenant preferences, user preferences, and event preferences.

        Current Resolution Logic (Precdence hight-to-low):
            - Event Preferences (Optional)
                - Tenant Preferences
                    - User Preferences
        """
        if not hasattr(self, "_event") or not self._event or not self._event.event_type:
            return set()

        event_preferences = None
        for member in EventPreferences:
            if member.value[0] == self._event.event_type:
                event_preferences = member.get_preferences()
                break

        if self.skip_user_pref:
            effective = set(self.tenant_preferences)
        else:
            effective = set(self.tenant_preferences) & set(self.user_preferences)

        if event_preferences is not None:  # explicitly configured — further restrict
            effective &= event_preferences

        return effective

    @property
    def party(self):
        if hasattr(self, "_party"):
            return getattr(self, "_party")

        return self._get_party()

    def _get_party(self):
        try:
            if isinstance(self._party_id, int) or (isinstance(self._party_id, str) and self._party_id.isdigit()):
                self._party = User.objects.prefetch_related("notification_preferences").get(pk=self._party_id)
            else:
                raise User.DoesNotExist
        except User.DoesNotExist:
            try:
                self._party = Customer.objects.prefetch_related("notification_preferences").get(pk=self._party_id)
            except Customer.DoesNotExist:
                self._party = None

        return self._party

    def _load_tenant_preferences(self):
        """Load tenant preferences for current tenant. All Configs are cached so don't need to cache this one specifically."""

        config = Configurations.get_latest_config(InterfaceType.NOTIFICATION_CONFIGURATION.value)
        if not config:
            raise NotificationResolverException("Notifications not configured for tenant.")

        tenant_pref = config.details.get("tenant_preferences")
        if not tenant_pref:
            raise ImproperlyConfigured("Tenant Preferences not found for current tenant.")

        self._tenant_pref = tenant_pref

    def _load_user_preferences(self):
        """Load user preferences from NotificationPreference Model"""
        self._user_preferences = []
        if not self.party:
            return self._user_preferences

        self._user_preferences = list(
            self.party.notification_preferences.filter(event_type=self._event.event_type, opted_in=True).values_list(
                "preference_type", flat=True
            )
        )

        return self._user_preferences

    def resolve(self) -> list["ChannelInstruction"]:
        """Resolve out preferences, and genereate instructions for dispatcher."""

        instructions = []
        for channel_type in self.preferences:
            resolver: "BaseResolver" = resolver_registry.get(key=channel_type)
            if not resolver:
                raise NotificationResolverException(f"Cannot find any resolver for: {resolver}")

            instruction: "ChannelInstruction" = resolver(self._event, channel_type).resolve()
            instructions.append(instruction)

        return instructions


class BaseResolver(abc.ABC):
    _channel_type = None

    def __init__(self, event: "NotificationEvent", channel_type: str):

        if channel_type not in ChannelTypeChoices.values:
            raise NotificationResolverException(f"Invalid Channel type: {channel_type}")

        self._event = event
        self._channel_type = channel_type

    @classmethod
    @abc.abstractmethod
    def _get_instruction_dataclass(cls, *args, **kwargs) -> "ChannelInstruction":
        """
        Getter for Instruction Dataclass, should return a `ChannelInstruction` subclass
        Override in implementation for channel specific logic
        """

    def initialize_log(self) -> "NotificationLog":
        """
        Initialize a log object and log event data in it, also pass this log_id to celery task,
        """
        return NotificationLog.objects.create(
            status=LogStatusChoices.QUEUED,
            channel=self._channel_type,
            context_data=self._event.data or {},
        )

    @abc.abstractmethod
    def _get_dataclass_data(self, *args, **kwargs) -> dict:
        """
        Getter for Instruction Dataclass's data
        Override in implementation for channel specific logic
        """
        log = self.initialize_log()

        return {
            "log_id": log.pk,
            "user_id": self._event.assosciated_party,
            "channel_type": self._channel_type,
            "context_data": self._event.data,
        }

    def resolve(self, *args, **kwargs):
        """
        The actual method that gets called when resolving instructions for dispatcher
        The flow remains consistent, but the implemenration might differ channel to ch
        """
        channel_instruction: "ChannelInstruction" = self._get_instruction_dataclass(*args, **kwargs)
        data: dict = self._get_dataclass_data(*args, **kwargs)
        return channel_instruction(**data)
