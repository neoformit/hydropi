"""Check nutrient concentration."""

import logging
from threading import Thread

from hydropi.config import config
from hydropi.interfaces.sensors.ec import ECSensor
from hydropi.interfaces.controllers.ec import ECController
from hydropi.process.errors import handle_errors

logger = logging.getLogger('hydropi')


@handle_errors
def level():
    """Check nutrient levels."""
    sensor = ECSensor()
    stat = sensor.read(n=5)

    # Not yet capable of maintenance
    return stat

    # Need to refactor to use database history and take action based on median
    # levels over past hour. This prevents responding to spurious (spike)
    # measurements - like when additions have just been mixed into the tank!

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
