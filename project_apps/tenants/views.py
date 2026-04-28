import json
from http import HTTPStatus

from django.views import View
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate

LOGIN_TEMPLATE = "base_authenticated.html"
LOGIN_REDIRECT_URL = "/admin"


class LoginView(View):

    @staticmethod
    def return_render(request: HttpRequest, status: int, data: dict = None):
        """Return a redirect from server"""
        if not data:
            data = {}
        return render(request=request, template_name=LOGIN_TEMPLATE, context=data, status=status)

    @staticmethod
    def return_redirect():
        """Redirect to source after successfull login and alternate attempts"""
        return redirect(to=LOGIN_REDIRECT_URL, permanent=True, preserve_request=True)

    @staticmethod
    def _is_authenticated(request: HttpRequest):
        session_valid = request.session.session_key and request.session.exists(request.session.session_key)
        user_valid = request.user.is_authenticated
        return session_valid and user_valid

    def get(self, request: HttpRequest, *args, **kwargs):

        if self._is_authenticated(request):
            return LoginView.return_redirect()

        # 404 -> User Sesion not found ??
        # 200 -> So that UI doesn't show error's on Login Ping
        return LoginView.return_render(request, HTTPStatus.OK._value_)

    def post(self, request: HttpRequest, *args, **kwargs):
        data = {"errors": None}

        request_data = json.loads(request.body.decode())
        username = request_data.get("username")
        password = request_data.get("password")

        from django.db import connection
        print("Current DB connection >>> ", connection.schema_name)
        print("Request data >>> ", request_data)

        if user := authenticate(request, username=username, password=password):
            login(request, user)
            return LoginView.return_redirect()

        data["errors"] = "User Not found"
        data = json.dumps(data).encode()
        return HttpResponse(data, status=HTTPStatus.NOT_FOUND._value_) # 404 -> Not Found

    def _is_strong_password(self, password: str) -> bool:
        return (
            password.isalnum()  # Contains Alphabets and Numbers
            and password.lower() != password  # Contains Uppercase
            and password.upper() != password  # Contains Lowercase
        )

    def validate_password(self, password: str):
        """Reuse in Register, but don't use during login
        # try:
        #     password = self.validate_password(request_data.get("password"))
        # except AssertionError as e:
        #     data["errors"] = str(e)
        #     data = json.dumps(data).encode()
        #     # 406 -> Not acceptable
        #     return HttpResponse(data, status=HTTPStatus.NOT_ACCEPTABLE._value_)
        """
        _password = password.strip()

        assert _password.__len__() >= 8, "Password is too short, make it atleast 8 digits."

        assert self._is_strong_password(
            _password
        ), "Password is not so strong It must contain a LowerCase, an UpperCase and a Digit"

        return _password


class LogoutView(View):

    def get(self, request: HttpRequest, *args, **kwargs):
        logout(request)
        return redirect(to="", permanent=True, preserve_request=False)
