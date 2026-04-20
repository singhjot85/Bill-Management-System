from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django.shortcuts import redirect, render

from bma.core.constants import APIRequestMethods as Method
from bma.core.forms import LoginForm, RegistrationForm
from bma.core.models import BaseUserModel

AUTH_TEMPLATE = "auth.html"
ERROR_TEMPLATE = "error.html"
AUTH_REDIRECT = "/public/payments/"


def auth_view(request: HttpRequest, *args, **kwargs):
    err_msg = "Unknown error !!"

    if _is_authenticated(request):
        return redirect(to=AUTH_REDIRECT, permanent=True, preserve_request=True)

    req_method = request.method.upper()

    if req_method == Method.GET.value:
        form = LoginForm()
        mode = "login"

        if request.GET.get("mode", None) == "register":
            form = RegistrationForm()
            mode = "register"

        context = {"form": form, "mode": mode}
        return render(request, AUTH_TEMPLATE, context=context)

    if req_method == Method.POST.value:
        data = request.POST

        if data.get("mode") == "register":
            if RegistrationForm(data).is_valid():
                _create_user(data)
                return redirect(AUTH_REDIRECT)

            err_msg = "User Registration unsuccessful"

        if data.get("mode") == "login":
            username = data.get("username", None)
            password = data.get("password", None)

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(to=AUTH_REDIRECT, permanent=True, preserve_request=True)

            err_msg = "User not found"

    return render(request, ERROR_TEMPLATE, context={"message": err_msg})


def _is_authenticated(request: HttpRequest):
    session_valid = request.session.session_key and request.session.exists(request.session.session_key)
    user_valid = request.user.is_authenticated
    return session_valid and user_valid


def _create_user(data: dict):
    username = data.get("username")
    password = data.get("password")
    user: BaseUserModel = BaseUserModel.objects.create(username=username)
    user.set_password(password)

    NON_UPDATABLE_ATTRS = ["username", "password", "is_active", "is_superuser", ""]
    for attr, val in data.items():
        if attr in NON_UPDATABLE_ATTRS:
            continue
        if hasattr(user, str(attr)):
            setattr(user, attr, val)
    user.save()
