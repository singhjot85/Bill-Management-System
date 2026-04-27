from django.contrib.admin import AdminSite

class PublicAdminSite(AdminSite):
    # TODO: Make this configurable
    site_header = "Public Administration"
    site_title = "Public Admin"
    index_title = "Public Portal"

public_admin_site = PublicAdminSite(name="public_admin")

class TenantAdminSite(AdminSite):
    site_header = "Tenant Administration"
    site_title = "Tenant Admin"
    index_title = "Tenant Portal"

private_admin_site = TenantAdminSite(name="private_admin")