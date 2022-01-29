"""Perform cyclical release of nutrient solution."""

import time
import logging
from RPi import GPIO as io

from hydropi.config import config
from hydropi.notifications import telegram
from hydropi.process.check.time import is_quiet_time
from hydropi.interfaces.controllers.mist import MistController

logger = logging.getLogger('hydropi')


def mist():
    """Periodically release nutrient mist."""
    try:
        while True:
            if is_quiet_time():
                cycle_minutes = config.MIST_CYCLE_NIGHT_MINUTES
            else:
                cycle_minutes = config.MIST_CYCLE_MINUTES
            logger.debug(
                f"ACTION: MIST {config.MIST_DURATION_SECONDS} SECONDS")
            mc = MistController()
            mc.on()
            time.sleep(config.MIST_DURATION_SECONDS)
            mc.off()
            time.sleep(
                60 * cycle_minutes
                - config.MIST_DURATION_SECONDS
            )
    except Exception as exc:
        telegram.notify(f"ERROR ENCOUNTERED IN DELIVERY:\n\n{exc}")
        raise exc
    finally:
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
        else:
            io.cleanup()
