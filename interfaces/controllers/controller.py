"""Abstract controller for single pin output signals."""

import time
import logging
import RPi.GPIO as io

logger = logging.getLogger(__name__)


class AbstractController:
    """Control a single pin output device."""

    ON = 0
    OFF = 1

    def __init__(self, pin):
        """Initialize interface."""
        self.PIN = pin
        self.state = self.OFF
        io.setmode(io.BCM)
        io.setup(self.PIN, io.OUT)
        io.output(self.PIN, self.state)

    def on(self):
        """Activate the device."""
        self.state = self.ON
        logger.debug(
            f"{type(self).__name__}: switch output state to {self.state}")
        io.output(self.PIN, self.state)

    def off(self):
        """Deactivate the device."""
        self.state = self.OFF
        logger.debug(
            f"{type(self).__name__}: switch output state to {self.state}")
        io.output(self.PIN, self.state)

    def test(self):
        """Test the controller."""
        logger.info(f"Testing {type(self).__name__} controller...")
        logger.info("~~~~~~ Press CTRL+C to end test ~~~~~~")
        time.sleep(1)
        while True:
            logger.info("SWITCH ON")
            self.on()
            time.sleep(3)
            logger.info("SWITCH OFF")
            self.off()
            time.sleep(3)
