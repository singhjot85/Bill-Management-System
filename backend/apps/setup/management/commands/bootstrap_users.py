from django.core.management import BaseCommand

from apps.setup.local_setup import bootstrap_users


class Command(BaseCommand):
    help = "Setup Base Users"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("User Bootstrap Started..."))
        try:
            bootstrap_users()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"User Bootstrap Failed >>> {str(e)}"))
            raise e

        self.stdout.write(self.style.SUCCESS("User Bootstrap Successfull."))
