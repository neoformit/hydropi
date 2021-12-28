"""Check if quiet time."""

from datetime import datetime, timedelta
from config import config


def is_quiet_time(within_minutes=0):
    """Check whether we are currently in quiet time."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    quiet_start = datetime.strptime(
        f'{today} {config.QUIET_TIME_START}', "%Y-%m-%d %H:%M")
    quiet_end = datetime.strptime(
        f'{today} {config.QUIET_TIME_END}', "%Y-%m-%d %H:%M")

    if within_minutes:
        # Calculate whether quiet time is starting within n minutes
        quiet_start_within = quiet_start - timedelta(minutes=within_minutes)
        return now > quiet_start_within and now < quiet_start

    return now > quiet_start or now < quiet_end
