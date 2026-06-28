from apps.notifications.exceptions import NotificationDispatcherException
from apps.notifications.workflow.resolvers import ChannelInstruction
from apps.tasks.registry import TaskNames, queue_task


class Dispatcher:
    """
    Dispatcher consumes some instuctions and create a celery task for those given instructions.
    Its responsibilty is to handle and manage task queuing.
    It also logs the event to datbase, by creating a log entry.
    """

    _default_task_name = TaskNames.NOTIFICATION_TASK

    def __init__(self, instruction: "ChannelInstruction", task_name: str = None):
        """
        Args:
            instruction (ChannelInstruction): instructions for dispatcher and celery task.
            task_name (str, optional): Celery task name to be used.
        """
        self._instruction = instruction
        self._task_name = task_name or self._default_task_name

    @property
    def task_kwargs(self):
        """Cached Getter task_kwargs, currently keeping empty"""
        if hasattr(self, "_instruction") and self._instruction:
            return self._instruction.__dict__
        return None

    @property
    def task_args(self):
        """Cached Getter task_args, currently keeping empty"""
        return None

    def get_idempotency_key(self):
        """
        Cached Getter an idempotency to ensure uique task is queued.
        Assuming resolver exceute sync, this should not lead to deadlock/race condition,
        """
        return f"{self._instruction.channel_type}-{self._instruction.log_id}"

    def dispatch(self):
        """
        Dipatch the given instructions to a celery task.
        TODO: Handle failure's, retries and re-triggers.
        """
        try:
            queue_task(
                task=self._task_name,
                on_commit=True,
                task_args=self.task_args,
                task_kwargs=self.task_kwargs,
                idempotency_key=self.get_idempotency_key(),
            )
        except Exception as e:
            raise NotificationDispatcherException("Error in queing celery task") from e
