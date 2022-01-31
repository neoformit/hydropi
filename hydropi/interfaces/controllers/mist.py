"""Operate solenoid valve to control nutrient release from pressure tank."""

import time
import logging

from hydropi.config import config
from hydropi.process.check.time import is_quiet_time
from .controller import AbstractController

logger = logging.getLogger('hydropi')


class MistController(AbstractController):
    """Control valve to deliver nutrient solution."""

    PIN = config.PIN_MIST_VALVE

    def mist(self):
        """Deliver a mist pulse."""
        seconds = (
            config.MIST_DURATION_NIGHT_SECONDS if is_quiet_time()
            else config.MIST_DURATION_SECONDS
        )
        logger.debug(f"ACTION: MIST {seconds} SECONDS")
        self.on()
        time.sleep(seconds)
        self.off()
