from django.contrib.admin import AdminSite
from django.shortcuts import redirect


class PublicAdminSite(AdminSite):
    # TODO: Make this configurable
    site_header = "Public Administration"
    site_title = "Public Admin"
    index_title = "Public Portal"

    def login(self, request, extra_context=...):
        """
        If user is alredy logged in redirect to admin
        Else redirect to custom login endpoint
        """

        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin:index")

        return redirect("/", preserve_request=False)


public_admin_site = PublicAdminSite(name="public_admin")


class TenantAdminSite(AdminSite):
    site_header = "Tenant Administration"
    site_title = "Tenant Admin"
    index_title = "Tenant Portal"

    def login(self, request, extra_context=...):
        """
        If user is alredy logged in redirect to admin
        Else redirect to custom login endpoint
        """

        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin:index")

        return redirect("/", preserve_request=False)


private_admin_site = TenantAdminSite(name="private_admin")
