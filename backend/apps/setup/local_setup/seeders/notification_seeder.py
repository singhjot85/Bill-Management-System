import logging

from django.contrib.auth import get_user_model

from apps.customer_management.models import Customer, CustomerTypeChoices
from apps.notifications.constants import EventPreferences
from apps.notifications.models import NotificationPreferences, NotificationTemplate

from ..constants import seeder_registry
from .base_seeder import BaseSeeder

LOGGER = logging.getLogger()
User = get_user_model()


class NotificationSeeder(BaseSeeder):
    label = "Notification Seeder"
    REGISTERY_KEY = "notifications"
    data_cache_key = "notification_seeder_data"
    notification_seeder_data: dict = None

    def run_in_schema(self) -> str:
        if not self.notification_seeder_data:
            return "public"
        return self.notification_seeder_data.get("OrganizationTenant", {}).get("schema_name", "public")

    def _seed_templates(self):
        """Seed NotificationTemplate"""
        templates_data = self.notification_seeder_data.get("NotificationTemplate", [])
        for data in templates_data:
            resolved_fields = {}
            for field in ["plain_text", "html", "subject"]:
                val = data.get(field)
                self.load_file_fields(val, field, resolved_fields)

            # Filter model fields
            filtered_fields = self.filter_model_fields(NotificationTemplate, data)
            filtered_fields.update(resolved_fields)

            # Idempotency
            uniques, defaults = self.classify_fields(NotificationTemplate, filtered_fields)
            template, created = NotificationTemplate.objects.get_or_create(**uniques, defaults=defaults)
            if not created:
                for k, v in defaults.items():
                    setattr(template, k, v)
                template.save()
                LOGGER.info("Updated NotificationTemplate: %s (%s)", template.template_name, template.channel)
            else:
                LOGGER.info("Created NotificationTemplate: %s (%s)", template.template_name, template.channel)

    def _seed_preferences(self):
        """Seed NotificationPreferences"""
        user_data = self.notification_seeder_data.get("Users", [])
        for u_data in user_data:
            username = u_data.get("username")
            user_obj = User.objects.filter(username=username).first()
            if not user_obj:
                LOGGER.warning("User %s not found. Skipping preference seeding.", username)
                continue

            customer_obj, created_cust = Customer.objects.get_or_create(
                email=user_obj.email,
                defaults={
                    "name": f"{user_obj.first_name} {user_obj.last_name}".strip() or user_obj.username,
                    "phone": "1234567890",
                    "customer_type": CustomerTypeChoices.INTERNAL,
                },
            )
            if created_cust:
                LOGGER.info("Created Customer record for user %s", user_obj.username)

            # Create default preferences for all events and channels
            for ep in EventPreferences:
                event_type = ep.value[0]
                channels = ep.value[1]
                for channel in channels:
                    pref, created_pref = NotificationPreferences.objects.get_or_create(
                        user=user_obj,
                        customer=customer_obj,
                        event_type=event_type,
                        preference_type=channel,
                        defaults={"opted_in": True},
                    )
                    if created_pref:
                        LOGGER.info(
                            "Created default notification preference for %s: event=%s, channel=%s",
                            username,
                            event_type,
                            channel,
                        )

    def seed(self, *args, **kwargs):
        # Notifications models are only in DJANGO_TENANT_PRIVATE_APPS, so they don't exist in the public schema
        schema_name = self.run_in_schema()
        if schema_name == "public":
            LOGGER.info("[%s] Skipping notification seeding for public schema.", self.label)
            return

        self._seed_templates()
        self._seed_preferences()


seeder_registry.register(NotificationSeeder)
