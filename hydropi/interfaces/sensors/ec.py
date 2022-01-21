"""Interface for reading nutrient conductivity levels."""

from hydropi.config import config
from .analog import AnalogInterface


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
