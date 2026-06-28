import logging
import typing
from dataclasses import dataclass, field
from uuid import UUID

from apps.notifications.constants import EventTypeChoices
from apps.notifications.exceptions import (
    InvalidEventException,
    NotificationDispatcherException,
    NotificationResolverException,
)
from apps.notifications.workflow.dispatcher import Dispatcher
from apps.notifications.workflow.resolvers import ResolverFactory

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.resolvers import ChannelInstruction


LOGGER = logging.getLogger()


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

        if isinstance(id, int):
            return

        if isinstance(id, str):
            if id.isdigit():
                return
            try:
                UUID(id)
                return
            except ValueError:
                pass

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
        """Handles the atomic trigger logic, so that each trigger is handled gracefully.

        Args:
            event_type (str): Event Type to be trigerred.
            party (str | UUID): Id or reference(s) for parties (customer/user) associated to that event.
                could be a Customer or a User id.
            data (dict): Additional data to be passed in notification context.

        Kwargs:
            celery_task_name (str, optional): Celery Task Name, to be executed.
        """
        event: "NotificationEvent" = self.build_event(event_type, party, data, *args, **kwargs)
        instructions: list["ChannelInstruction"] = ResolverFactory(event, party).resolve()
        for instruction in instructions:
            celery_task_name = kwargs.get("celery_task_name")
            Dispatcher(instruction, task_name=celery_task_name).dispatch()

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
            parties (str | UUID | list | tuple): Id or reference(s) for parties (customer/user) associated to that event.
                could be a Customer or a User id.
            data (dict): Additional data to be passed in notification context.

        Kwargs:
            celery_task_name (str, optional): Celery Task Name, to be executed.
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


notification_service = NotificationService()


def trigger_notifications(
    event_type: str, assosciated_parties: list[str], data: dict = None, raise_exception: bool = True
):
    """Trigger notification lifecylce from just this method

    Args:
        event_type (str): Event Type to trigger, should be a pre-registered event.
        assosciated_parties (list[str]): All the parties(user's/customer') assossciated with the event.
        data (dict, optional): Additional context data to pe passed to the Notification flow.
        raise_exception (bool, optional): Raise caught exceptions.
            default to True, i.e. trigger will not silently fail

    Kwargs:
        celery_task_name (str, optional): Celery Task Name, to be executed.

    Return:
        (bool): If the notification flow was queued sucessfully, or not.

    Raises:
        InvalidEventException: If the issue in trigggering the flow.
        NotificationResolverException: If the issue is in resolver phase.
        NotificationDispatcherException: If the issue in dispatch phase

    """
    try:
        notification_service.trigger(event_type=event_type, parties=assosciated_parties, data=data)
    except InvalidEventException as ieExcp:
        LOGGER.error("Error in event creation", exc_info=ieExcp)
        if raise_exception:
            raise
    except NotificationResolverException as nrExcp:
        LOGGER.error("Error in resolving instructions", exc_info=nrExcp)
        if raise_exception:
            raise
    except NotificationDispatcherException as ndExcp:
        LOGGER.error("Error in dipatching instructions", exc_info=ndExcp)
        if raise_exception:
            raise
    except Exception as e:
        LOGGER.error("An unkown error occurred in notification flow: %s", str(e), exc_info=e)
        if raise_exception:
            raise
