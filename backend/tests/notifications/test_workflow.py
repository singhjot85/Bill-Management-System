from unittest.mock import MagicMock, patch
import pytest
from django.core.cache import cache
from django.contrib.auth import get_user_model
from constance.test import override_config

from apps.notifications.constants import (
    ChannelTypeChoices,
    EventTypeChoices,
    NotificationTemplateChoices,
    LogStatusChoices,
)
from apps.notifications.exceptions import (
    InvalidEventException,
    NotificationDispatcherException,
    NotificationResolverException,
)
from apps.notifications.models import (
    NotificationLog,
    NotificationPreferences,
    NotificationTemplate,
)
from apps.notifications.workflow.dispatcher import Dispatcher
from apps.notifications.workflow.resolvers import BaseResolver, ChannelInstruction, ResolverFactory
from apps.notifications.workflow.resolvers.email_resolver import EmailInstructions, EmailResolver
from apps.notifications.workflow.resolvers.sms_resolver import SmsInstructions, SMSResolver
from apps.notifications.workflow.stratergies.email_stratergy import EmailStratergy
from apps.notifications.workflow.trigger import NotificationEvent, trigger_notifications
from apps.setup.constants import ConfigurationInterfaceChoices
from apps.setup.models import Configurations
from tests.factories import (
    ConfigurationsFactory,
    CustomerFactory,
    NotificationLogFactory,
    NotificationPreferencesFactory,
    NotificationTemplateFactory,
    UserFactory,
)

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestNotificationTrigger:
    """
    Tests for the notification trigger phase.
    """

    def test_notification_event_validation_success(self):
        """Checks if a valid NotificationEvent initializes correctly."""
        party_id = "00000000-0000-0000-0000-000000000001"
        event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=party_id,
            data={"test": "data"}
        )
        assert event.event_type == EventTypeChoices.WELCOME_USER.value
        assert event.assosciated_party == party_id
        assert event.data == {"test": "data"}

    def test_notification_event_validation_invalid_event_type(self):
        """Verifies that validation fails with empty or invalid event type."""
        with pytest.raises(InvalidEventException):
            NotificationEvent(event_type="")

        with pytest.raises(InvalidEventException):
            NotificationEvent(event_type="invalid_event_type")

    def test_notification_event_validation_invalid_party(self):
        """Verifies that associated party validation fails with non-UUID, non-numeric strings."""
        with pytest.raises(InvalidEventException):
            NotificationEvent(event_type=EventTypeChoices.WELCOME_USER.value, assosciated_party="not-a-uuid")

    @patch("apps.notifications.workflow.trigger.Dispatcher")
    @patch("apps.notifications.workflow.trigger.ResolverFactory")
    def test_trigger_notifications_success(self, mock_resolver_factory, mock_dispatcher_cls):
        """Validates that trigger_notifications successfully resolves and dispatches events."""
        party_id = "00000000-0000-0000-0000-000000000001"
        instruction = ChannelInstruction(
            log_id="00000000-0000-0000-0000-000000000002",
            user_id=party_id,
            channel_type=ChannelTypeChoices.EMAIL.value
        )
        
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = [instruction]
        mock_resolver_factory.return_value = mock_resolver

        mock_dispatcher = MagicMock()
        mock_dispatcher_cls.return_value = mock_dispatcher

        trigger_notifications(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_parties=[party_id],
            data={"template_name": "welcome_new_user"}
        )

        mock_resolver_factory.assert_called_once()
        mock_resolver.resolve.assert_called_once()
        mock_dispatcher_cls.assert_called_once_with(instruction, task_name=None)
        mock_dispatcher.dispatch.assert_called_once()

    @patch("apps.notifications.workflow.trigger.Dispatcher")
    @patch("apps.notifications.workflow.trigger.ResolverFactory")
    def test_trigger_notifications_multiple_parties(self, mock_resolver_factory, mock_dispatcher_cls):
        """Verifies that trigger_notifications resolves separate events when multiple parties are supplied."""
        party1 = "00000000-0000-0000-0000-000000000001"
        party2 = "00000000-0000-0000-0000-000000000002"
        
        mock_resolver = MagicMock()
        mock_resolver.resolve.return_value = []
        mock_resolver_factory.return_value = mock_resolver

        trigger_notifications(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_parties=[party1, party2],
            data={"template_name": "welcome_new_user"}
        )

        assert mock_resolver_factory.call_count == 2

    @patch("apps.notifications.workflow.trigger.ResolverFactory")
    def test_trigger_notifications_exceptions_raised(self, mock_resolver_factory):
        """Verifies that exceptions in the workflow resolution are bubbles up."""
        party_id = "00000000-0000-0000-0000-000000000001"
        mock_resolver_factory.side_effect = NotificationResolverException("Resolver error")

        with pytest.raises(NotificationResolverException):
            trigger_notifications(
                event_type=EventTypeChoices.WELCOME_USER.value,
                assosciated_parties=[party_id]
            )


