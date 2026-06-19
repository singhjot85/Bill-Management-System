import logging
import typing

from django.template import Template, context

from apps.notifications.models import NotificationTemplate
from apps.notifications.exceptions import TemplateHelperException

if typing.TYPE_CHECKING:
    from apps.notifications.workflow.resolvers import ChannelInstruction

LOGGER = logging.getLogger()


class TemplateHelperMixin:
    """
    Helper mixin for Template related feature's in a Stratergy.
    Cannot work independently, needs to be inhereted in a Strattegry.
    """

    _template_model: "NotificationTemplate"
    _instructions: "ChannelInstruction"

    HTML_FIELD = "html"
    SUBJECT_FIELD = "subject"
    PLAIN_TEXT_FIELD = "plain_text"
    TEMPLATE_DB_FIELDS = (HTML_FIELD, PLAIN_TEXT_FIELD, SUBJECT_FIELD)

    @property
    def template(self) -> "NotificationTemplate":
        if hasattr(self, "_template_object"):
            return self._template_object

        return self.fetch_template()

    def fetch_template(self) -> "NotificationTemplate":
        """
        Fetch Template from Database, based on the _instruction on current object.

        Returns:
            "NotificationTemplate": Template object from database
        """
        if (
            not hasattr(self, "_instructions")
            or not self._instructions
            or not self._instructions.template_name
            or not self._instructions.channel_type
        ):
            raise TemplateHelperException("Unable to fetch template, invalid channel instructions.")

        if not hasattr(self, "_template_model"):
            self._template_model = self.get_template_model()

        self._template_object = self._template_model.objects.filter(
            template_name=self._instructions.template_name,
            channel=self._instructions.channel_type,
        ).first()

        return self._template_object

    def get_template_model(self) -> "NotificationTemplate":
        """Getter for database template model, can be override if for some stratergy it changes"""
        return NotificationTemplate

    # Subject
    def subject_pre_render_hook(self, string: str, data: dict, *args, **kwargs) -> tuple[str, dict]:
        """
        Hook to be executed before rendering the subject.
        Should mostly handle pre-processing and validations

        Args:
            string (str): Subject String to render.
            data (dict): Context dict to fill in subject.
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            template_string (str): pre-processed subject string.
            context_data (dict): pre-processed context data.
        """
        if not string:
            raise TemplateHelperException("Template String not provided.")

        if not data:
            data = {}

        data = context.Context(data)

        return string, data

    def render_subject(self, data: dict, string: str = None, *args, **kwargs) -> str:
        """
        Render Subject from template.

        Args:
            data (dict): Context data.
            string (str): Template String, optional (default: None).
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            str: Rendered Template.
        """
        return self._render(data, string, self.SUBJECT_FIELD, args, kwargs)

    def subject_post_render_hook(self, rendered: str, *args, **kwargs) -> str:
        """Hook to be executed after the rendering logic.
        Mostly post processing logic and validations

        Args:
            rendered(str): Post processed render
        """
        return rendered.strip()

    # Html Content
    def html_pre_render_hook(self, string: str, data: dict, *args, **kwargs) -> tuple[str, dict]:
        """
        Hook to be executed before rendering the html message.
        Should mostly handle pre-processing and validations

        Args:
            string (str): Html template String to render.
            data (dict): Context dict to fill in html template.
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            template_string (str): pre-processed template string.
            context_data (dict): pre-processed context data.
        """
        if not string:
            raise TemplateHelperException("Template String not provided.")

        if not data:
            data = {}

        data = context.Context(data)

        return string, data

    def render_html(self, data: dict, string: str = None, *args, **kwargs) -> str:
        """
        Render HTML from template.

        Args:
            data (dict): Context data.
            string (str): Template String, optional (default: None).
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            str: Rendered Template.
        """
        return self._render(data, string, self.HTML_FIELD, args, kwargs)

    def html_post_render_hook(self, rendered: str, *args, **kwargs) -> str:
        """Hook to be executed after the rendering logic.
        Mostly post processing logic and validations

        Args:
            rendered(str): Post processed render
        """

        return rendered.strip()

    # Plain Text
    def plain_text_pre_render_hook(self, string: str, data: dict, *args, **kwargs) -> tuple[str, dict]:
        """
        Hook to be executed before rendering the text message.
        Should mostly handle pre-processing and validations

        Args:
            string (str): Text template String to render.
            data (dict): Context dict to fill in html template.
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            template_string (str): pre-processed template string.
            context_data (dict): pre-processed context data.
        """
        if not string:
            raise TemplateHelperException("Template String not provided.")

        if not data:
            data = {}

        data = context.Context(data)

        return string, data

    def render_plain_text(self, data: dict, string: str = None, *args, **kwargs) -> str:
        """
        Render HTML from template.

        Args:
            data (dict): Context data.
            string (str): Template String, optional (default: None).
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            str: Rendered Template.
        """
        return self._render(data, string, self.PLAIN_TEXT_FIELD, args, kwargs)

    def plain_text_post_render_hook(self, rendered: str, *args, **kwargs) -> str:
        """Hook to be executed after the rendering logic.
        Mostly post processing logic and validations

        Args:
            rendered(str): Post processed render
        """

        return rendered.strip()

    def _render(self, data: dict, string: str, type: str = PLAIN_TEXT_FIELD, *args, **kwargs) -> str:
        """
        Atomic render to logic to save code rewriting.

        Args:
            data (dict): Context Data.
            string (str): Template String, optional (default: fetched from db).
            type (str): DB field name to process, optional (default: PLAIN_TEXT_FIELD).
            *args (type): Description.
            **kwargs (type): Description.

        Returns:
            str: Rendered Message
        """

        if not string:
            if type not in self.TEMPLATE_DB_FIELDS:
                raise TemplateHelperException(
                    f"Invalid type for render given: {type}, expected: {self.TEMPLATE_DB_FIELDS}"
                )
            string = getattr(self.template(), type)

        if hasattr(self, f"{type}_pre_render_hook"):
            LOGGER.info(f"Executing pre-processing hook for [{type}]")
            string, data = getattr(self, f"{type}_pre_render_hook")(string, data, *args, **kwargs)

        render = Template(string).render(data)

        if hasattr(self, f"{type}_post_render_hook"):
            LOGGER.info(f"Executing post-processing hook for [{type}]")
            getattr(self, f"{type}_post_render_hook")(render * args, **kwargs)

        return render
