from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from project_apps.customer_management.models import Customer, CustomerAddress
from project_apps.utils.admin_utils import private_admin_site

User = get_user_model()


class CustomerAdmin(admin.ModelAdmin):
    pass


class CustomerAddressAdmin(admin.ModelAdmin):
    pass


private_admin_site.register(User, UserAdmin)
private_admin_site.register(Customer, CustomerAdmin)
private_admin_site.register(CustomerAddress, CustomerAddressAdmin)
