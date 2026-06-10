from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from model_utils.models import SoftDeletableModel, TimeStampedModel, UUIDModel

User = get_user_model()


class SoftDeleteManager(models.Manager):

    def get_queryset(self):
        return self._queryset_class(
            model=self.model, using=self._db, **({"hints": self._hints} if hasattr(self, "_hints") else {})
        ).filter(is_removed=False)


class SoftDeleteModelMixin(models.Model):

    deleted_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_removed = models.BooleanField(default=False, null=False)

    available_objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, soft: bool = True, deleted_by: User = None):
        if not soft:
            super().delete(using, keep_parents)

        update_fields = ["deleted_at", "is_removed"]
        self.deleted_at = datetime.now()
        self.is_removed = True

        if deleted_by and isinstance(deleted_by, User):
            self.deleted_by = deleted_by
            update_fields += ["deleted_by"]

        self.save(update_fields=update_fields)


class InvalidVersionException(Exception):
    """Raised when a version is invalid"""

    pass


class SimpleVersionModelMixin(models.Model):
    DEFAULT_ORDERING = ("-version_major", "-version_minor", "-version_patch")
    DEFAULT_VERSION = (1, 0, 0)

    version_major = models.IntegerField(default=DEFAULT_VERSION[0])
    version_minor = models.IntegerField(default=DEFAULT_VERSION[1])
    version_patch = models.IntegerField(default=DEFAULT_VERSION[2])
    version = models.CharField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.resolve_version()
        super().save(*args, **kwargs)

    def validate_version(self):
        if not self.version:
            return self.DEFAULT_VERSION

        try:
            major, minor, patch = map(int, self.version.split("."))
            return major, minor, patch
        except Exception as e:
            raise InvalidVersionException from e

    def resolve_version(self):
        if self.version:
            (
                self.version_major,
                self.version_minor,
                self.version_patch,
            ) = self.validate_version()
        else:
            self.version = f"{self.version_major}.{self.version_minor}.{self.version_patch}"


class SafeModelMixin(SoftDeletableModel, TimeStampedModel):
    """Combination of SoftDeletableModel, TimeStampedModel
    Fields:
        is_removed (bool): Deleting marks this as false
        created (AutoCreatedField): Date time when object is created
        modified (AutoLastModifiedField): Date time when object is modified
    """

    class Meta:
        abstract = True


class BetterModelMixin(UUIDModel, SafeModelMixin):
    """Combination of UUIDModel, SoftDeletableModel, TimeStampedModel
    Fields:
        id (UUID): prinary key
        is_removed (bool): Deleting marks this as false
        created (AutoCreatedField): Date time when object is created
        modified (AutoLastModifiedField): Date time when object is modified
    """

    class Meta:
        abstract = True


class VersionedSafeModelMixin(SafeModelMixin, SimpleVersionModelMixin):
    """Combination of SoftDeletableModel, TimeStampedModel, SimpleVersionModelMixin
    Fields:
        is_removed (bool): Deleting marks this as false
        created (AutoCreatedField): Date time when object is created
        modified (AutoLastModifiedField): Date time when object is modified
        version_major (int): version major
        version_minor (int): version minor
        version_patch (int): version patch
        version (str): Complete version string
    """

    class Meta:
        abstract = True


class VersionedBetterModelMixin(BetterModelMixin, SimpleVersionModelMixin):
    """Combination of UUIDModel, SoftDeletableModel, TimeStampedModel, SimpleVersionModelMixin
    Fields:
        id (UUID): prinary key
        is_removed (bool): Deleting marks this as false
        created (AutoCreatedField): Date time when object is created
        modified (AutoLastModifiedField): Date time when object is modified
        version_major (int): version major
        version_minor (int): version minor
        version_patch (int): version patch
        version (str): Complete version string
    """

    class Meta:
        abstract = True
