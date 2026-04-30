from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from project_apps.utils.admin_utils import public_admin_site

User = get_user_model()


public_admin_site.register(User, UserAdmin)
# TODO: Expose other default django models also.
