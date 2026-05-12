from django.http import JsonResponse
from django.shortcuts import redirect


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
