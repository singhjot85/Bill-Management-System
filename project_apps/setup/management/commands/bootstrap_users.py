from django.conf import settings
from django.core.management import BaseCommand

from project_apps.utils.user_utils import UserCreationUtils

class Command(BaseCommand):
    help = "Setup initial users"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("User Bootstrap Started...")
        )

        if not self._is_development_mode():
            self.stdout.write(
                self.style.SUCCESS("Creating Production Users...")
            )
            self._public_creation(options)
            return
            
        self._bootstrapping()
        return
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--user_name",
            type=str,
            help="Username of user"
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password of user"
        )

    def _public_creation(self, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS("Creating public user...")
            )
            UserCreationUtils.public_user_creation(
                options.get("user_name"),
                options.get("password")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Public user creation failed: {str(e)}")
            )
        self.stdout.write(
            self.style.SUCCESS("Public User Created Successfully")
        )
    
    def _bootstrapping(self):
        try:
            UserCreationUtils.bootstrap_users()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error in user bootstrap: {str(e)}")
            )
        
        self.stdout.write(
            self.style.SUCCESS("User Bootstrap Completed Successfully")
        )

    def _is_development_mode(self):
        return bool(
            settings.DEBUG
            and settings.CURRENT_ENV in settings.LOCAL_ENVS
        )