import typing

from constance import config
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection

from config.settings.constances import ConstanceFields
from config.settings.constants import DJANGO_SMTP_BACKEND
from apps.notifications.constants import ChannelTypeChoices
from apps.notifications.exceptions import NotificationStratergyException
from apps.notifications.workflow.stratergies import (
    BaseStratergy,
    TemplateHelperMixin,
    notification_stratergy_registry,
)

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.resolvers.email_resolver import EmailInstructions


class EmailStratergy(BaseStratergy, TemplateHelperMixin):
    """
    Email Stratergy for notification flow
    TODO: Implement Attachement support.
    """
    _email_be_setting_name = ConstanceFields.EMAIL_BE_CHOICES.field_name
    _use_mock_email_setting_name = ConstanceFields.MOCK_EMAIL_SERV.field_name

    _instructions: "EmailInstructions"
    _channel_type: str = ChannelTypeChoices.EMAIL.value
    label: str = _channel_type.title()
    REGISTERY_KEY = _channel_type

    def get_host(self):
        """Get Email for host user"""
        context_data = self._instructions.context_data
        from_email = context_data.get("from") or context_data.get("host")
        if from_email and isinstance(from_email, str):
            return from_email

        return settings.EMAIL_HOST_USER
    
    @property
    def get_connection(self):
        if not getattr(config, self._use_mock_email_setting_name):
            return get_connection(DJANGO_SMTP_BACKEND)
        
        backend_name = getattr(config, self._email_be_setting_name)
        return get_connection(backend_name)

    @property
    def from_email(self):
        return self.get_host()

    @property
    def to_email(self) -> list[str]:
        return [self.associated_party.email]

    def mulipart_email_message(self, *args, **kwargs) -> "EmailMultiAlternatives":
        """
        Cunstructed message for multi-part emails.

        Returns:
            "EmailMultiAlternatives": Description.
        """
        subject = self.render_subject(self._instructions.context_data, args, kwargs)
        plain_text = self.render_plain_text(self._instructions.context_data, args, kwargs)
        html = self.render_html(self._instructions.context_data, args, kwargs)

        message = EmailMultiAlternatives(
            connection=self.get_connection,
            subject=subject,
            body=plain_text or "",
            from_email=self.from_email,
            to=self.to_email,
        )
        message.attach_alternative(html, "text/html")
        return message

    def email_message(self, *args, **kwargs) -> "EmailMessage":
        """
        Build and return a `EmailMessage` object from given instructions.

        Args:
            *args (type): Description.
            **kwargs (type): Description.
        """
        subject = self.render_subject(self._instructions.context_data, args, kwargs)
        plain_text = self.render_plain_text(self._instructions.context_data, args, kwargs)

        return EmailMessage(
            connection=self.get_connection,
            subject=subject,
            body=plain_text or "",
            from_email=self.from_email,
            to=self.to_email,
        )

    def _send(self, render_html: bool = True, *args, **kwargs):
        """
        Send logic for Email Messages.

        Args:
            render_html (bool): Render HTML message.
            *args (type): Description.
            **kwargs (type): Description.
        """
        message = None
        if render_html:
            message = self.mulipart_email_message()
        else:
            message = self.email_message()

        if not message:
            raise NotificationStratergyException("Unable to build a email message from given instructions.")

        message.send()


notification_stratergy_registry.register(EmailStratergy)
