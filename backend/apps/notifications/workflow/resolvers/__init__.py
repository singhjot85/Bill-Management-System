"""
Resolver resolve's out instruction(s) for dispatcher from a given event
Its responsibilty is to resolve and validate everything before passing to dispatcher.
If something needs to fetched from databse, resolver should that.
"""

from utils.registry_utils import ClassRegistry

from .base_resolver import (  # noqa: F401
    BaseResolver,
    ChannelInstruction,
    ResolverFactory,
)
from .email_resolver import EmailResolver  # noqa: F401
from .sms_resolver import SMSResolver  # noqa: F401
from .webhook_resolver import WebHookResolver  # noqa: F401

resolver_registry = ClassRegistry()


class NotificationResolverException(Exception):
    """General Exception for any issue(s) in Resolver"""

    pass
