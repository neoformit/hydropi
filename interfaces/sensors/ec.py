"""Interface for reading nutrient conductivity levels."""

from config import config
from .analogue import AnalogueInterface


class ECSensor(AnalogueInterface):
    """Interface for analogue EC sensor.

    Call .read() to get conductivity in mS.
    """

    TEXT = 'EC'
    UNIT = 'mS'
    MIN_UNITS = 0
    MAX_UNITS = 1562
    MIN_VOLTS = 0
    MAX_VOLTS = 2.3
    V0_OFFSET = 0

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_EC)

    def get_status_text(self, value):
        """Return appropriate status text for given value."""
        return None
