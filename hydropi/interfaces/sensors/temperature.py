"""Read the temperature in the nutrient tank."""

from hydropi.config import config
from .analogue import AnalogueInterface


class TemperatureSensor(AnalogueInterface):
    """Interface for temperature sensor.

    Call read() to get current temperature in degrees C.
    """

    CHANNEL = config.CHANNEL_TEMPERATURE
    TEXT = 'Temperature'
    UNIT = '°C'
