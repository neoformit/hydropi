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
    MIN_UNITS = 0
    MAX_UNITS = 14
    MIN_VOLTS = 0
    MAX_VOLTS = 3.3
