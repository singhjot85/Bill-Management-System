from enum import Enum

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CountryCodeChoices(TextChoices):
    INDIA = "+91", _("India (+91)")
    USA_OR_CND = "+1", _("United States/Canada (+1)")
    UK = "+44", _("United Kingdom (+44)")
    AUSTRALIA = "+61", _("Australia (+61)")
    GERMANY = "+49", _("Germany (+49)")
    FRANCE = "+33", _("France (+33)")
    ITALY = "+39", _("Italy (+39)")
    JAPAN = "+81", _("Japan (+81)")
    CHINA = "+86", _("China (+86)")
    SINGAPORE = "+65", _("Singapore (+65)")
    UAE = "+971", _("United Arab Emirates (+971)")
    SOUTH_AFRICA = "+27", _("South Africa (+27)")
    BRAZIL = "+55", _("Brazil (+55)")
    MEXICO = "+52", _("Mexico (+52)")


class SuffixChoices(TextChoices):
    MR = "Mr.", _("Mister Mr.")
    MRS = "Mrs.", _("Missus Mrs.")
    MISS = "Miss", _("Miss Miss")
    MS = "Ms.", _("Ms")
    DR = "Dr.", _("Doctor Dr.")
    PROF = "Prof.", _("Professor Prof.")
    SIR = "Sir", _("Sir")
    MADAM = "Madam", _("Madam")
    SR = "Sr.", _("Sardar Sr.")


class APIRequestMethods(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
