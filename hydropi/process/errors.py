"""Error handling for system services."""

import os
import logging
import traceback

from hydropi.config import config
from hydropi.notifications import telegram

logger = logging.getLogger('hydropi')


def catchme(func):
    """Handle and log all uncaught exceptions."""
    def wrapper(*args, **kwargs):
        """Wrap target function to catch errors."""
        try:
            return func(*args, **kwargs)
        except Exception:
            tb = traceback.format_exc()
            logger.error(tb)
            telegram.notify(tb)
    return wrapper


class ErrorWatcher:
    """Observe errors and raise them if they persist."""

    def __init__(self):
        """Initialize error watch."""
        self.error = False

    def catch(self, exc, message=None):
        """Catch or raise an exception."""
        tb = traceback.format_exc()
        msg = f"{message}:\n\n{tb}" if message else tb
        telegram.notify(msg)
        logger.error(msg)
        with open(os.path.join(config.TEMP_DIR, 'stderr'), 'w') as f:
            f.write(msg)
        if self.error:
            raise exc
        self.error = True

    def reset(self):
        """Reset watcher."""
        self.error = False
