"""Random value generators."""

from random import randint
from datetime import datetime
from uuid import uuid4

# 85 char set
valid_string_characters = (
    "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ.1234567890"
    "-=+_.!@#$%^&*()[]{}/ "
)


def random_string(length):
    """Return a random string of given length."""

    s = ''
    while len(s) < length:
        s += valid_string_characters[randint(0, 84)]

    return s


def random_datetime(start_timestamp=315514800, end_timestamp=1539043927):
    """Generate a random datetime object from given range"""
    return datetime.fromtimestamp(randint(start_timestamp, end_timestamp))


def uuid():
    """Return new uuid4."""
    return str(uuid4())
