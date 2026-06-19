"""
Resolver resolve's out instruction(s) for dispatcher from a given event
Its responsibilty is to resolve and validate everything before passing to dispatcher.
If something needs to fetched from databse, resolver should that.
"""

from .base_resolver import (  # noqa: F401
    BaseResolver,
    ChannelInstruction,
    ResolverFactory,
    resolver_registry
)
