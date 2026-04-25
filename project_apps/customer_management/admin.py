from django.contrib import admin

from project_apps.customer_management.models import Customer

admin.site.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email"]