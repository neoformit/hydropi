"""Operate mains water valve to regulate tank depth."""

import time
import logging

from hydropi.config import config
from .controller import AbstractController

from hydropi.interfaces.sensors.depth import DepthSensor

logger = logging.getLogger(__name__)


class WaterController(AbstractController):
    """Control mains water additions.

    As a safeguard, water addition valve should be set up with a float switch
    and a push-to-break switch on the valve circuit.
    """

    PIN = config.PIN_WATER_VALVE

    def refill(self):
        """Refill the nutrient tank with water."""
        depth = DepthSensor()
        max_additions = (
            config.WATER_MAX_ADDITION_SECONDS
            / config.WATER_ADDITION_SECONDS
        )
        for i in range(max_additions):
            if depth.full():
                break
            logger.debug("ACTION: Water valve open")
            self.on()
            time.sleep(config.WATER_FILL_INTERVAL_SECONDS)
            logger.debug("ACTION: Water valve close")
            self.off()
