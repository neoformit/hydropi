"""Operate solenoid valve to control nutrient release from pressure tank."""

from hydropi.config import config
from .controller import AbstractController


class MistController(AbstractController):
    """Control valve to deliver nutrient solution."""

    PIN = config.PIN_MIST_VALVE
