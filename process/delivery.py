"""Perform cyclical release of nutrient solution."""

import time

from config import config
from interfaces.controllers.flow import FlowController


def mist():
    """Periodically release nutrients."""
    flow = FlowController()
    while True:
        flow.on()
        time.sleep(config.MIST_DURATION_SECONDS)
        flow.off()
        time.sleep(CYCLE_MINUTES * 60 - config.MIST_CYCLE_MINUTES)
