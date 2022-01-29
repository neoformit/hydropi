"""Interface for reading nutrient conductivity levels."""

from hydropi.config import config
from .analog import AnalogInterface
from .temperature import PipeTemperatureSensor


class ECSensor(AnalogInterface):
    """Interface for analog EC sensor.

    Call .read() to get conductivity in mS.
    """

    CHANNEL = config.CHANNEL_EC
    TEXT = 'EC'
    UNIT = 'μS'
    MIN_UNITS = 0
    MAX_UNITS = 10000  # Spec says 3125...
    MIN_VOLTS = 0
    MAX_VOLTS = 3.3
    V0_OFFSET = 0
    RANGE_LOWER = config.EC_MIN
    RANGE_UPPER = config.EC_MAX
    DECIMAL_POINTS = None

    # Temperature correction coefficients
    # Will have to recalculate these for TankTemperatureSensor
    TC_M = -14.21
    TC_C = 443

    def read_transform(self, value):
        """Apply temperature correction to reading."""
        # Not worth doing with pipe temperature
        return value

        ts = PipeTemperatureSensor()
        return value + ts.read() * self.TC_M + self.TC_C
