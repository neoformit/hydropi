"""Interface for reading nutrient conductivity levels."""

from config import config
from .analogue import AnalogueInterface


class ECSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call .read() to get current pressure.
    """

    UNIT = 'mS'

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_EC)
