"""Error handling for system services."""

import logging

from hydropi.notifications import telegram

logger = logging.getLogger('hydropi')


def catchme(func):
    """Handle and log all uncaught exceptions."""
    def wrapper(*args, **kwargs):
        """Wrap target function to catch errors."""
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.error(exc)
            telegram.notify(exc)
    return wrapper
