"""Interface for reading nutrient reservoir depth.

https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
"""

import time
import math
import random
import logging
import statistics
try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

from hydropi.config import config

logger = logging.getLogger(__name__)

SONIC_SPEED = 34300  # cm/sec


class DepthSensor:
    """Interface for digital depth sensor.

    A median sample with n=15 and delay=0.01 sec gives +/- 2mm reading.

    Works better with clear space between sensor and object i.e. no adjacent
    wall or other object.
    """

    TEXT = 'depth'
    UNIT = 'mm'

    def __init__(self):
        """Initialise interface."""
        if config.DEVMODE:
            logger.warning("DEVMODE: configure sensor without ADC interface")
            return
        io.setmode(io.BCM)
        io.setup(config.PIN_DEPTH_TRIG, io.OUT)
        io.setup(config.PIN_DEPTH_ECHO, io.IN)
        io.output(config.PIN_DEPTH_TRIG, 0)
        time.sleep(1)

    def __del__(self):
        """Clean up IO hardware on termination."""
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
            return
        io.setmode(io.BCM)
        io.cleanup(self.PIN)

    def read(self, n=1, depth=False, volume=False):
        """Return current depth in mm."""
        if n > 1:
            return self._read_median(n)
        if config.DEVMODE:
            logger.warning(
                "DEVMODE: configure depth without ultrasonic interface")
            td = random.uniform(
                0.0001,
                config.DEPTH_MAXIMUM_MM / 10 / SONIC_SPEED
            )
        else:
            td = self._get_echo_time()
        if volume:
            r = round(time_to_volume(td), 1)
            logger.info(f"DepthSensor READ: {r}L (n={n})")
            return r
        if depth:
            r = round(time_to_depth(td), None)
            logger.info(f"DepthSensor READ: {r}{self.UNIT} (n={n})")
            return r
        r = round(time_to_distance(td), None)
        logger.info(f"DepthSensor READ: {r}{self.UNIT} (n={n})")
        return r

    def _read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.read())
            time.sleep(config.MEDIAN_SAMPLE_DELAY_SECONDS)
        r = statistics.median(readings)
        logger.debug(f"{type(self).__name__} READ: {r}{self.UNIT} (n={n})")
        return r

    def _get_echo_time(self):
        """Collect a reading from the ultrasonic sensor."""
        io.output(config.PIN_DEPTH_TRIG, 1)
        time.sleep(0.00001)
        io.output(config.PIN_DEPTH_TRIG, 0)
        # Collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 0:
            pulse_start = time.time()
        # Collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 1:
            pulse_end = time.time()

        return pulse_end - pulse_start

    def get_status_text(self, value):
        """Return appropriate status text for given value."""
        return 'NA'

    def full(self):
        """Check whether tank is full and return Boolean."""
        stat = self.read(n=5)
        # 95% full is good enough
        if stat < 0.95 * config.DEPTH_MAXIMUM_MM:
            logger.debug("Tank depth below full")
            return False
        logger.debug("Tank depth full")
        return True

    def test(self):
        """Test the component interface."""
        while True:
            logger.info(f"READING: {self.read(n=15)}{self.UNIT}")
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


def time_to_volume(seconds):
    """Estimate volume (L) for given echo response in a 60L bin."""
    mm = time_to_depth(seconds)
    d = mm / 10   # Convert to cm
    H = 50.0      # Total height
    Rt = 21.7     # Radius top
    Rb = 17.5     # Radius bottom
    Rd = Rt - Rb  # Radius difference

    return (
        (Rd * d / H) / 2 + Rb
    )**2 * math.pi * d / 1000
