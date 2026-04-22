from bma.core.views import auth_view
from django.urls import path

urlpatterns = [
    path(r"", auth_view, name="login"),
]
