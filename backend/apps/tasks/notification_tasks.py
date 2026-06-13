import logging
import typing

from celery import shared_task

from apps.notifications.workflow.stratergies import notification_stratergy_registry

LOGGER = logging.getLogger()

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.stratergies import BaseStratergy

@shared_task
def notification_task(*args, **kwargs):
    """
    Notification task that helps notification flow to work asynchronously
    It's just placeholder all the logic is in workflow services.
    """
    manager_key = kwargs.get("channel_type", None)
    manager: "BaseStratergy" = notification_stratergy_registry.get(manager_key)
    manager.send(args, kwargs)
