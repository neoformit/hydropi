"""Operate doser pump to deliver nutrients to the nutrient reservoir."""

import logging

from hydropi.config import config
from .dose import AbstractDoseController

logger = logging.getLogger(__name__)


class ECController(AbstractDoseController):
    """Control EC with nutrient additives (two part - control two pumps).

    Dosage:
    ------
    - 50ml (each) in 15L --> 1100 uS

    - deliver(ml=20) into 10L -> +700uS

    """

    PIN = config.PIN_NUTRIENT_PUMP

    # def balance()  # When EC sensor working
