from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from project_apps.utils.admin_utils import public_admin_site

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()

# router.register('auth', AuthViewSet, 'auth')

api_urlpatterns = [
    path("admin/", public_admin_site.urls, name="admin"),
    path("auth/", include("dj_rest_auth.urls")),
]

api_urlpatterns.extend(router.urls)

urlpatterns = [
    path("api/", include(api_urlpatterns)),
]
