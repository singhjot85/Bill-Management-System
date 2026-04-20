from django.urls import path

from bma.core.views import auth_view

urlpatterns = [
    path(r"", auth_view, name="login"),
]
