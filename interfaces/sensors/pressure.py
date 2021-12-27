"""Interface for reading system pressure."""

from config import config
from .analogue import AnalogueInterface


class PressureSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call read() to get current pressure.

    0.33 - 3 volts -> 0 - 145 psi
    """

    TEXT = 'Pressure'
    UNIT = 'psi'
    MIN_UNITS = 0
    MAX_UNITS = 175
    MIN_VOLTS = 0.3
    MAX_VOLTS = 3.3
    V0_OFFSET = -0.006152

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_PRESSURE)

    def get_status_text(self, value):
        """Return appropriate status text for given value."""
        if (value > config.MIN_PRESSURE_PSI
                and value < config.MAX_PRESSURE_PSI):
            return self.STATUS.NORMAL
        elif (value > config.MIN_PRESSURE_PSI - config.PRESSURE_DANGER_PSI
              and
              value < config.MAX_PRESSURE_PSI + config.PRESSURE_DANGER_PSI):
            return self.STATUS.WARNING
        return self.STATUS.DANGER
