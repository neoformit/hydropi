"""Check the nutrient pressure tank level and adjust with pressure pump."""

import logging
from threading import Thread

# import notifications
from config import config
from process.check.time import is_quiet_time
from interfaces.sensors.pressure import PressureSensor
from interfaces.controllers.pressure import PressurePumpController

logger = logging.getLogger(__name__)


def level():
    """Check pressure level."""
    sensor = PressureSensor()
    stat = sensor.read(n=5)
    logger.info(f"READ pressure: {stat} {sensor.UNIT}")

    if stat < config.MIN_PRESSURE_PSI:
        if stat < config.MIN_PRESSURE_PSI - config.PRESSURE_DANGER_PSI:
            message = (
                f"System pressure below ALERT level: {stat} {sensor.UNIT}")
            logger.warning(message)
            # notifications.alert(message)
        else:
            logger.debug(
                "System pressure below lower limit of"
                f" {config.MIN_PRESSURE_PSI} {sensor.UNIT}")
        return restore(stat)
    else:
        logger.debug(
            "System pressure above lower limit of"
            f" {config.MIN_PRESSURE_PSI} {sensor.UNIT}")

    if stat < config.MAX_PRESSURE_PSI and is_quiet_time(within_minutes=15):
        logger.debug("Quiet time approaching. Restoring system pressure.")
        return restore(stat)

    if stat > config.MAX_PRESSURE_PSI + config.PRESSURE_DANGER_PSI:
        message = f"System pressure above ALERT level: {stat} {sensor.UNIT}"
        logger.warning(message)
        # notifications.alert(message)
    return stat


def restore(stat):
    """Evaluate system pressure and take action to restore."""
    if is_quiet_time():
        logger.info(
            "Cannot restore system pressure:"
            " waiting for quiet time end to restore.")
        return

    logger.info("Restoring system pressure.")
    pump = PressurePumpController()
    Thread(target=pump.refill).start()
    return stat
