"""Operate solenoid valve to control nutrient release from pressure tank."""

import time
import logging

from hydropi.config import config
from .controller import AbstractController

logger = logging.getLogger('hydropi')


class MistController(AbstractController):
    """Control valve to deliver nutrient solution."""

    PIN = config.PIN_MIST_VALVE

    def mist(self):
        """Deliver a mist pulse."""
        logger.debug(
            f"ACTION: MIST {config.MIST_DURATION_SECONDS} SECONDS")
        self.on()
        time.sleep(config.MIST_DURATION_SECONDS)
        self.off()
