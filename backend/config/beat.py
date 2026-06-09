from django_celery_beat.schedulers import DatabaseScheduler


class CustomDatabaseScheduler(DatabaseScheduler):

    def apply_entry(self, entry, producer=None):
        """TODO: Override for tenant specific task execution logic."""
        return super().apply_entry(entry, producer)
