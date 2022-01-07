"""Interface for reading nutrient pH level."""

from hydropi.config import config
from .analog import AnalogInterface


class PHSensor(AnalogInterface):
    """Interface for analog pressure sensor.

    Call .read() to get current pressure.
    """

    CHANNEL = config.CHANNEL_PH
    TEXT = 'pH'
    UNIT = ''
    MIN_UNITS = 1.351
    MAX_UNITS = 12
    MIN_VOLTS = 1.8857
    MAX_VOLTS = 3.3
    INVERSE = True
    RANGE_LOWER = config.PH_MIN
    RANGE_UPPER = config.PH_MAX
    DECIMAL_POINTS = 2