class TestNotificationResolver:
    """
    Tests for the resolver phase.
    """

    def setup_method(self):
        # Create tenant config for the tests using ConfigurationsFactory
        Configurations.objects.all().delete()
        NotificationLog._base_manager.all().delete()
        NotificationPreferences._base_manager.all().delete()
        User.objects.all().delete()
        CustomerFactory._meta.model._base_manager.all().delete()
        cache.clear()

        self.config = ConfigurationsFactory(
            interface_type=ConfigurationInterfaceChoices.NOTIFICATION_CONFIGURATION.value,
            details={"tenant_preferences": ["email"]}
        )
        self.user = UserFactory()
        self.customer = CustomerFactory()
        self.event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "welcome_new_user"}
        )

    def test_resolver_factory_no_config(self):
        """Verifies that missing tenant configuration raises an exception."""
        Configurations.objects.all().delete()
        cache.clear()

        with pytest.raises(NotificationResolverException) as exc:
            ResolverFactory(self.event, str(self.user.id))

        assert "Notifications not configured for tenant" in str(exc.value)

    def test_resolver_factory_no_tenant_preferences(self):
        """Verifies that missing preferences in configuration raises an exception."""
        self.config.details = {}
        self.config.save()

        with pytest.raises(NotificationResolverException) as exc:
            ResolverFactory(self.event, str(self.user.id))

        assert "Tenant Preferences not found for current tenant" in str(exc.value)

    def test_resolver_factory_preference_resolution(self):
        """Checks resolving effective channel preferences when tenant & user configurations align."""
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )

        resolver_factory = ResolverFactory(self.event, str(self.user.id))
        assert resolver_factory.tenant_preferences == ["email"]
        assert resolver_factory.user_preferences == ["email"]
        assert resolver_factory.preferences == {"email"}

    def test_resolver_factory_preference_resolution_opt_out(self):
        """Verifies that channel is excluded if user opted-out."""
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=False
        )

        resolver_factory = ResolverFactory(self.event, str(self.user.id))
        assert resolver_factory.preferences == set()

    def test_resolver_factory_skip_user_preferences(self):
        """Verifies that missing party skips user preference checks and relies on event/tenant preferences."""
        resolver_factory = ResolverFactory(self.event, None)

        assert resolver_factory.skip_user_pref is True
        assert resolver_factory.preferences == {"email"}

    def test_resolver_factory_resolve_calls_resolver(self):
        """Verifies resolver generates correct instruction dataclasses."""
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )

        resolver_factory = ResolverFactory(self.event, str(self.user.id))
        instructions = resolver_factory.resolve()
        
        assert len(instructions) == 1
        instruction = instructions[0]
        assert isinstance(instruction, EmailInstructions)
        assert instruction.user_id == str(self.user.id)
        assert instruction.channel_type == ChannelTypeChoices.EMAIL.value
        assert instruction.template_name == "welcome_new_user"

    def test_resolver_factory_multiple_tenant_preferences(self):
        """Verifies resolver resolves multiple channel preferences if both tenant and user opt-in."""
        self.config.details = {"tenant_preferences": ["email", "sms"]}
        self.config.save()
        cache.clear()

        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            preference_type=ChannelTypeChoices.SMS.value,
            opted_in=True
        )

        invoice_event = NotificationEvent(
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "invoice_created"}
        )

        resolver_factory = ResolverFactory(invoice_event, str(self.user.id))
        assert resolver_factory.preferences == {"email", "sms"}

    def test_resolver_factory_intersection_partial(self):
        """Tests that intersection logic excludes user preferences not enabled by the tenant."""
        self.config.details = {"tenant_preferences": ["email"]}
        self.config.save()
        cache.clear()

        # User opted in for both, but tenant only allows email
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            preference_type=ChannelTypeChoices.SMS.value,
            opted_in=True
        )

        invoice_event = NotificationEvent(
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "invoice_created"}
        )

        resolver_factory = ResolverFactory(invoice_event, str(self.user.id))
        assert resolver_factory.preferences == {"email"}

    def test_resolver_factory_event_type_constraint(self):
        """Tests that EventPreferences further restricts the preferences resolved."""
        self.config.details = {"tenant_preferences": ["email", "sms"]}
        self.config.save()
        cache.clear()

        # User has opted in for email and sms
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.SMS.value,
            opted_in=True
        )

        # Welcome user event only supports email (according to EventPreferences.WELCOME_USER)
        resolver_factory = ResolverFactory(self.event, str(self.user.id))
        assert resolver_factory.preferences == {"email"}

    def test_resolver_factory_party_does_not_exist(self):
        """Verifies ResolverFactory doesn't raise error if party ID is non-existent, but falls back to empty user preferences."""
        resolver_factory = ResolverFactory(self.event, "00000000-0000-0000-0000-000000000099")
        assert resolver_factory.party is None
        assert resolver_factory.user_preferences == []
        assert resolver_factory.preferences == set()

    def test_resolver_factory_party_is_customer(self):
        """Verifies ResolverFactory correctly resolves preferences when the associated party is a Customer (UUID PK)."""
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )
        resolver_factory = ResolverFactory(self.event, str(self.customer.id))
        assert resolver_factory.party == self.customer
        assert resolver_factory.user_preferences == ["email"]
        assert resolver_factory.preferences == {"email"}

    def test_resolver_factory_user_opted_in_different_event(self):
        """Checks that user preferences for other event types do not opt the user into the current event."""
        # Opt-in to email but for INVOICE_CREATED instead of WELCOME_USER
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.INVOICE_CREATED.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )
        resolver_factory = ResolverFactory(self.event, str(self.user.id))
        assert resolver_factory.user_preferences == []
        assert resolver_factory.preferences == set()


