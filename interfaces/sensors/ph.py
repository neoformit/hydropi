"""Interface for reading nutrient pH level."""

from config import config
from .analogue import AnalogueInterface


class PHSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call .read() to get current pressure.
    """

    TEXT = 'pH'
    UNIT = ''
    MIN_UNITS = 0
    MAX_UNITS = 14
    MIN_VOLTS = 0
    MAX_VOLTS = 3.3

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_PH)

    def get_status_text(self, value):
        """Return appropriate status text for given value."""
        return None
