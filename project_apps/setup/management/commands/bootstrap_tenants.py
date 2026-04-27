from django.core.management import BaseCommand

from project_apps.utils.constants import TenantTypes
from project_apps.utils.tenant_utils import TenantCreationUtils, DomainConfig

class Command(BaseCommand):
    help = "Setup Base Tenants"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Tenant Bootstrap Started...")
        )

        self.stdout.write(
            self.style.SUCCESS("Creating Public Tenant...")
        )
        try:
            public_tenant, _ = TenantCreationUtils.create_tenant(
                tenant_type=TenantTypes.PUBLIC.value,
                schema_name="",
                domain_config=DomainConfig([], is_public=True)
            )       
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(str(e))
            )
            return 
        self.stdout.write(
            self.style.SUCCESS(f"[{public_tenant}] Tenant Created Successfully...")
        )

        if private_schema := options["schema_name"]:
            self.stdout.write(
                self.style.SUCCESS(f"Creating Private Tenant: [{private_schema}]...")
            )
            try:
                private_tenant, _ = TenantCreationUtils.create_tenant(
                    tenant_type=TenantTypes.PRIVATE.value, 
                    schema_name=private_schema,
                    create_domain=False
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(str(e))
                )
            self.stdout.write(
                self.style.SUCCESS(f"[{str(private_tenant)}]Tenant Created Successfully...")
            )
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--schema_name",
            type=str,
            help="Create a custom tenant with schema name"
        )