class TestNotificationDispatcher:
    """
    Tests for the dispatcher phase.
    """

    def setup_method(self):
        self.instruction = EmailInstructions(
            log_id="00000000-0000-0000-0000-000000000001",
            user_id="00000000-0000-0000-0000-000000000002",
            channel_type=ChannelTypeChoices.EMAIL.value,
            context_data={"name": "John Doe"},
            template_name=NotificationTemplateChoices.WELCOME_NEW_USER.value
        )
        self.dispatcher = Dispatcher(self.instruction)

    def test_dispatcher_initialization(self):
        """Verifies default task configuration."""
        assert self.dispatcher._instruction == self.instruction
        from apps.tasks.registry import TaskNames
        assert self.dispatcher._task_name == TaskNames.NOTIFICATION_TASK

    def test_dispatcher_task_kwargs(self):
        """Verifies task kwargs correctly extract raw dictionary parameters from instruction."""
        kwargs = self.dispatcher.task_kwargs
        assert kwargs["log_id"] == "00000000-0000-0000-0000-000000000001"
        assert kwargs["user_id"] == "00000000-0000-0000-0000-000000000002"
        assert kwargs["channel_type"] == ChannelTypeChoices.EMAIL.value
        assert kwargs["template_name"] == NotificationTemplateChoices.WELCOME_NEW_USER.value
        assert kwargs["context_data"] == {"name": "John Doe"}

    @patch("apps.notifications.workflow.dispatcher.queue_task")
    def test_dispatcher_dispatch_success(self, mock_queue_task):
        """Verifies Dispatcher calls queue_task with standard parameters and commit safety."""
        self.dispatcher.dispatch()
        mock_queue_task.assert_called_once_with(
            task=self.dispatcher._task_name,
            on_commit=True,
            task_args=None,
            task_kwargs=self.dispatcher.task_kwargs,
            idempotency_key="email-00000000-0000-0000-0000-000000000001"
        )

    @patch("apps.notifications.workflow.dispatcher.queue_task")
    def test_dispatcher_dispatch_failure(self, mock_queue_task):
        """Checks dispatcher exception translation when queue_task fails."""
        mock_queue_task.side_effect = Exception("Queue error")
        with pytest.raises(NotificationDispatcherException) as exc:
            self.dispatcher.dispatch()
        assert "Error in queing celery task" in str(exc.value)


