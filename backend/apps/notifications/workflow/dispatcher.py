class NotificationDispatcherException(Exception):
    pass


class NotificationDispatcher:
    """Dispatcher consumes some instuctions and create a celery task for those given instructions.
    Its responsibilty is to handle and manage task queuing.
    It also logs the event to datbase, by creating a log entry.
    """

    def dispatch(self):
        pass
