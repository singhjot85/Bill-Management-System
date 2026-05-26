import os

def pytest_configure():
    os.environ["DJANGO_SECRETE_KEY"] = "test-secret-key"  # pragma: allowlist-secret
    os.environ["RAZORPAY_API_KEY"] = "test_key"  # pragma: allowlist-secret
    os.environ["RAZORPAY_API_SECRETE"] = "test_secret"  # pragma: allowlist-secret
