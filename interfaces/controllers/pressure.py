"""Operate pressure pump to regulate tank pressure."""

import time
import logging

from config import config
from interfaces.sensors.pressure import PressureSensor

from .controller import AbstractController

logger = logging.getLogger(__name__)


class PressurePumpController(AbstractController):
    """Control pressure pump."""

    PIN = config.PIN_PRESSURE_PUMP

    def refill(self):
        """Activate pump to restore system pressure."""
        sensor = PressureSensor()
        logger.debug(
            f"ACTION: restore system pressure to {config.MAX_PRESSURE_PSI}")
        self.on()
        while sensor.read() < config.MAX_PRESSURE_PSI:
            time.sleep(1)
        self.off()
        logger.info(
            f"System pressure restored to {sensor.read()} {sensor.UNIT}")
