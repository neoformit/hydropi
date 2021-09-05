"""Interface for reading nutrient reservoir depth.

https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
"""

import time
import logging
import statistics
import RPi.GPIO as io

from config import config

logger = logging.getLogger(__name__)

SONIC_SPEED = 34300  # cm/sec


class DepthSensor:
    """Interface for digital depth sensor."""

    UNIT = 'mm'

    def __init__(self):
        """Initialise interface."""
        io.setmode(io.BCM)
        io.setup(config.PIN_DEPTH_TRIG, io.OUT)
        io.setup(config.PIN_DEPTH_ECHO, io.IN)
        io.output(config.PIN_DEPTH_TRIG, 0)
        time.sleep(1)

    def read(self, n=1):
        """Return current depth in mm."""
        if n > 1:
            return self.read_median(n)
        io.output(config.PIN_DEPTH_TRIG, 1)
        time.sleep(0.00001)
        io.output(config.PIN_DEPTH_TRIG, 0)

        start = time.time()
        stop = time.time()

        # Collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 0:
            start = time.time()

        # Collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 1:
            stop = time.time()

        return self.time_to_depth(stop - start)

    def read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.read())
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        r = statistics.median(readings)
        logger.debug(f"{type(self).__name__} READ: {r} {self.UNIT} (n={n})")
        return r

    def time_to_depth(seconds):
        """Convert pulse time to depth."""
        return config.TANK_HEIGHT_MM - (
            (seconds * SONIC_SPEED)  # time -> distance
            / 2                      # There and back
            / 10                     # cm -> mm
        )

    def full(self):
        """Check whether tank is full and return Boolean."""
        stat = self.read(n=5)
        if stat < 0.95 * config.DEPTH_MAXIMUM_MM:
            logger.debug("Tank depth below full")
            return False
        logger.debug("Tank depth full")
        return True

    def test(self):
        """Test the component interface."""
        while True:
            print(f"READING: {self.read()}{self.UNIT}")
            time.sleep(1)
