from django.core.management import BaseCommand

from apps.setup.local_setup import run_local_setup


class Command(BaseCommand):
    help = "Run All Seeders for local setup"

    def add_arguments(self, parser):
        parser.add_argument("--seeder-name", type=str, help="Username of public user")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeder Run Started..."))
        try:
            seeder_name = options.get("seeder-name", None)
            run_local_setup(seeder_name)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Seeder Run Failed >>> {str(e)}"))
            raise e

        self.stdout.write(self.style.SUCCESS("Seeder Run Successfull"))
