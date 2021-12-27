"""Interface for reading nutrient reservoir depth.

https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
"""

import time
import logging
import statistics
try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

from config import config

logger = logging.getLogger(__name__)

SONIC_SPEED = 34300  # cm/sec


class DepthSensor:
    """Interface for digital depth sensor.

    A median sample with n=15 and delay=0.01 sec gives +/- 2mm reading.

    Works better with clear space between sensor and object i.e. no adjacent
    wall or other object.
    """

    UNIT = 'mm'

    def __init__(self):
        """Initialise interface."""
        io.setmode(io.BCM)
        io.setup(config.PIN_DEPTH_TRIG, io.OUT)
        io.setup(config.PIN_DEPTH_ECHO, io.IN)
        io.output(config.PIN_DEPTH_TRIG, 0)
        time.sleep(1)

    def read(self, n=1, depth=False):
        """Return current depth in mm."""
        if n > 1:
            return self.read_median(n)
        io.output(config.PIN_DEPTH_TRIG, 1)
        time.sleep(0.00001)
        io.output(config.PIN_DEPTH_TRIG, 0)

        # Collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 0:
            pulse_start = time.time()

        # Collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 1:
            pulse_end = time.time()

        td = pulse_end - pulse_start

        if depth:
            return time_to_depth(td)
        return time_to_distance(td)

    def read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.read())
            time.sleep(config.MEDIAN_SAMPLE_DELAY_SECONDS)
        r = statistics.median(readings)
        logger.debug(f"{type(self).__name__} READ: {r} {self.UNIT} (n={n})")
        return r

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
            logger.info(f"READING: {self.read_median(n=15)}{self.UNIT}")
            time.sleep(1)


def time_to_depth(seconds):
    """Convert pulse time to depth."""
    return round(config.TANK_HEIGHT_MM - (
        (seconds * SONIC_SPEED)  # time -> distance
        / 2                      # There and back
        * 10                     # cm -> mm
    ))


def time_to_distance(seconds):
    """Convert pulse time to distance."""
    return round(
        (seconds * SONIC_SPEED)  # time -> distance
        / 2                      # There and back
        * 10                     # cm -> mm
    )
