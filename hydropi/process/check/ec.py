"""Check nutrient concentration."""

import logging
from threading import Thread

from hydropi.config import config
from hydropi.interfaces.sensors.ec import ECSensor
from hydropi.interfaces.controllers.ec import ECController

logger = logging.getLogger('hydropi')


def level():
    """Check nutrient levels."""
    sensor = ECSensor()
    stat = sensor.read(n=5)

    # Not yet capable of maintenance
    return stat

    if config.EC_ACTION_THRESHOLD > abs(stat - config.EC_TARGET):
        logger.info(f"EC within acceptable range of target {config.EC_TARGET}")
        return stat
    return restore(stat)


def restore(stat):
    """Evaluate EC levels and take action to restore."""
    if (stat - config.EC_TARGET) > 0:
        logger.warning("EC TOO HIGH: CANNOT TAKE ACTION")
        return stat
    logger.info("EC too low: performing top-up")
    ec = ECController()
    Thread(ec.top_up).start()
    return stat
