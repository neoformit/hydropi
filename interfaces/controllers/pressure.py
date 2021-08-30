"""Operate pressure pump to regulate tank pressure."""

from config import config
import RPi.GPIO as io


class PressurePumpController(AbstractController):
    """Control pressure pump."""

    def __init__(self):
        """Initialize interface"""
        super().__init__(config.PIN_PRESSURE_PUMP)
