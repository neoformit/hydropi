"""Perform cyclical release of nutrient solution."""

try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

import time
import logging

from hydropi.config import config
from hydropi.notifications import telegram
from hydropi.process.check.time import is_quiet_time
from hydropi.interfaces.controllers.mist import MistController
from .pause import paused


logger = logging.getLogger('hydropi')


def mist():
    """Periodically release nutrient mist."""
    try:
        while True:
            if paused():
                logger.debug("Skip mist round while paused")
            else:
                MistController().mist()
            time.sleep(get_sleep_interval())
    except Exception as exc:
        telegram.notify(f"ERROR ENCOUNTERED IN DELIVERY:\n\n{exc}")
        raise exc
    finally:
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
        else:
            io.cleanup()


def get_sleep_interval():
    """Return seconds to sleep between events."""
    if is_quiet_time():
        cycle_minutes = config.MIST_CYCLE_NIGHT_MINUTES
    else:
        cycle_minutes = config.MIST_CYCLE_MINUTES
    return 60 * cycle_minutes - config.MIST_DURATION_SECONDS
