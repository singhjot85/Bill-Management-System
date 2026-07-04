from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    from django.conf import settings

    default_auto_field = "django.db.models.BigAutoField"
    name = settings.APP_NOTIFICATIONS

    def ready(self):
        self.register_resolvers()
        self.register_statergies()

    def register_statergies(self):
        from apps.notifications.workflow.stratergies import (
            notification_stratergy_registry,
        )
        from apps.notifications.workflow.stratergies.email_stratergy import (
            EmailStratergy,
        )
        from apps.notifications.workflow.stratergies.sms_stratergy import SMSStratergy
        from apps.notifications.workflow.stratergies.webhook_stratergy import (
            WebhookStratergy,
        )

        notification_stratergy_registry.register(EmailStratergy)
        notification_stratergy_registry.register(SMSStratergy)
        notification_stratergy_registry.register(WebhookStratergy)

    def register_resolvers(self):
        from apps.notifications.workflow.resolvers import resolver_registry
        from apps.notifications.workflow.resolvers.email_resolver import EmailResolver
        from apps.notifications.workflow.resolvers.sms_resolver import SMSResolver
        from apps.notifications.workflow.resolvers.webhook_resolver import (
            WebHookResolver,
        )

        resolver_registry.register(EmailResolver)
        resolver_registry.register(SMSResolver)
        resolver_registry.register(WebHookResolver)
