"""Perform cyclical release of nutrient solution."""

import time
import logging

from config import config
from interfaces.controllers.mist import MistController

logger = logging.getLogger(__name__)


def mist():
    """Periodically release nutrient mist."""
    while True:
        logger.debug(f"ACTION: MIST {config.MIST_DURATION_SECONDS} SECONDS")
        # Threaded MC seems to break if re-used between cycles
        mc = MistController()
        mc.on()
        time.sleep(config.MIST_DURATION_SECONDS)
        mc.off()
        time.sleep(
            60 * config.MIST_CYCLE_MINUTES
            - config.MIST_DURATION_SECONDS
        )
