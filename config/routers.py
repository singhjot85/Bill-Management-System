from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from project_apps.customer_management.views import WorkflowViewSet
from project_apps.utils.admin_utils import private_admin_site

app_name = "api"
urlpatterns = [
    path("admin/", private_admin_site.urls, name="admin"),
    path('auth/', include('dj_rest_auth.urls')),
]

router = SimpleRouter()
if settings.DEBUG:
    router = DefaultRouter()


router.register("workflow", WorkflowViewSet, "workflow")

urlpatterns.extend(router.urls)
