"""Interface for reading nutrient reservoir depth.

https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
"""

import time
import math
import random
import logging
import statistics
from bmp280 import BMP280
from smbus2 import SMBus

try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

from hydropi.config import config
from hydropi.process.errors import catchme
from .pressure import PressureSensor
from .analog import STATUS

logger = logging.getLogger('hydropi')

H = 50.0                  # Total height of nutrient bin (reservoir)
RT = 21.7                 # Radius top
RB = 17.5                 # Radius bottom

# Pressure -> depth linear constants
HPA_TO_DEPTH_M = 10.0874
HPA_TO_DEPTH_C = -10122

I2C_PATH = '/dev/i2c-1'

if not config.DEVMODE and not os.path.exists(I2C_PATH):
    raise OSError(f'Path not found: {I2C_PATH}\n'
                  'You must enable I2C for the raspberry pi.')


class DepthSensor:
    """Interface for digital depth sensor.

    Digital (I2C) barometric sensor uses accurate pressure readings as a proxy
    for depth inside a sealed pipe, where pressure increases linearly with
    depth.

    Sample of n=5 is more than sufficient as readings are usually very
    consistent.
    """

    TEXT = 'depth'
    UNIT = 'L'
    DECIMAL_POINTS = 1
    PIN_SCL = config.PIN_DEPTH_SCL  # TODO: configure
    PIN_SDA = config.PIN_DEPTH_SDA
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
            logger.warning("DEVMODE: configure sensor without I2C interface")
            return
        # Initialise the BMP280
        self.bus = SMBus(1)
        self.bmp280 = BMP280(i2c_dev=bus)

    @catchme
    def read(self, n=None, pressure=False, include_pressure_tank=True,
             depth=False):
        """Return current volume in litres.

        include_pressure=True adds on the estimated volume stored in the
        pressure tank

        echo=True provides the echo time in ms

        head=True provides head height in mm (distance from sensor to surface)

        depth=True provides tank depth in mm
        """
        n = n or self.DEFAULT_MEDIAN_SAMPLES
        if n > 1:
            hpa = self._read_median(n)
        else:
            hpa = self._get_pressure_hpa()

        if pressure:
            return hpa
        elif depth:
            r = round(hpa_to_depth(hpa), None)
            logger.info(f"{type(self).__name__} READ: DEPTH {r}mm (n={n})")
        else:
            vol = hpa_to_volume(td)
            logger.debug(
                f"{type(self).__name__} READ: tank volume excluding pressure"
                f" {round(vol, self.DECIMAL_POINTS)} litres")
            if include_pressure_tank:
                ps = PressureSensor()
                vol += ps.get_tank_volume()
            r = round(vol, self.DECIMAL_POINTS)
            logger.info(f"{type(self).__name__} READ: {r}{self.UNIT} (n={n})")
        return max(r, 0)

    def _read_median(self, n):
        """Return median echo time from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.read(n=1, pressure=True))
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        return statistics.median(readings)

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


def hpa_to_depth(hpa):
    """Convert pressure (hPa) to depth in mm."""
    return round(hp * HPA_TO_DEPTH_M + HPA_TO_DEPTH_C)


def hpa_to_volume(hpa):
    """Estimate volume (L) for given pressure (hPa) in a 60L bin."""
    mm = hpa_to_depth(hpa)
    return depth_to_volume(mm)


def depth_to_volume(mm):
    """Estimate volume in litres for given depth in mm."""
    depth_cm = mm / 10
    rd = RT - RB  # Radius difference

    return (
        (rd * depth_cm / H) / 2 + RB
    )**2 * math.pi * depth_cm / 1000
