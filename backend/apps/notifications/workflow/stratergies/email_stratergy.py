import typing

from constance import config
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection

from apps.notifications.constants import ChannelTypeChoices, LogStatusChoices
from apps.notifications.exceptions import NotificationStratergyException
from apps.notifications.workflow.stratergies import BaseStratergy, TemplateHelperMixin
from config.settings.constances import ConstanceFields
from config.settings.constants import DJANGO_SMTP_BACKEND

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

    message: typing.Union[EmailMessage, EmailMultiAlternatives] = None

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

    @property
    def subject(self, *args, **kwargs) -> str:
        if hasattr(self, "_subject") and getattr(self, "_subject"):
            return self._subject

        self._subject = self.render_subject(self._instructions.context_data, *args, **kwargs)
        return self._subject

    @property
    def plain_text(self, *args, **kwargs) -> str:
        if hasattr(self, "_plain_text") and getattr(self, "_plain_text"):
            return self._plain_text

        self._plain_text = self.render_plain_text(self._instructions.context_data, *args, **kwargs)
        return self._plain_text

    @property
    def html(self, *args, **kwargs) -> str:
        if hasattr(self, "_html") and getattr(self, "_html"):
            return self._html

        self._html = self.render_html(self._instructions.context_data, *args, **kwargs)
        return self._html

    def get_template_snapshot(self) -> str:
        """Prepare template snapshot for logging"""
        snapshot = ""

        if self.subject:
            snapshot += self.subject
        if self.plain_text:
            snapshot += f"\n\n{self.plain_text}"
        if self.html:
            snapshot += f"\n\n{self.html}"

        return snapshot

    def pre_send_hooks(self, *args, **kwargs):
        """Pre hooks before sending the mail"""
        self.log_obj.status = LogStatusChoices.IN_PROGRESS.value
        self.log_obj.template = self.template
        self.log_obj.template_snapshot = self.get_template_snapshot()
        self.log_obj.context_data = (
            self._instructions.context_data if self._instructions and self._instructions.context_data else {}
        )
        self.log_obj.save(update_fields=["status", "template", "template_snapshot", "context_data"])

    def _send(self, render_html: bool = True, *args, **kwargs):
        """
        Send logic for Email Messages.

        Args:
            render_html (bool): Render HTML message.
            *args (type): Description.
            **kwargs (type): Description.
        """

        if render_html:
            self.message = EmailMultiAlternatives(
                connection=self.get_connection,
                subject=self.subject,
                body=self.plain_text or "",
                from_email=self.from_email,
                to=self.to_email,
            )
            self.message.attach_alternative(self.html, "text/html")
        else:
            self.message = EmailMessage(
                connection=self.get_connection,
                subject=self.subject,
                body=self.plain_text or "",
                from_email=self.from_email,
                to=self.to_email,
            )

        if not self.message:
            raise NotificationStratergyException("Unable to build a email message from given instructions.")

        self.message.send()
