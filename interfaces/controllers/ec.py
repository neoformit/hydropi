"""Operate doser pump to deliver nutrients to the nutrient reservoir."""

import time
import logging
from threading import Thread

from config import config

from .controller import AbstractController
from .mix import MixController

logger = logging.getLogger(__name__)


class ECController(AbstractController):
    """Control nutrient delivery to increase EC."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_NUTRIENT_PUMP)

    def top_up(self):
        """Top up nutrient levels."""
        seconds = config.EC_ADDITION_SECONDS
        delay = config.MIX_ADDITION_DELAY_SECONDS
        logger.info(f"ACTION: top up nutrient levels {seconds} seconds")
        logger.info(f"DELAY: {delay} seconds")
        mixer = MixController()
        Thread(target=mixer.run).start()
        time.sleep(delay)
        self.on()
        time.sleep(seconds)
        self.off()
