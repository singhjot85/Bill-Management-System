import logging
import typing

from celery import shared_task

from apps.notifications.workflow.stratergies import (
    NotificationStrategyException,
    notification_stratergy_registry,
)

LOGGER = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.stratergies import BaseStratergy


@shared_task
def notification_task(*args, **kwargs):
    """
    Notification task that helps notification flow to work asynchronously
    It's just placeholder all the logic is in workflow services.
    """
    manager_key = kwargs.get("channel_type", None)
    NotificationStatergy: type["BaseStratergy"] = notification_stratergy_registry.get(manager_key)

    if not NotificationStatergy:
        raise NotificationStrategyException(f"Cannot find NotificationStatergy for channel: {manager_key}")

    instructions = NotificationStatergy.reconstruct_instructions(*args, **kwargs)

    stratergy: "BaseStratergy" = NotificationStatergy(instructions, *args, **kwargs)
    stratergy.send()
