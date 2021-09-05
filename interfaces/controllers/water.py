"""Operate mains water valve to regulate tank depth."""

import time
import logging

from config import config
from .controller import AbstractController

from interfaces.sensors.depth import DepthSensor

logger = logging.getLogger(__name__)


class WaterController:
    """Control mains water valve."""

    ON = 0
    OFF = 1

    def __init__(self):
        """Initialize interface."""
        self.relay_1 = RelayController1()
        self.relay_2 = RelayController2()
        self.state = self.OFF

    def on(self):
        """Activate the device."""
        self.state = self.ON
        logger.debug(
            f"{type(self).__name__}: switch output state to {self.state}")
        self.relay_1.on()
        self.relay_2.on()

    def off(self):
        """Deactivate the device."""
        self.state = self.OFF
        logger.debug(
            f"{type(self).__name__}: switch output state to {self.state}")
        self.relay_1.off()
        self.relay_2.off()

    def refill(self):
        """Refill the nutrient tank with water."""
        depth = DepthSensor()
        max_additions = (
            config.WATER_FILL_MAX_SECONDS
            / config.WATER_FILL_INTERVAL_SECONDS
        )
        for i in range(max_additions):
            if depth.full():
                break
            logger.debug("ACTION: Water valve open")
            self.on()
            time.sleep(config.WATER_FILL_INTERVAL_SECONDS)
            logger.debug("ACTION: Water valve close")
            self.off()


class RelayController1(AbstractController):
    """Control first relay."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_WATER_VALVE_1)


class RelayController2(AbstractController):
    """Control second relay."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_WATER_VALVE_2)
