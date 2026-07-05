"""
Implementation lofgic for what happens when a event is trigerred is defined by stratergies
"""

from .base_stratergy import (  # noqa: F401
    BaseStratergy,
    NotificationStrategyException,
    notification_stratergy_registry,
)
from .stratergy_mixins import TemplateHelperMixin  # noqa: F401
