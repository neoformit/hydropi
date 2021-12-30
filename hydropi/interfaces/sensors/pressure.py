"""Interface for reading system pressure."""

from hydropi.config import config
from .analogue import AnalogueInterface


class PressureSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call read() to get current pressure.

    0.33 - 3 volts -> 0 - 145 psi
    """

    TEXT = 'pressure'
    UNIT = ' PSI'
    MIN_UNITS = 0
    MAX_UNITS = 175
    MIN_VOLTS = 0.3
    MAX_VOLTS = 3.3
    V0_OFFSET = -0.006152
    DECIMAL_POINTS = None
    CHANNEL = config.CHANNEL_PRESSURE
    RANGE_LOWER = config.MIN_PRESSURE_PSI
    RANGE_UPPER = config.MAX_PRESSURE_PSI
