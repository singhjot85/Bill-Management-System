from django.shortcuts import redirect


class AuthenticatedViewMixin:
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        session_valid = (
            request.session.session_key
            and request.session.exists(request.session.session_key)
        )

        user_valid = request.user.is_authenticated

        if not (session_valid and user_valid):
            return redirect(self.login_url)

        return super().dispatch(request, *args, **kwargs)