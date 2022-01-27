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
from .pressure import PressureSensor
from .analog import STATUS

logger = logging.getLogger('hydropi')

SONIC_SPEED = 34300  # cm/sec
H = 50.0      # Total height of nutrient bin (reservoir)
RT = 21.7     # Radius top
RB = 17.5     # Radius bottom


class DepthSensor:
    """Interface for digital depth sensor.

    A median sample with n=15 and delay=0.01 sec gives +/- 2mm reading.

    Works better with clear space between sensor and object i.e. no adjacent
    wall or other object.
    """

    TEXT = 'depth'
    UNIT = 'L'
    DECIMAL_POINTS = 1
    PIN_TRIG = config.PIN_DEPTH_TRIG
    PIN_ECHO = config.PIN_DEPTH_ECHO
    MEDIAN_INTERVAL_SECONDS = 0.05 or config.MEDIAN_INTERVAL_SECONDS
    DEFAULT_MEDIAN_SAMPLES = 5

    def __init__(self):
        """Initialise interface."""
        self.FLOOR_L = 0
        self.CEILING_L = depth_to_volume(config.DEPTH_MAX_MM)
        self.VOLUME_TARGET_L = config.VOLUME_TARGET_L
        self.VOLUME_TARGET_PC = config.VOLUME_TARGET_L / self.CEILING_L
        self.RANGE_LOWER_L = self.VOLUME_TARGET_L * (
            1 - config.VOLUME_TOLERANCE)
        self.RANGE_UPPER_L = self.VOLUME_TARGET_L * (
            1 + config.VOLUME_TOLERANCE)
        self.DANGER_LOWER_L = self.VOLUME_TARGET_L * (
            1 - config.VOLUME_TOLERANCE * 2)
        self.DANGER_UPPER_L = self.VOLUME_TARGET_L * (
            1 + config.VOLUME_TOLERANCE * 2)
        if config.DEVMODE:
            logger.warning("DEVMODE: configure sensor without ADC interface")
            return
        io.setmode(io.BCM)
        io.setup(self.PIN_TRIG, io.OUT)
        io.setup(self.PIN_ECHO, io.IN)
        io.output(self.PIN_TRIG, 0)
        time.sleep(1)

    def __del__(self):
        """Clean up IO hardware on termination."""
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
            return
        io.setmode(io.BCM)
        io.cleanup(self.PIN_TRIG)
        io.cleanup(self.PIN_ECHO)

    def read(self, n=None, include_pressure=True,
             depth=False, head=False, echo=False):
        """Return current volume in litres.

        include_pressure=True adds on the estimated volume stored in the
        pressure tank

        echo=True provides the echo time in ms

        head=True provides head height in mm (distance from sensor to surface)

        depth=True provides tank depth in mm
        """
        n = n or self.DEFAULT_MEDIAN_SAMPLES
        if n > 1:
            td = self._read_median(n)
        else:
            td = self._get_echo_time()

        if echo:
            return td
        if head:
            r = round(time_to_distance(td), None)
            logger.info(f"{type(self).__name__} READ: HEAD {r}mm (n={n})")
            return r
        if depth:
            r = round(time_to_depth(td), None)
            logger.info(f"{type(self).__name__} READ: DEPTH {r}mm (n={n})")
            return r
        vol = time_to_volume(td)
        logger.debug(
            f"{type(self).__name__} READ: tank volume excluding pressure"
            f" {round(vol, self.DECIMAL_POINTS)} litres")
        if include_pressure:
            ps = PressureSensor()
            vol += ps.get_tank_volume()
        r = round(vol, self.DECIMAL_POINTS)
        logger.info(f"{type(self).__name__} READ: {r}{self.UNIT} (n={n})")
        return r

    def _read_median(self, n):
        """Return median echo time from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.read(n=1, echo=True))
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        return statistics.median(readings)

    def _get_echo_time(self):
        """Collect a reading from the ultrasonic sensor."""
        if config.DEVMODE:
            logger.warning(
                "DEVMODE: spoof ultrasonic reading")
            mu = 6.5 * config.VOLUME_TARGET_L / SONIC_SPEED
            return random.normalvariate(
                mu,
                mu * config.VOLUME_TOLERANCE,
            )

        io.output(self.PIN_TRIG, 1)
        time.sleep(0.00001)
        io.output(self.PIN_TRIG, 0)
        # Collect end of echo pulse
        while io.input(self.PIN_ECHO) == 0:
            pulse_start = time.time()
        # Collect end of echo pulse
        while io.input(self.PIN_ECHO) == 1:
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
            current = depth.read()

        # Represent reading as a percent of total volume
        if current > depth.CEILING_L:
            percent = 1.0
        elif current < depth.FLOOR_L:
            percent = 0.0
        else:
            percent = round(
                (current - depth.FLOOR_L)
                / (depth.CEILING_L - depth.FLOOR_L),
                4
            )

        return {
            'text': cls.TEXT,
            'status': depth.get_status_text(current),
            'value': current,
            'percent': percent,
            'targetPercent': depth.VOLUME_TARGET_PC,
            'unit': cls.UNIT,
        }

    def full(self):
        """Check whether tank is full and return Boolean."""
        stat = self.read()
        # 95% full is good enough
        if stat < 0.95 * config.DEPTH_MAXIMUM_MM:
            logger.debug("Tank depth below full")
            return False
        logger.debug("Tank depth full")
        return True

    def test(self):
        """Test the component interface."""
        while True:
            logger.info(f"READING: {self.read()}{self.UNIT}")
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
    rd = RT - RB  # Radius difference

    return (
        (rd * d / H) / 2 + RB
    )**2 * math.pi * d / 1000
