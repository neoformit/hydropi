"""Operate doser pump to decrease the pH of the nutrient reservoir."""

import config
from .controller import AbstractController


class PhDownController(AbstractController):
    """Control acid delivery to decrease the pH."""

    def __init__(self):
        """Initialize interface"""
        super().__init__(config.PIN_PH_DOWN_PUMP)
