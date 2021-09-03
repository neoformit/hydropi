"""Interface for reading nutrient pH level."""

from config import config
from .analogue import AnalogueInterface


class PHSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call .read() to get current pressure.
    """

    UNIT = 'pH'

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_PH)
