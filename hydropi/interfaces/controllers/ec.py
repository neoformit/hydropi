"""Operate doser pump to deliver nutrients to the nutrient reservoir."""

import time
import logging
from threading import Thread

from hydropi.config import config

from .controller import AbstractController
from .mix import MixPumpController

logger = logging.getLogger(__name__)


class ECController(AbstractController):
    """Control nutrient delivery to increase EC."""

    PIN = config.PIN_NUTRIENT_PUMP

    def top_up(self):
        """Top up nutrient levels."""
        seconds = config.EC_ADDITION_SECONDS
        delay = config.MIX_ADDITION_DELAY_SECONDS
        logger.info(f"ACTION: top up nutrient levels {seconds} seconds")
        logger.info(f"DELAY: {delay} seconds")
        mixer = MixPumpController()
        Thread(target=mixer.mix).start()
        time.sleep(delay)
        self.on()
        time.sleep(seconds)
        self.off()
