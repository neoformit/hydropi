"""Operate doser pump to deliver nutrients to the nutrient reservoir."""

from config import config
from .controller import AbstractController


class ECController(AbstractController):
    """Control nutrient delivery to increase EC."""

    def __init__(self):
        """Initialize interface."""
        super().__init__(config.PIN_EC_UP_PUMP)
