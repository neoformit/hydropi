"""Interface for reading nutrient conductivity levels."""

from hydropi.config import config
from .analogue import AnalogueInterface


class ECSensor(AnalogueInterface):
    """Interface for analogue EC sensor.

    Call .read() to get conductivity in mS.
    """

    CHANNEL = config.CHANNEL_EC
    TEXT = 'EC'
    UNIT = 'mS'
    MIN_UNITS = 0
    MAX_UNITS = 1562
    MIN_VOLTS = 0
    MAX_VOLTS = 2.3
    V0_OFFSET = 0
