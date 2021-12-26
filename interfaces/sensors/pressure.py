"""Interface for reading system pressure."""

from config import config
from .analogue import AnalogueInterface


class PressureSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call read() to get current pressure.

    0.33 - 3 volts -> 0 - 145 psi
    """

    UNIT = 'psi'
    MIN_UNITS = 0
    MAX_UNITS = 200
    MIN_VOLTS = 0.3
    MAX_VOLTS = 3.3
    V0_OFFSET = -0.006152

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_PRESSURE)
