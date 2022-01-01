"""Read the temperature in the nutrient tank."""

import os

from hydropi.config import config


class TemperatureSensor():
    """Interface for digital temperature sensor using OneWire interface.

    Call read() to get current temperature in degrees C.
    """

    PIN = config.PIN_TEMPERATURE
    TEXT = 'temperature'
    UNIT = '°C'
    DEVICE = '/sys/bus/w1/devices/28-01131b576dcc/w1_slave'

    def __init__(self):
        """Initialize interface."""
        if not os.path.exists(self.DEVICE):
            raise RuntimeError(
                f'OneWire device not found: {self.DEVICE}\n'
                'To ensure that OneWire has been configured for GPIO'
                f' {self.PIN}, run:\n'
                f'$ sudo dtoverlay w1-gpio gpiopin={self.PIN} pullup=0')

    def read(self):
        """Read temperature."""
        with open(self.DEVICE) as f:
            data = f.read().split('\n')[1].split('t=')[1]
        return int(data) / 1000
