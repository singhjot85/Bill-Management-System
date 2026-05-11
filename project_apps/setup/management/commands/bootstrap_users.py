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
            "--username",
            type=str,
            help="Username of public user"
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password of public user"
        )
        parser.add_argument(
            "--super",
            type=bool,
            help="Is the user a superuser"
        )

    def _public_creation(self, **options):
        try:
            self.stdout.write(
                self.style.SUCCESS("Creating public user...")
            )
            UserCreationUtils.user_creation(
                UserCreationUtils.public_tenant_creds(
                    username=options.get("username"),
                    password=options.get("password"),
                    create_super=options.get("super")
                )
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
            UserCreationUtils.bootstrap_users(
                private_creds=UserCreationUtils.private_tenant_creds(),
                public_creds=UserCreationUtils.public_tenant_creds()
            )
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