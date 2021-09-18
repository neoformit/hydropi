"""Read the temperature in the nutrient tank."""

from config import config
from .analogue import AnalogueInterface


class Thermometer(AnalogueInterface):
    """Interface for temperature sensor.

    Call read() to get current temperature in degrees C.
    """

    UNIT = '°C'

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_TEMPERATURE)
