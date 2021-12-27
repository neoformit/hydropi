"""Check if quiet time."""

from datetime import datetime
from config import config


def is_quiet_time():
    """Check whether we are currently in quiet time."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    quiet_start = datetime.strptime(
        f'{today} {config.QUIET_TIME_START}', "%Y-%m-%d %H:%M")
    quiet_end = datetime.strptime(
        f'{today} {config.QUIET_TIME_END}', "%Y-%m-%d %H:%M")
    if now > quiet_start or now < quiet_end:
        return True
    return False
