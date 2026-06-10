import logging

from apps.notifications.constants import (
    ChannelInstruction,
    EventTypeChoices,
    NotificationEvent,
)
from apps.notifications.workflow.dispatcher import (
    NotificationDispatcher,
    NotificationDispatcherException,
)
from apps.notifications.workflow.resolver import (
    NotificationResolver,
    NotificationResolverException,
)

LOGGER = logging.getLogger()


class NotificationServiceException(Exception):
    pass


class NotificationService:
    """The notification service is a common wrapper over Notification flow, that makes it easier to work with the flow."""

    _event_type: EventTypeChoices
    _event: NotificationEvent
    _instructions: list["ChannelInstruction"]

    resolver: NotificationResolver
    dispatcher: NotificationDispatcher

    def __init__(self):
        self.resolver = NotificationResolver()
        self.dispatcher = NotificationDispatcher()

    def create_instructions(self) -> list["ChannelInstruction"]:
        """Calls the resolver with an event to create a list of instructions."""
        if not self._event:
            raise NotificationServiceException("No valid event found to initiate the flow!")

        return self.resolver.resolve(self._event)

    def dispatch_instructions(self):
        """Calls the dispatcher for each instruction."""
        for instruction in self._instructions:
            self.dispatcher.dispatch(instruction)

    def trigger(self):
        """
        This method triggers the notification flow:
            Creates a Notification event
            Create instructions for disaptcher from those events
            Dispatch individual tasks for each of those instuctions
        """
        LOGGER.info("[%s] Starting Notification flow...", self._event_type)

        try:
            self._instructions = self.create_instructions()
        except NotificationResolverException as nexcp:
            LOGGER.error(
                f"[{self._event_type}] Instruction resolution failed due to exception: {str(nexcp)}", exc_info=nexcp
            )
            return
        except Exception as e:
            LOGGER.error(f"[{self._event_type}] Instruction resolution failed due to exception: {str(e)}", exc_info=e)
            raise

        LOGGER.info("[%s] Notification instructions resolved successfully.", self._event_type)

        try:
            self.dispatch_instructions()
        except NotificationDispatcherException as dnexcp:
            LOGGER.error(
                f"[{self._event_type}] Notification dispatch failed due to exception: {str(dnexcp)}", exc_info=dnexcp
            )
            return
        except Exception as e:
            LOGGER.error(f"[{self._event_type} Notification dispatch failed due to exception: {str(e)}", exc_info=e)
            raise

        LOGGER.info("[%s] Notification flow completed successfully.", self._event_type)
