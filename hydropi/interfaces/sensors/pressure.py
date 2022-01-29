"""Interface for reading system pressure."""

import logging

from hydropi.config import config
from .analog import AnalogInterface

logger = logging.getLogger('hydropi')


class PressureSensor(AnalogInterface):
    """Interface for analog pressure sensor.

    Call read() to get current pressure.
    """

    TEXT = 'pressure'
    UNIT = ' PSI'
    MIN_UNITS = 0
    MAX_UNITS = 175
    MIN_VOLTS = 0.3
    MAX_VOLTS = 3.3
    V0_OFFSET = -0.006152
    DECIMAL_POINTS = None
    CHANNEL = config.CHANNEL_PRESSURE

    def __init__(self):
        """Initialise object."""
        self.RANGE_LOWER = config.MIN_PRESSURE_PSI
        self.RANGE_UPPER = config.MAX_PRESSURE_PSI
        super().__init__()

    def get_tank_volume(self):
        """Estimate tank volume in litres based on the current pressure."""
        psi = self.read()
        litres = (
            config.PRESSURE_TANK_VOLUME_L
            * (psi / config.PRESSURE_TANK_BASE_PSI - 1)
            / (psi / config.PRESSURE_TANK_BASE_PSI)
        )
        logger.debug(
            f'{type(self).__name__} READ tank volume {litres:.2f} litres')
        return litres
