from django.core.exceptions import ImproperlyConfigured

from .constants import (
    LOCAL_ENVS,
    REDIS_CLUSTER_DEFAULT_OPTIONS,
    REDIS_DEFAULT_BACKEND,
    REDIS_DEFAULT_OPTIONS,
    VALKEY_CLUSTER_DEFAULT_OPTIONS,
    VALKEY_DEFAULT_BACKEND,
    VALKEY_DEFAULT_OPTIONS,
)
from .variables import (
    BROKER_HOST,
    BROKER_PORT,
    BROKER_PROVIDER,
    CACHE_HOST,
    CACHE_PORT,
    CACHE_PROVIDER,
    CURRENT_ENV,
    DEFAULT_FROM_EMAIL,
    VALKEY_SOCKER_TIMEOUT,
    VALKEY_SOCKET_CONN_TIMEOUT,
)


def get_broker_url():
    if not any([BROKER_PROVIDER, BROKER_HOST, BROKER_PORT]):
        raise ImproperlyConfigured("Celery Broker url is incorrect")

    return f"{BROKER_PROVIDER}://{BROKER_HOST}:{BROKER_PORT}/0"


def get_cache_url():
    if not any([CACHE_PROVIDER, CACHE_HOST, CACHE_PORT]):
        raise ImproperlyConfigured("Cache url is incorrect")

    return f"{CACHE_PROVIDER}://{CACHE_HOST}:{CACHE_PORT}/0"


def get_resolved_cache_options():
    CACHE_BACKEND = None
    RESOLVED_CACHE_OPTIONS = None

    if CACHE_PROVIDER == "valkey":
        CACHE_BACKEND = VALKEY_DEFAULT_BACKEND
        RESOLVED_CACHE_OPTIONS = VALKEY_DEFAULT_OPTIONS

    elif CACHE_PROVIDER == "redis":
        # NOTE: The project doesn't support redis as of now, not really sure about valkey so this is future proofing
        CACHE_BACKEND = REDIS_DEFAULT_BACKEND
        RESOLVED_CACHE_OPTIONS = REDIS_DEFAULT_OPTIONS

    else:
        raise ImproperlyConfigured(f"Invalid Cache provider [{CACHE_PROVIDER}].")

    return CACHE_BACKEND, RESOLVED_CACHE_OPTIONS


# TODO: Do we need to implement clusters ??
def get_resolved_cache_options_cluster():
    CACHE_BACKEND = None
    RESOLVED_CACHE_OPTIONS = None

    if CACHE_PROVIDER == "valkey":
        CACHE_BACKEND = VALKEY_DEFAULT_BACKEND
        RESOLVED_CACHE_OPTIONS = VALKEY_CLUSTER_DEFAULT_OPTIONS
        if VALKEY_SOCKET_CONN_TIMEOUT:
            RESOLVED_CACHE_OPTIONS["CONNECTION_POOL_KWARGS"]["socket_connection_timeout"] = VALKEY_SOCKET_CONN_TIMEOUT
        if VALKEY_SOCKER_TIMEOUT:
            RESOLVED_CACHE_OPTIONS["CONNECTION_POOL_KWARGS"]["socket_timeout"] = VALKEY_SOCKER_TIMEOUT

    elif CACHE_PROVIDER == "redis":
        # NOTE: The project doesn't support redis as of now, not really sure about valkey so this is future proofing
        CACHE_BACKEND = REDIS_DEFAULT_BACKEND
        RESOLVED_CACHE_OPTIONS = REDIS_CLUSTER_DEFAULT_OPTIONS

    else:
        raise ImproperlyConfigured(f"Invalid Cache provider [{CACHE_PROVIDER}].")

    return CACHE_BACKEND, RESOLVED_CACHE_OPTIONS


def set_default_email_from():
    if CURRENT_ENV in LOCAL_ENVS:
        return "dev@mailig.com"

    return DEFAULT_FROM_EMAIL
