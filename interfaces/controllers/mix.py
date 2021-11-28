"""Operate solenoid valve to control nutrient flow from pressure tank."""

import time
import logging

from config import config
from .controller import AbstractController

logger = logging.getLogger(__name__)


class MixPumpController(AbstractController):
    """Control pump to mix nutrient solution."""

    PIN = config.PIN_MIX_PUMP

    def run(self):
        """Run pump to mix nutrient tank additions."""
        logger.debug(f"ACTION: Mix tank for {config.MIX_PUMP_SECONDS} seconds")
        self.on()
        time.sleep(config.MIX_PUMP_SECONDS)
        self.off()
