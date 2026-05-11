import pytest
import os

def pytest_configure():
    os.environ["DJANGO_SECRETE_KEY"] = "test-secret-key"
    os.environ["RAZORPAY_API_KEY"] = "test_key"
    os.environ["RAZORPAY_API_SECRETE"] = "test_secret"
    
    from django.conf import settings
    
    # Overwrite DATABASES to use SQLite for tests
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }