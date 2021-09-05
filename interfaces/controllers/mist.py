"""Operate solenoid valve to control nutrient release from pressure tank."""

from config import config
from .controller import AbstractController


class MistController(AbstractController):
    """Control valve to deliver nutrient solution."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_MIST_VALVE)
