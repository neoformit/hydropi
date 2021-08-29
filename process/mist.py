"""Perform cyclical release of nutrient solution."""

import time

import config
from interfaces.controllers.flow import NutrientFlowController


def mist():
    """Periodically release nutrients."""
    flow = NutrientFlowController()
    while True:
        flow.on()
        time.sleep(config.get('MIST_DURATION_SECONDS'))
        flow.off()
        time.sleep(CYCLE_MINUTES * 60 - config.get('MIST_CYCLE_MINUTES'))
