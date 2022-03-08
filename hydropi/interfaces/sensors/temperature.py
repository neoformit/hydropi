"""Read the temperature in the nutrient tank."""

import os
import random
import logging

from hydropi.config import config
from hydropi.notifications import telegram
from .analog import AnalogInterface

logger = logging.getLogger('hydropi')


class PipeTemperatureSensor():
    """Measurements temperature inside a pipe in full-sun.

    Uses a digital temperature sensor using OneWire interface.

    Call read() to get current temperature in degrees C.
    """

    PIN = config.PIN_TEMPERATURE_PIPE
    TEXT = 'temperature (pipe)'
    UNIT = '°C'
    DEVICE = '/sys/bus/w1/devices/28-01131b576dcc/w1_slave'
    DECIMAL_POINTS = 1

    def __init__(self):
        """Initialize interface."""
        if config.DEVMODE:
            return logger.warning("DEVMODE: spoofed w1 interface")
        if not os.path.exists(self.DEVICE):
            raise RuntimeError(
                f'OneWire device not found: {self.DEVICE}\n'
                'To ensure that OneWire has been configured for GPIO'
                f' {self.PIN}, run:\n'
                f'$ sudo dtoverlay w1-gpio gpiopin={self.PIN} pullup=0')

    def read(self):
        """Read temperature."""
        try:
            if config.DEVMODE:
                logger.warning("DEVMODE: spoofed temperature reading")
                return round(random.uniform(18, 45), self.DECIMAL_POINTS)
            with open(self.DEVICE) as f:
                content = f.read()
                logger.debug(f"READ temperature:\n{content}")
                data = content.split('\n')[1].split('t=')[1]
            return round(int(data) / 1000, self.DECIMAL_POINTS)
        except Exception as exc:
            message = (
                "Error reading PipeTemperature sensor from OneWire"
                f" interface. Read content:\n{content}\n\n"
                + str(exc)
            )
            telegram.notify(message)
            logger.error(message)
        return 0


class TankTemperatureSensor(AnalogInterface):
    """Measure temperature in the nutrient tank.

    Doesn't seem to be working - gives the same reading as empty pin.
    """

    CHANNEL = config.CHANNEL_TEMPERATURE_PIPE
    TEXT = 'temperature (tank)'
    UNIT = '°C'
    MIN_UNITS = 0
    MAX_UNITS = 100
    MIN_VOLTS = 0
    MAX_VOLTS = 3.3
    DECIMAL_POINTS = 1
    RANGE_LOWER = 18
    RANGE_UPPER = 25
