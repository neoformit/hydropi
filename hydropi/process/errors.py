"""Error handling for system services."""

import os
import logging
import traceback
import time
import types

from hydropi.config import config
from hydropi.notifications import telegram

logger = logging.getLogger('hydropi')
RETRY_INTERVAL_SECONDS = 1


def catchme(*args, **kwargs):
    """Handle and log all uncaught exceptions."""

    retry = kwargs.get('retry')
    notify = kwargs.get('notify', True)

    def decorator(func):
        """The decorator function to be called."""
        def wrapper(*args, **kwargs):
            """Wrap target function to catch errors."""
            try:
                if retry:
                    return retry_call(func, retry, args, kwargs)
                return func(*args, **kwargs)
            except Exception:
                tb = traceback.format_exc()
                logger.error(tb)
                if notify:
                    telegram.notify(tb)
        return wrapper

    if args and type(args[0]) == types.FunctionType:
        # Decorator was declared without arguments
        return decorator(args[0])
    # Decorator called with arguments i.e. @catchme(retries=n)
    return decorator


def retry_call(func, n, args, kwargs):
    """Retry function n times after error."""
    count = 0
    while n - count:
        count += 1
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.warning(
                f"Call to {func.__name__} failed (attempt {count}/{n})."
                f" Exception: {exc}")
            time.sleep(RETRY_INTERVAL_SECONDS)

    return func(*args, **kwargs)


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