class TestEmailStratergy:
    """
    Tests for the Email Strategy phase.
    """

    def setup_method(self):
        NotificationPreferences._base_manager.all().delete()
        User.objects.all().delete()
        NotificationLog._base_manager.all().delete()
        NotificationTemplate.objects.all().delete() 
        CustomerFactory._meta.model._base_manager.all().delete()

        self.user = UserFactory(email="user@example.com")
        self.customer = CustomerFactory(email="customer@example.com")
        self.log = NotificationLogFactory(channel=ChannelTypeChoices.EMAIL.value)
        self.template = NotificationTemplateFactory(
            template_name=NotificationTemplateChoices.WELCOME_NEW_USER.value,
            channel=ChannelTypeChoices.EMAIL.value,
            subject="Welcome {{ name }}",
            plain_text="Hello {{ name }}, welcome to BMA.",
            html="<h1>Hello {{ name }}</h1>"
        )

    def test_strategy_associated_party_user(self):
        """Checks User model resolution based on user_id."""
        instructions = {
            "log_id": str(self.log.id),
            "user_id": str(self.user.id),
            "channel_type": ChannelTypeChoices.EMAIL.value,
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "context_data": {"name": "John Doe"}
        }
        strategy = EmailStratergy(**instructions)
        party = strategy.associated_party
        assert party == self.user

    def test_strategy_associated_party_customer(self):
        """Checks Customer model fallback resolution when user_id matches Customer instead of User."""
        instructions = {
            "log_id": str(self.log.id),
            "user_id": str(self.customer.id),
            "channel_type": ChannelTypeChoices.EMAIL.value,
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "context_data": {"name": "John Doe"}
        }
        strategy = EmailStratergy(**instructions)
        party = strategy.associated_party
        assert party == self.customer

    def test_strategy_associated_party_not_found(self):
        """Checks that NotificationStrategyException is raised when party is not found in database."""
        instructions = {
            "log_id": str(self.log.id),
            "user_id": "00000000-0000-0000-0000-000000000099",
            "channel_type": ChannelTypeChoices.EMAIL.value,
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "context_data": {"name": "John Doe"}
        }
        strategy = EmailStratergy(**instructions)
        from apps.notifications.workflow.stratergies.base_stratergy import NotificationStrategyException
        with pytest.raises(NotificationStrategyException) as exc:
            strategy.associated_party
        assert "does not exist" in str(exc.value)

    @patch("apps.notifications.workflow.stratergies.email_stratergy.get_connection")
    def test_email_strategy_get_connection(self, mock_get_connection):
        """Validates connection loading based on Constance parameters (mock vs SMTP)."""
        instructions = {
            "log_id": str(self.log.id),
            "user_id": str(self.user.id),
            "channel_type": ChannelTypeChoices.EMAIL.value,
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "context_data": {"name": "John Doe"}
        }
        strategy = EmailStratergy(**instructions)

        with override_config(USE_MOCK_EMAIL_SERVICE=True, EMAIL_BACKEND_CHOICES="mock_backend"):
            strategy.get_connection
            mock_get_connection.assert_called_with("mock_backend")

        with override_config(USE_MOCK_EMAIL_SERVICE=False):
            strategy.get_connection
            from config.settings.constants import DJANGO_SMTP_BACKEND
            mock_get_connection.assert_called_with(DJANGO_SMTP_BACKEND)

    @patch("django.core.mail.EmailMessage.send")
    def test_email_strategy_send_multipart(self, mock_send):
        """Verifies multipart email content structure is generated and dispatched."""
        instructions = {
            "log_id": str(self.log.id),
            "user_id": str(self.user.id),
            "channel_type": ChannelTypeChoices.EMAIL.value,
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "context_data": {"name": "John Doe"}
        }
        strategy = EmailStratergy(**instructions)
        strategy.send()
        
        mock_send.assert_called_once()

    @patch("django.core.mail.EmailMessage.send")
    def test_email_strategy_send_plain(self, mock_send):
        """Verifies plain text email rendering and dispatching."""
        instructions = {
            "log_id": str(self.log.id),
            "user_id": str(self.user.id),
            "channel_type": ChannelTypeChoices.EMAIL.value,
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "context_data": {"name": "John Doe"}
        }
        strategy = EmailStratergy(**instructions)
        strategy.send(render_html=False)
        
        mock_send.assert_called_once()


