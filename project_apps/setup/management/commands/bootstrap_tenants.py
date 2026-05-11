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
                create_domain=True,
                domain_config=DomainConfig([], is_public=True)
            )       
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(str(e))
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Public Tenant Created Successfully...")
        )

        if private_schema := options["schema_name"]:
            self.stdout.write(
                self.style.SUCCESS(f"Creating Private Tenant: [{private_schema}]...")
            )
            try:
                create_domain, domain_config = (False, None)
                if domain := options["domain_name"]:
                    create_domain = True
                    domain_config = DomainConfig([domain], False)
                    
                TenantCreationUtils.create_tenant(
                    tenant_type=TenantTypes.PRIVATE.value, 
                    schema_name=private_schema,
                    create_domain=create_domain,
                    domain_config=domain_config
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating private schema: {str(e)}")
                )
            self.stdout.write(
                self.style.SUCCESS(f"Tenant Created Successfully...")
            )
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--schema_name",
            type=str,
            help="Create a private tenant with schema name along with public tenant"
        )
        parser.add_argument(
            "--domain_name",
            type=str,
            help="[Optional] Domain Name for the private tenant."
        )