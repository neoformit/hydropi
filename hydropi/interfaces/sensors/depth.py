"""Interface for reading nutrient reservoir depth.

TODO: need to account for pressure changes in the pipe resulting from
temperature flux... could be interesting :(
When it cools down it will create negative pressure and suck up some water,
making it seem shallower than it is. The hottest temperature will then give the
"true" depth reading and everything else will be relative to that.
  - 8% expansion from 10 -> 35C = 4.8L

"""

import os
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

from hydropi.config import config, STATUS
from hydropi.process.errors import catchme
from hydropi.interfaces.utils import WeatherAPI
from .pressure import PressureSensor

logger = logging.getLogger('hydropi')

H = 50.0                  # Total height of nutrient bin (reservoir)
RT = 21.7                 # Radius top
RB = 17.5                 # Radius bottom

# Pressure -> depth linear constants
HPA_TO_DEPTH_M = 10.0874
HPA_TO_DEPTH_C = 0

# Pressure -> depth temperature compensation
DEPTH_ADJUST_PER_C = 1.0
DEPTH_ADJUST_FROM_C = 10

I2C_PATH = '/dev/i2c-1'

if not config.DEVMODE and not os.path.exists(I2C_PATH):
    raise OSError(f'Path not found: {I2C_PATH}\n'
                  'Barometric depth sensor requires I2C to be enabled on the'
                  ' raspberry pi (run `sudo raspi-config` and reboot).')


class DepthSensor:
    """Interface for digital depth sensor.

    Digital (I2C) barometric sensor uses accurate pressure readings as a proxy
    for depth inside a sealed pipe, where pressure increases linearly with
    depth.

    This sensor also provides an accurate temperature reading which can be used
    to calibrate the depth reading, since internal pressure also varies with
    temperature.

    Sample of n=5 is more than sufficient as readings are usually very
    consistent.
    """

    TEXT = 'depth'
    UNIT = 'L'
    DECIMAL_POINTS = 1
    PIN_SCL = config.PIN_DEPTH_SCL  # TODO: config.yml
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
        self.bmp280 = BMP280(i2c_dev=self.bus)

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
            abs_hpa = self._read_median(n)
        else:
            abs_hpa = self._get_pressure_hpa()

        ambient_hpa = WeatherAPI().get_ambient_pressure_hpa()
        if not ambient_hpa:
            logger.warning('No data returned from WeatherAPI')
            return
        logger.info(f"WeatherAPI current: {ambient_hpa} hPa")
        hpa = abs_hpa - ambient_hpa

        logger.debug(f"Read depth relative pressure: {hpa:.2f} hPa")

        if pressure:
            return hpa

        temp_c = self._get_temperature_c()
        logger.info(f"Tank temperature: {temp_c:.1f}C")

        if depth:
            r = round(hpa_to_depth(hpa, temp_c), None)
            logger.info(f"{type(self).__name__} READ: DEPTH {r}mm (n={n})")
        else:
            vol = hpa_to_volume(hpa, temp_c)
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
            r = self.read(n=1, pressure=True)
            if r is not None:
                readings.append(r)
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)

        return statistics.median(readings)

    def _get_pressure_hpa(self):
        """Read pressure from BMP280 and convert to relative pressure."""
        return self.bmp280.get_pressure()

    def _get_temperature_c(self):
        """Read temperature from BMP280 sensor."""
        return self.bmp280.get_temperature()

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


def hpa_to_depth(hpa, temp_c):
    """Convert pressure (hPa) to depth in mm."""

    # TODO: apply temperature correction

    depth_raw = round(hpa * HPA_TO_DEPTH_M + HPA_TO_DEPTH_C)
    logger.debug(f"Raw depth from barometric pressure: {depth_raw:.2f}mm")
    depth_adjusted = get_temp_adjusted_depth(depth_raw, temp_c)
    logger.debug(f"Raw depth from barometric pressure: {depth_raw:.2f}mm")

    return depth_adjusted


def get_temp_adjusted_depth(depth, temp_c):
    """Adjust depth estimate based on temperature."""
    delta = temp_c - DEPTH_ADJUST_FROM_C
    factor = 1  # delta * DEPTH_ADJUST_PER_C
    return depth * factor


def hpa_to_volume(hpa, temp_c):
    """Estimate volume (L) for given pressure (hPa) in a 60L bin."""
    mm = hpa_to_depth(hpa, temp_c)
    return depth_to_volume(mm)


def depth_to_volume(mm):
    """Estimate volume in litres for given depth in mm."""
    depth_cm = mm / 10
    rd = RT - RB  # Radius difference

    return (
        (rd * depth_cm / H) / 2 + RB
    )**2 * math.pi * depth_cm / 1000