class TestBaseResolver:
    """
    Tests for the BaseResolver functionality.
    """

    class DummyResolver(BaseResolver):
        def _get_instruction_dataclass(self, *args, **kwargs):
            return ChannelInstruction

        def _get_dataclass_data(self, *args, **kwargs):
            return super()._get_dataclass_data(*args, **kwargs)

    def setup_method(self):
        NotificationPreferences._base_manager.all().delete()
        NotificationLog._base_manager.all().delete()
        User.objects.all().delete()

        self.user = UserFactory()
        self.event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "welcome_new_user"}
        )
        self.resolver = self.DummyResolver(self.event, ChannelTypeChoices.EMAIL.value)

    def test_base_resolver_initialization_invalid_channel(self):
        """Verifies Resolver fails to initialize with an invalid channel."""
        with pytest.raises(NotificationResolverException) as exc:
            self.DummyResolver(self.event, "invalid_channel")
        assert "Invalid Channel type" in str(exc.value)

    def test_base_resolver_initialize_log(self):
        """Verifies base resolver successfully initializes a NotificationLog record."""
        log = self.resolver.initialize_log()
        assert log.id is not None
        assert log.status == LogStatusChoices.QUEUED.value
        assert log.channel == ChannelTypeChoices.EMAIL.value

    def test_base_resolver_get_dataclass_data(self):
        """Verifies default properties generated for dataclass payload."""
        data = self.resolver._get_dataclass_data()
        assert "log_id" in data
        assert data["user_id"] == str(self.user.id)
        assert data["channel_type"] == ChannelTypeChoices.EMAIL.value
        assert data["context_data"] == {"template_name": "welcome_new_user"}

    def test_base_resolver_resolve_success(self):
        """Verifies resolve() successfully returns ChannelInstruction with correct data."""
        instruction = self.resolver.resolve()
        assert isinstance(instruction, ChannelInstruction)
        assert instruction.user_id == str(self.user.id)
        assert instruction.channel_type == ChannelTypeChoices.EMAIL.value
        assert instruction.context_data == {"template_name": "welcome_new_user"}


class TestEmailResolver:
    """
    Tests for EmailResolver.
    """

    def setup_method(self):
        NotificationPreferences._base_manager.all().delete()
        NotificationLog._base_manager.all().delete()
        User.objects.all().delete()

        self.user = UserFactory()
        self.event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "welcome_new_user"}
        )
        self.resolver = EmailResolver(self.event, ChannelTypeChoices.EMAIL.value)

    def test_email_resolver_success(self):
        """Verifies resolve creates EmailInstructions with template details."""
        instruction = self.resolver.resolve()
        assert isinstance(instruction, EmailInstructions)
        assert instruction.template_name == "welcome_new_user"

    def test_email_resolver_invalid_template(self):
        """Checks validation for invalid template name."""
        invalid_event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "invalid_template"}
        )
        resolver = EmailResolver(invalid_event, ChannelTypeChoices.EMAIL.value)
        with pytest.raises(NotificationResolverException) as exc:
            resolver.resolve()
        assert "Invalid Template name" in str(exc.value)

    def test_email_resolver_missing_template_name(self):
        """Checks validation error raised when template name is missing."""
        invalid_event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={}
        )
        resolver = EmailResolver(invalid_event, ChannelTypeChoices.EMAIL.value)
        with pytest.raises(NotificationResolverException) as exc:
            resolver.resolve()
        assert "Template name is required" in str(exc.value)


class TestSMSResolver:
    """
    Tests for SMSResolver.
    """

    def setup_method(self):
        NotificationPreferences._base_manager.all().delete()
        NotificationLog._base_manager.all().delete()
        User.objects.all().delete()

        self.user = UserFactory()
        self.event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "welcome_new_user"}
        )
        self.resolver = SMSResolver(self.event, ChannelTypeChoices.SMS.value)

    def test_sms_resolver_success(self):
        """Verifies resolve creates SmsInstructions with template details."""
        instruction = self.resolver.resolve()
        assert isinstance(instruction, SmsInstructions)
        assert instruction.template_name == "welcome_new_user"

    def test_sms_resolver_invalid_template(self):
        """Checks validation for missing/invalid template names in SmsInstructions."""
        invalid_event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={"template_name": "invalid_template"}
        )
        resolver = SMSResolver(invalid_event, ChannelTypeChoices.SMS.value)
        with pytest.raises(NotificationResolverException) as exc:
            resolver.resolve()
        assert "Invalid Template name" in str(exc.value)

    def test_sms_resolver_missing_template_name(self):
        """Verifies validation error raised when SMS template name is missing."""
        invalid_event = NotificationEvent(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_party=str(self.user.id),
            data={}
        )
        resolver = SMSResolver(invalid_event, ChannelTypeChoices.SMS.value)
        with pytest.raises(NotificationResolverException) as exc:
            resolver.resolve()
        assert "Template name is required" in str(exc.value)


