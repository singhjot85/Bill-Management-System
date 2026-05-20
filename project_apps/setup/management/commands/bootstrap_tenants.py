from django.core.management import BaseCommand

from project_apps.setup.local_setup import run_local_setup


class Command(BaseCommand):
    help = "Setup Base Tenants"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Tenant Bootstrap Started..."))
        try:
            run_local_setup()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Tenant Bootstrap Failed >>> {str(e)}"))
            raise e

        self.stdout.write(self.style.SUCCESS("Tenant Bootstrap Successfull."))
