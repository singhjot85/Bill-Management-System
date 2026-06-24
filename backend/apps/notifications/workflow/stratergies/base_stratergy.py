import logging
import typing
from abc import ABC, abstractmethod

from django.contrib.auth import get_user_model

from utils.registry_utils import ClassRegistry
from apps.customer_management.models import Customer
from apps.notifications.workflow.resolvers import (
    ChannelInstruction,
    resolver_registry,
)

LOGGER = logging.getLogger()

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import User as UserModel

    from apps.notifications.workflow.resolvers import BaseResolver

User = get_user_model()


class NotificationStrategyException(Exception):
    """Notification Stratergy related exceptions"""

    pass


class BaseStratergy(ABC):
    label: str = ""
    _instructions: "ChannelInstruction" = None

    def __init__(self, *args, **kwargs) -> None:
        self._instructions = self.reconstruct_instructions(*args, **kwargs)

    @property
    def associated_party(self) -> typing.Optional[typing.Union["User", "Customer"]]:
        """
        Fetch associated party from databse or object cache

        Returns:
            _associated_party: Associated party object, (Customer/User).

        Raises:
            NotificationStrategyException: Description.
        """
        if not hasattr(self, "_instructions"):
            return None

        if hasattr(self, "_associated_party"):
            return self._associated_party

        return self._get_associated_party()

    def _get_associated_party(self) -> typing.Optional[typing.Union["UserModel", "Customer"]]:
        """
        Get from database

        Raises:
            NotificationStrategyException: Description.
        """
        _user_id = self._instructions.user_id
        try:
            if isinstance(_user_id, int) or (isinstance(_user_id, str) and _user_id.isdigit()):
                self._associated_party = User.objects.get(id=_user_id)
            else:
                raise User.DoesNotExist
        except User.DoesNotExist:
            try:
                self._associated_party = Customer.objects.get(id=_user_id)
            except Customer.DoesNotExist:
                raise NotificationStrategyException(f"A user/customer for id: [{_user_id}] does not exist")
            except Customer.MultipleObjectsReturned:
                raise NotificationStrategyException(f"Multiple Customers found for: [{_user_id}], that isn't ideal")
        except User.MultipleObjectsReturned:
            raise NotificationStrategyException(f"Multiple users found for: [{_user_id}], that isn't ideal")

        return self._associated_party

    def reconstruct_instructions(self, *args, **kwargs) -> "ChannelInstruction":
        """
        Reconstruct ChannelInstruction back from the provided json data

        Args:
            *args (type): Description.
            **kwargs (type): Keyword arguments from celery-task directly.
        """
        from dataclasses import fields

        def filter_kwargs(data_cls):
            field_names = {f.name for f in fields(data_cls)}
            return {k: v for k, v in kwargs.items() if k in field_names}

        channel_type = kwargs.get("channel_type")
        resolver: "BaseResolver" = resolver_registry.get(key=channel_type)
        if hasattr(resolver, "_get_instruction_dataclass"):
            instruction_cls = resolver._get_instruction_dataclass(None)
            return instruction_cls(**filter_kwargs(instruction_cls))

        return ChannelInstruction(**kwargs)

    @abstractmethod
    def _send(self, *args, **kwargs):
        """Actual send logic belongs here, this can be overriden in each subclass."""
        pass

    def send(self, raise_on_exception: bool = True, *args, **kwargs):
        """
        Main Send caller, that calls the send logic, and also handles logging and error handling.

        Args:
            raise_on_exception (bool, optional): Whether to raise exception, or just log it silently.
                default to True

        Example Usage:

            >>> manager = notification_stratergy_registry.get("email")
            >>> manager.send()
            >>> manager = notification_stratergy_registry.get("email")
            >>> manager.send(raise_on_exception=True)
        """

        LOGGER.info("Sending %s notification...", self.label)

        try:
            self._send(args, kwargs)
        except Exception as ex:
            LOGGER.error("Error in sending %s", self.label, exc_info=ex)
            if raise_on_exception:
                raise NotificationStrategyException from ex

        LOGGER.info("Successfully sent %s notification", self.label)


notification_stratergy_registry = ClassRegistry()
