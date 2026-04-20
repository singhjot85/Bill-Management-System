from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import SoftDeletableModel, TimeStampedModel, UUIDModel

from bma.core.constants import CountryCodeChoices, SuffixChoices


class BaseModel(UUIDModel, TimeStampedModel, SoftDeletableModel):
    class Meta:
        abstract = True


class BaseUserModel(AbstractBaseUser, BaseModel, PermissionsMixin):

    username_validator = ASCIIUsernameValidator()
    # phonenumber_validator = PhoneNumberValidator()

    username = models.CharField(
        verbose_name="Username",
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    suffix = models.CharField(_("Suffix"), max_length=10, choices=SuffixChoices, blank=True)
    first_name = models.CharField(_("First Name"), max_length=150, blank=True)
    middle_name = models.CharField(_("Middle Name"), max_length=150, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=150, blank=True)

    email = models.EmailField(_("email address"), blank=True)
    country_code = models.CharField(
        verbose_name="Contact Country Code",
        default=CountryCodeChoices.INDIA,
        choices=CountryCodeChoices,
    )
    phonenumber = models.CharField(verbose_name="Contact Number", null=False, blank=False)

    is_staff = models.BooleanField(
        _("Staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name"]

    class Meta:
        verbose_name = _("BMA User")
        verbose_name_plural = _("BMA Users")

    def clean(self):
        super().clean()
        self.phonenumber = self.phonenumber.replace("-", "").replace(" ", "").strip()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "{} {} {} {}".format(
            self.suffix,
            self.first_name,
            self.middle_name,
            self.last_name,
        )
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        full_name = "{} {}".format(self.first_name, self.last_name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Customer(BaseModel):
    # TODO: Improve this model over time
    name = models.CharField(verbose_name="Name", max_length=150, null=False, blank=False)
    email = models.EmailField(verbose_name="Email")
    country_code = models.CharField(
        verbose_name="Contact Country Code",
        default=CountryCodeChoices.INDIA,
        choices=CountryCodeChoices,
    )
    phone_number = models.CharField(verbose_name="Contact Number", null=False, blank=False)

    def save(self, *args, **kwargs):
        self.email = self.email.strip()
        self.phone_number = self.phone_number.replace(" ", "").replace("-", "").strip()
        self.name = " ".join(self.name.split()).strip()
        super().save(*args, **kwargs)
