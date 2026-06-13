import typing
from dataclasses import dataclass, field
from uuid import UUID

from apps.notifications.constants import EventTypeChoices
from apps.notifications.workflow.resolvers import ResolverFactory

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.dispatcher import NotificationDispatcher
    from apps.notifications.workflow.resolvers import ChannelInstruction


class InvalidEventException(Exception):
    """General Exception for any issue(s) in Trigger"""

    pass


@dataclass(frozen=True)
class NotificationEvent:
    event_type: str
    assosciated_party: typing.Union[str, UUID] = None
    data: dict = field(default_factory=dict)

    def validate_event_type(self):
        if not self.event_type:
            raise InvalidEventException("event_type is required to trigger a notification")

        if self.event_type not in EventTypeChoices.values:
            raise InvalidEventException(f"Invalid event_type: {self.event_type}")

    def validate_assosciated_party(self):
        id = self.assosciated_party
        if not id:
            return

        if not isinstance(id, str):
            raise InvalidEventException(f"Invalid id: {id}")

        try:
            UUID(id)
        except ValueError:
            raise InvalidEventException(f"Invalid id: {id}")

    def __post_init__(self):
        self.validate_event_type()
        self.validate_assosciated_party()


class NotificationService:

    def build_event(self, event_type: str, party: typing.Union[str, UUID], data: dict = None, *args, **kwargs):
        """Build and event dataclass from the given data,
        Data validation also happens inside in dataclass only.
        kwargs:
            event_type (str): Event Type to be trigerred.
            users (list[str], optional): List of user ids.
            customers (list[str], optional): List of customer ids.
            data (dict): Additional data to be passed in notification context.
        """
        return NotificationEvent(event_type=event_type, assosciated_party=party, data=data)

    def _trigger(self, event_type: str, party: typing.Union[str, UUID], data: dict = None, *args, **kwargs):

        event: "NotificationEvent" = self.build_event(event_type, party, data, *args, **kwargs)
        instructions: list["ChannelInstruction"] = ResolverFactory(event, party).resolve()
        for instruction in instructions:


    def trigger(
        self,
        event_type: str,
        parties: typing.Union[str, UUID, list, tuple],
        data: dict = None,
        *args,
        **kwargs,
    ):
        """
        This method triggers the notification flow:
            Creates a Notification event
            Create instructions for disaptcher from those events
            Dispatch individual tasks for each of those instuctions
        Args:
            event_type (str): Event Type to be trigerred.
            parties (str | UUID): Id or reference(s) for parties (customer/user) associated to that event.
                could be a Customer or a User id.
            data (dict): Additional data to be passed in notification context.
        """
        many = False
        if isinstance(parties, list) or isinstance(parties, tuple):
            many = True

        if not data:
            data = {}

        if many:
            for party in parties:
                self._trigger(event_type, party, data, *args, **kwargs)
        else:
            self._trigger(event_type, parties, data, *args, **kwargs)
