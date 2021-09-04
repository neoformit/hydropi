"""Operate solenoid valve to control nutrient flow from pressure tank."""

import time
import logging

from config import config
from .controller import AbstractController

logger = logging.getLogger(__name__)


class MixController(AbstractController):
    """Control pump to mix nutrient solution."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_MIX_PUMP)

    def run(self):
        """Run pump to mix nutrient tank additions."""
        logger.debug(f"ACTION: Mix tank for {config.MIX_PUMP_SECONDS} seconds")
        self.on()
        time.sleep(config.MIX_PUMP_SECONDS)
        self.off()
