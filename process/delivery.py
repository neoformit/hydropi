"""Perform cyclical release of nutrient solution."""

import time
import logging

from config import config
from interfaces.controllers.mist import MistController

logger = logging.getLogger(__name__)


def mist():
    """Periodically release nutrient mist."""
    mist = MistController()
    while True:
        logger.debug(f"ACTION: MIST {config.MIST_DURATION_SECONDS} SECONDS")
        mist.on()
        time.sleep(config.MIST_DURATION_SECONDS)
        mist.off()
        time.sleep(
            60 * config.MIST_CYCLE_MINUTES
            - config.MIST_DURATION_SECONDS
        )
