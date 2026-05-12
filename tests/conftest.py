import os

from django.conf import settings


def pytest_configure():
    os.environ["DJANGO_SECRETE_KEY"] = "test-secret-key"  # pragma: allowlist-secret
    os.environ["RAZORPAY_API_KEY"] = "test_key"  # pragma: allowlist-secret
    os.environ["RAZORPAY_API_SECRETE"] = "test_secret"  # pragma: allowlist-secret

    # Overwrite DATABASES to use SQLite for tests
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
