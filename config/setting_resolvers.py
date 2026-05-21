from .constants import (
    VALKEY_DEFAULT_BACKEND,
    VALKEY_DEFAULT_OPTIONS,
    REDIS_DEFAULT_BACKEND,
    REDIS_DEFAULT_OPTIONS,
    VALKEY_CLUSTER_DEFAULT_OPTIONS,
    REDIS_CLUSTER_DEFAULT_OPTIONS,
)
from .variables import CACHE_PROVIDER, VALKEY_SOCKET_CONN_TIMEOUT, VALKEY_SOCKER_TIMEOUT, CACHE_HOST, CACHE_PORT

from django.core.exceptions import ImproperlyConfigured


def get_cache_url():
    if not any([CACHE_PROVIDER, CACHE_HOST, CACHE_PORT]):
        return None

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
