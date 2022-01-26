"""Check nutrient solution tank depth."""

import logging
from threading import Thread

from hydropi.config import config
from hydropi.interfaces.sensors.depth import DepthSensor
from hydropi.interfaces.controllers.water import WaterController

logger = logging.getLogger('hydropi')


def depth():
    """Check tank depth."""
    sensor = DepthSensor()
    stat = sensor.read(n=5)

    # Not yet capable of maintenance
    return stat

    depth_lower_limit = config.DEPTH_MAXIMUM_MM * config.DEPTH_ACTION_THRESHOLD

    if stat > depth_lower_limit:
        logger.info(
            "Tank depth within acceptable range of target"
            f" {config.DEPTH_MAXIMUM_MM}{sensor.UNIT}"
        )
        return stat
    return restore(stat)


def restore(stat):
    """Evaluate tank depth and take action to restore."""
    logger.info("Tank depth low: topping up with water")
    water = WaterController()
    Thread(water.refill).start()
    return stat
