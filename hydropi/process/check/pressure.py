"""Check the nutrient pressure tank level and adjust with pressure pump."""

import logging
from threading import Thread

# import notifications
from hydropi.process.check.time import is_quiet_time
from hydropi.interfaces.sensors.pressure import PressureSensor
from hydropi.interfaces.controllers.pressure import PressurePumpController

logger = logging.getLogger('hydropi')


def level():
    """Check pressure level."""
    ps = PressureSensor()
    stat = ps.read(n=5)

    if stat < ps.RANGE_LOWER:
        if stat < ps.DANGER_LOWER:
            message = (
                f"System pressure below ALERT level: {stat}{ps.UNIT}")
            logger.warning(message)
            # notifications.alert(message)
        else:
            logger.info(
                "System pressure below lower limit of"
                f" {ps.RANGE_LOWER}{ps.UNIT}")
        return restore(stat)
    else:
        logger.debug(
            "System pressure above lower limit of"
            f" {ps.RANGE_LOWER}{ps.UNIT}")

    if stat < ps.RANGE_UPPER and is_quiet_time(within_minutes=15):
        logger.info("Quiet time approaching.")
        return restore(stat)

    if stat > ps.DANGER_UPPER:
        message = f"System pressure above ALERT level: {stat}{ps.UNIT}"
        logger.warning(message)
        # notifications.alert(message)
    return stat


def restore(stat):
    """Evaluate system pressure and take action to restore."""
    if is_quiet_time():
        logger.info(
            "Cannot restore system pressure:"
            " waiting for quiet time end to restore.")
        return stat

    logger.info("Restoring system pressure.")
    pump = PressurePumpController()
    Thread(target=pump.refill).start()
    return stat
