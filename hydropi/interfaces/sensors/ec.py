"""Interface for reading nutrient conductivity levels."""

try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

import time
import logging

from hydropi.config import config
from .analog import AnalogInterface
from .temperature import PipeTemperatureSensor

logger = logging.getLogger('hydropi')

"""Switching TDS sensor circuit.

- GPIO default state (i.e. not set up) is enough to trigger npn transistor if
  using pin with pullup high (GPIO 2-8). See http://www.panu.it/raspberry/
- Either way, turns off on io.setup()
- io.outuput() on/off then controls circuit adequately
- But unlikely that this will work with 12v TDS circuit without a MOSFET:
  see example https://raspberrypi.stackexchange.com/questions/67166/raspberry-pi-mosfet-npn-transistor-24v-solenoid-circuit-gets-hot?rq=1

For now, trying to achieve this with a relay channel.
"""


class ECSensorIsolator:
    """Provide isolation interface for ECSensor hardware."""

    ON = 0
    OFF = 1
    PIN = config.SPARE_RELAY_PIN_A

    def _setup(self):
        """Initialize interface."""
        if config.DEVMODE:
            return
        io.setmode(io.BCM)
        io.setup(self.PIN, io.OUT)

    def __enter__(self):
        """Enable isolation."""
        self._setup()
        logger.debug("EC isolation ON")
        self.switch_power(self.ON)
        # Short pause to let electricity dissipate
        time.sleep(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disable isolation."""
        logger.debug("EC isolation OFF")
        self.switch_power(self.OFF)

    def switch_power(self, state):
        """Switch 12v power to TDS module on/off."""
        if config.DEVMODE:
            return
        io.output(self.PIN, state)


class ECSensor(AnalogInterface):
    """Interface for analog EC sensor.

    Call .read() to get conductivity in mS.
    """

    CHANNEL = config.CHANNEL_EC
    TEXT = 'EC'
    UNIT = 'μS'
    MIN_UNITS = 0
    MAX_UNITS = 10000  # Spec says 3125... so this is interesting
    MIN_VOLTS = 0
    MAX_VOLTS = 3.3
    V0_OFFSET = 0
    DECIMAL_POINTS = None

    isolation = ECSensorIsolator

    # Temperature correction polynomial coefficients
    # Will have to recalculate these for TankTemperatureSensor
    TC_A = 0.50938
    TC_E = 2
    TC_B = -15.55071
    TC_C = 56

    def __init__(self):
        """Initialise object."""
        self.RANGE_LOWER = config.EC_MIN
        self.RANGE_UPPER = config.EC_MAX
        super().__init__()

    def read_transform(self, value):
        """Apply temperature correction to reading."""
        # Worth doing with pipe temperature?
        ts = PipeTemperatureSensor()
        t = ts.read()
        # Polynomial function between temperature and EC offset
        offset = self.TC_A * t ** self.TC_E + self.TC_B * t + self.TC_C
        logger.debug(f"Offset EC value {value} at {t}{ts.UNIT}: {offset}")
        return value + offset
