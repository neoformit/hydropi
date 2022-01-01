"""Operate doser pump to decrease the pH of the nutrient reservoir."""

import logging

from hydropi.config import config
from .dose import AbstractDoseController

logger = logging.getLogger(__name__)


class PHController(AbstractDoseController):
    """Control pH with down additive (phosphoric acid).

    Dosage:
    ------
    0.5ml STRAIGHT pH down in 15L
        --> 10X dilution
            --> 5ml in 15L      # Lasts longer
        --> 50X dilution
            --> 25ml in 15L     # More accurate

    """

    PIN = config.PIN_PH_DOWN_PUMP

    def deliver(self):
        """Deliver pH down additive."""
        # Set default dose to 5ml
        super().deliver(ml=5)

    # def balance()  # When pH sensor working
