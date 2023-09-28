import os

from typing import Optional
from diskcache import Cache
from .config import config
from . import logger

cache_directory = os.path.expanduser(config["global"]["cache_directory"])


def set(
    key: str,
    value,
    expire_in_seconds: Optional[int] = config["global"]["cache_expiry_in_seconds"],
):
    with Cache(cache_directory) as cache:
        cache.set(key, value, expire=expire_in_seconds)


def get(key: str):
    with Cache(cache_directory) as cache:
        value = cache.get(key)

    return value


def clear():
    with Cache(cache_directory) as cache:
        cache.clear()
