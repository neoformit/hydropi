"""Interface for reading system pressure."""

import config
from .analogue import AnalogueInterface


class PressureSensor(AnalogueInterface):
    """Interface for analogue pressure sensor.

    Call .read() to get current pressure.
    """

    def __init__(self):
        """Initialise interface."""
        super().__init__(config.CHANNEL_PRESSURE)
