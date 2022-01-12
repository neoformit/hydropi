"""Operate doser pump to deliver nutrients to the nutrient reservoir."""

import logging

from hydropi.config import config
from .dose import AbstractDoseController

logger = logging.getLogger('hydropi')


class PeroxideController(AbstractDoseController):
    """Dose nutrient reservoir with hydrogen peroxide to eliminate pathogens.

    $40 bottle (1L @ 50%) should last 1 year in a 60L tank.

    - Dilute to 10% and dose 60ml every 5 days
    - 500ml beaker lasts 40 days

    Need to buy another doser pump!
    """

    # Not yet configured
    PIN = config.PIN_PEROXIDE_PUMP
