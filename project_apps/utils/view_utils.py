from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.viewsets import ViewSet
from rest_framework import response, status


class AuthenticatedViewMixin:
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        session_valid = request.session.session_key and request.session.exists(request.session.session_key)

        user_valid = request.user.is_authenticated

        if not (session_valid and user_valid):
            if request.headers.get("accept") == "application/json" or request.content_type == "application/json":
                return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)
            return redirect(self.login_url)

        return super().dispatch(request, *args, **kwargs)


class ConnTestMixin(ViewSet):
    """Connection Test Utility"""

    def list(self, request, *args, **kwargs):
        return response.Response({"data": "Hey LIST"}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return response.Response({"data": "Hey GET"}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return response.Response({"data": "Hey POST"}, status=status.HTTP_200_OK)
