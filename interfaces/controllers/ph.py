"""Operate doser pump to decrease the pH of the nutrient reservoir."""

import time
import logging
from threading import Thread

from config import config

from .controller import AbstractController
from .mix import MixPumpController

logger = logging.getLogger(__name__)


class PHController(AbstractController):
    """Control acid delivery to decrease the pH."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_PH_DOWN_PUMP)

    def down(self):
        """Reduce the pH with an acid addition."""
        seconds = config.PH_ADDITION_SECONDS
        delay = config.MIX_ADDITION_DELAY_SECONDS
        logger.info(f"ACTION: pH down addition {seconds} seconds")
        logger.info(f"DELAY: {delay} seconds")
        mixer = MixPumpController()
        Thread(target=mixer.run).start()
        time.sleep(delay)
        self.on()
        time.sleep(seconds)
        self.off()
