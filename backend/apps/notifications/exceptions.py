"""
Custom Exception Classes for notifications app
"""


class NotificationResolverException(Exception):
    """General Exception for any issue(s) in Resolver"""

    pass


class NotificationStratergyException(Exception):
    """General Exception for any issue(s) in Stratergy"""

    pass


class NotificationDispatcherException(Exception):
    """General Exception for any issue(s) in Dispatcher"""

    pass


class TemplateHelperException(Exception):
    """Template Helper Mixin related exceptions."""

    pass


class InvalidEventException(Exception):
    """General Exception for any issue(s) in Event Creation"""

    pass
