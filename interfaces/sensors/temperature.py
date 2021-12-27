"""Read the temperature in the nutrient tank."""

from config import config
from .analogue import AnalogueInterface


class TemperatureSensor(AnalogueInterface):
    """Interface for temperature sensor.

    Call read() to get current temperature in degrees C.
    """

    TEXT = 'Temperature'
    UNIT = '°C'

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_TEMPERATURE)

    def get_status_text(self, value):
        """Return appropriate status text for given value."""
        return None
