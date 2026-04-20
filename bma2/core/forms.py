from django import forms
from django.utils.translation import gettext_lazy as _  # noqa: F401

from bma.core.constants import CountryCodeChoices, SuffixChoices


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Enter Username"}),
        required=True,
        max_length=150,
        min_length=5,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Enter Password"}),
        required=True,
        max_length=150,
        min_length=8,
    )


class RegistrationForm(LoginForm):
    confirmed_password = forms.CharField(
        label="Confirm Password",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Confirm Password"}),
        required=False,
        max_length=150,
        min_length=8,
        show_hidden_initial=True,
    )
    suffix = forms.ChoiceField(
        label="Suffix",
        widget=forms.Select(attrs={"class": "ele"}),
        choices=SuffixChoices,
        required=False,
        initial=SuffixChoices.MR,
    )
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "First Name(John)"}),
        required=True,
        max_length=150,
    )
    middle_name = forms.CharField(
        label="Middle Name",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Middle Name(M.)"}),
        required=False,
        max_length=150,
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Last Name(Doe)"}),
        required=False,
        max_length=150,
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Email(test@mail.com)"}),
        required=True,
    )
    country_code = forms.ChoiceField(
        label="Country Code",
        widget=forms.Select(attrs={"class": "ele"}),
        initial=CountryCodeChoices.INDIA,
        choices=CountryCodeChoices,
        required=True,
    )
    phone_number = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "ele", "placeholder": "Phone(99999 99999)"}),
        required=True,
        max_length=20,
        min_length=10,
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("password") != cleaned.get("confirmed_password"):
            err_msg = "Confirmed Password not equal to actual password"
            self.add_error("confirmed_password", err_msg)
            raise forms.ValidationError(err_msg)
