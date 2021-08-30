"""Perform cyclical release of nutrient solution."""

import time

from config import config
from interfaces.controllers.flow import NutrientFlowController


def mist():
    """Periodically release nutrients."""
    flow = NutrientFlowController()
    while True:
        flow.on()
        time.sleep(config.MIST_DURATION_SECONDS)
        flow.off()
        time.sleep(CYCLE_MINUTES * 60 - config.MIST_CYCLE_MINUTES)
