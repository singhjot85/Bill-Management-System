import logging
from abc import ABC, abstractmethod

from django.template import Template

LOGGER = logging.getLogger()


class InvalidTemplateExecption(Exception):
    pass


class BaseStratergy(ABC):
    label = ""
    _message = None  # Final Rendered Message

    @classmethod
    def pre_render_hook(self, template_string: str, context_data: dict, *args, **kwargs) -> tuple[str, dict]:
        """Hooks to be executed before rendering the message.
        Should mostly handle pre-processing and validations
        Args:
            template_string (str): Template String to render.
            context_data (dict): Context dict to fill data in template.
        Returns:
            context_data (dict): Context dict to fill data in template.
            template_string (str): Template String to render.
        """
        if not context_data:
            context_data = {}

        return template_string, context_data

    def render_message(self, template_string: str, context_data: dict, *args, **kwargs) -> str:
        """
        Render a message from given context data. This is one of helper method(s)
        Args:
            template_string (str): Template String to render.
            context_data (dict): Context dict to fill data in template.
        Returns:
            rendered_message (str): Rendered message.
        """
        if self._message:
            return self._message

        if not template_string:
            raise InvalidTemplateExecption("Template string is empty")

        template_string, context_data = self.pre_render_hook(template_string, context_data, args, kwargs)

        rendered_message = Template(template_string).render(context_data)

        self._message = self.post_render_hook(rendered_message, args, kwargs)

        return self._message
    
    @classmethod
    def post_render_hook(self, rendered_message: str, *args, **kwargs):
        """Hook to be executed after the rendering logic.

        Args:
            rendered_message (str): Final rendered message
        """


    @abstractmethod
    def _send(self, *args, **kwargs):
        """Actual send logic belongs here, this can be overriden in each subclass."""
        pass

    def send(cls, *args, **kwargs):
        """
        Main Send caller, that calls the send logic, and also handles logging and error handling.
        
        kwargs:
            raise_on_exception (bool): Whether to raise exception, or just log it silently.
        
        Example Usage:
            
            >>> manager = notification_stratergy_registry.get("email")
            >>> manager.send()
            >>> manager = notification_stratergy_registry.get("email")
            >>> manager.send(raise_on_exception=True)
        """

        LOGGER.info("Sending %s notification...", cls.label)

        try:
            cls._send(args, kwargs)
        except Exception as ex:
            LOGGER.error("Error in sending %s", cls.label, exc_info=ex)
            if kwargs.get("raise_on_exception", False):
                raise
            

        LOGGER.info("Successfully sent %s notification", cls.label)