@pytest.mark.django_db(transaction=True)
class TestNotificationEndToEnd:
    """
    End-to-End integration tests for the notification flow.
    """

    def setup_method(self):
        # Setup tenant configuration
        Configurations.objects.all().delete()
        NotificationLog._base_manager.all().delete()
        NotificationPreferences._base_manager.all().delete()
        User.objects.all().delete()
        CustomerFactory._meta.model._base_manager.all().delete()
        cache.clear()

        self.config = ConfigurationsFactory(
            interface_type=ConfigurationInterfaceChoices.NOTIFICATION_CONFIGURATION.value,
            details={"tenant_preferences": ["email"]}
        )

        # Setup user and customer records
        self.user = UserFactory(email="receiver@example.com")
        self.customer = CustomerFactory(email="receiver@example.com")

        # Opt user in for welcome emails
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=True
        )

        # Create template in DB
        self.template = NotificationTemplateFactory(
            template_name=NotificationTemplateChoices.WELCOME_NEW_USER.value,
            event_type=EventTypeChoices.WELCOME_USER.value,
            channel=ChannelTypeChoices.EMAIL.value,
            subject="Welcome {{ name }}!",
            plain_text="Hello {{ name }}, welcome to our platform."
        )

    @patch("django.core.mail.EmailMessage.send")
    def test_notification_e2e_flow_success(self, mock_send):
        """
        Runs the full notification pipeline:
        1. Trigger flow via trigger_notifications
        2. Resolve preferences to email
        3. Dispatch synchronous Celery tasks (since eager is enabled)
        4. Execute strategy and send the email
        """
        assert NotificationLog.objects.count() == 0

        # Trigger
        trigger_notifications(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_parties=[str(self.user.id)],
            data={
                "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
                "name": "Jane Doe"
            }
        )

        # Assertions
        # 1. Log has been created in status QUEUED
        assert NotificationLog.objects.count() == 1
        log = NotificationLog.objects.first()
        assert log.status == LogStatusChoices.QUEUED.value
        assert log.channel == ChannelTypeChoices.EMAIL.value
        assert log.context_data == {
            "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
            "name": "Jane Doe"
        }

        # 2. Strategy send was executed (EmailMessage.send mocked)
        mock_send.assert_called_once()

    @patch("django.core.mail.EmailMessage.send")
    def test_notification_e2e_flow_opted_out(self, mock_send):
        """
        Runs the full notification pipeline where the user is opted out:
        1. Trigger flow via trigger_notifications
        2. Resolve preferences finds that user has not opted in (or has opted out)
        3. No tasks are queued and no emails are sent
        """
        # Opt-out the user explicitly
        NotificationPreferences.objects.all().delete()
        NotificationPreferencesFactory(
            user=self.user,
            customer=self.customer,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=False
        )

        assert NotificationLog.objects.count() == 0

        # Trigger
        trigger_notifications(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_parties=[str(self.user.id)],
            data={
                "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
                "name": "Jane Doe"
            }
        )

        # Assertions: No logs are created and no emails are sent
        assert NotificationLog.objects.count() == 0
        mock_send.assert_not_called()

    @patch("django.core.mail.EmailMessage.send")
    def test_notification_e2e_flow_multiple_parties(self, mock_send):
        """
        Runs the pipeline with multiple associated parties (one opted-in, one opted-out):
        1. Trigger flow via trigger_notifications with two party IDs
        2. Verify that only one log is created and one email is sent
        """
        user_opted_out = UserFactory(email="optout@example.com")
        customer_opted_out = CustomerFactory(email="optout@example.com")

        # User opted-out has opted_in = False
        NotificationPreferencesFactory(
            user=user_opted_out,
            customer=customer_opted_out,
            event_type=EventTypeChoices.WELCOME_USER.value,
            preference_type=ChannelTypeChoices.EMAIL.value,
            opted_in=False
        )

        assert NotificationLog.objects.count() == 0

        # Trigger for both users
        trigger_notifications(
            event_type=EventTypeChoices.WELCOME_USER.value,
            assosciated_parties=[str(self.user.id), str(user_opted_out.id)],
            data={
                "template_name": NotificationTemplateChoices.WELCOME_NEW_USER.value,
                "name": "Jane Doe"
            }
        )

        # Assertions
        # 1. Exactly one log is created (for the opted-in user)
        assert NotificationLog.objects.count() == 1
        log = NotificationLog.objects.first()
        assert log.channel == ChannelTypeChoices.EMAIL.value
        assert log.context_data["name"] == "Jane Doe"

        # 2. Exactly one email is sent
        mock_send.assert_called_once()
