"""Perform cyclical release of nutrient solution."""

import time
import logging

from config import config
from process.check.time import is_quiet_time
from interfaces.controllers.mist import MistController

logger = logging.getLogger(__name__)


def mist():
    """Periodically release nutrient mist."""
    while True:
        if is_quiet_time():
            cycle_minutes = config.MIST_CYCLE_NIGHT_MINUTES
        else:
            cycle_minutes = config.MIST_CYCLE_MINUTES
        logger.debug(f"ACTION: MIST {config.MIST_DURATION_SECONDS} SECONDS")
        mc = MistController()
        mc.on()
        time.sleep(config.MIST_DURATION_SECONDS)
        mc.off()
        time.sleep(
            60 * cycle_minutes
            - config.MIST_DURATION_SECONDS
        )
