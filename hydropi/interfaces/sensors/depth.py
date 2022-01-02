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
from .analog import STATUS

logger = logging.getLogger(__name__)

SONIC_SPEED = 34300  # cm/sec


class DepthSensor:
    """Interface for digital depth sensor.

    A median sample with n=15 and delay=0.01 sec gives +/- 2mm reading.

    Works better with clear space between sensor and object i.e. no adjacent
    wall or other object.
    """

    TEXT = 'depth'
    UNIT = 'L'
    DECIMAL_POINTS = 1

    def __init__(self):
        """Initialise interface."""
        if config.DEVMODE:
            logger.warning("DEVMODE: configure sensor without ADC interface")
            return

        self.FLOOR = 0
        self.CEILING = depth_to_volume(config.DEPTH_MAX_MM)
        self.DEPTH_TARGET_MM = config.DEPTH_TARGET_PC * config.DEPTH_MAX_MM
        self.DEPTH_TARGET_L = depth_to_volume(self.DEPTH_TARGET_MM)
        self.RANGE_LOWER_L = self.DEPTH_TARGET_L * (
            1 - config.DEPTH_TOLERANCE)
        self.RANGE_UPPER_L = self.DEPTH_TARGET_L * (
            1 + config.DEPTH_TOLERANCE)
        self.DANGER_LOWER_L = self.DEPTH_TARGET_L * (
            1 - config.DEPTH_TOLERANCE * 2)
        self.DANGER_UPPER_L = self.DEPTH_TARGET_L * (
            1 + config.DEPTH_TOLERANCE * 2)
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

    def read(self, n=1, depth=False, head=False):
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
        if head:
            r = round(time_to_distance(td), None)
            logger.info(f"DepthSensor READ: HEAD {r}mm (n={n})")
            return r
        if depth:
            r = round(time_to_depth(td), None)
            logger.info(f"DepthSensor READ: DEPTH {r}mm (n={n})")
            return r
        r = round(time_to_volume(td), 1)
        logger.info(f"DepthSensor READ: {r}{self.UNIT} (n={n})")
        return r

    def _read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.read())
            time.sleep(config.MEDIAN_INTERVAL_SECONDS)
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
        if (value > self.RANGE_LOWER_L
                and value < self.RANGE_UPPER_L):
            return STATUS.NORMAL
        elif (value > self.DANGER_LOWER_L
                and value < self.DANGER_UPPER_L):
            return STATUS.WARNING
        return STATUS.DANGER

    @classmethod
    def get_status(cls):
        """Create interface and return current status data."""
        depth = cls()
        if config.DEVMODE:
            logger.warning("DEVMODE: Return random reading")
            current = round(
                random.uniform(depth.DANGER_LOWER_L, depth.DANGER_UPPER_L),
                depth.DECIMAL_POINTS)
        else:
            current = depth.read(n=5)

        # Represent reading as a percent of absolute limits such that 0.5 is in
        # the middle of the optimal range (for display on dials).
        if current > depth.CEILING:
            percent = 1
        elif current < depth.FLOOR:
            percent = 0
        else:
            percent = round(
                (current - depth.FLOOR) / (depth.CEILING - depth.FLOOR), 4)

        return {
            'text': cls.TEXT,
            'status': depth.get_status_text(current),
            'value': current,
            'percent': percent,
            'unit': cls.UNIT,
        }

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
    return depth_to_volume(mm)


def depth_to_volume(mm):
    """Estimate volume in litres for given depth in mm."""
    d = mm / 10   # Convert to cm
    H = 50.0      # Total height
    Rt = 21.7     # Radius top
    Rb = 17.5     # Radius bottom
    Rd = Rt - Rb  # Radius difference

    return (
        (Rd * d / H) / 2 + Rb
    )**2 * math.pi * d / 1000
