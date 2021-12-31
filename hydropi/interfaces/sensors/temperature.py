"""Read the temperature in the nutrient tank."""

from hydropi.config import config
from .analog import AnalogInterface


class TemperatureSensor(AnalogInterface):
    """Interface for temperature sensor.

    Call read() to get current temperature in degrees C.
    """

    CHANNEL = config.CHANNEL_TEMPERATURE
    TEXT = 'temperature'
    UNIT = '°C'
