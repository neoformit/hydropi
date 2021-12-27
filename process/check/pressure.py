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

    if stat < config.MIN_PRESSURE_PSI - config.PRESSURE_DANGER_PSI:
        message = f"Tank pressure below ALERT level: {stat} {sensor.UNIT}"
        logger.warning(message)
        # notifications.alert(message)
    if stat > config.MAX_PRESSURE_PSI + config.PRESSURE_DANGER_PSI:
        message = f"Tank pressure above ALERT level: {stat} {sensor.UNIT}"
        logger.warning(message)
        # notifications.alert(message)
    elif stat > config.MIN_PRESSURE_PSI:
        logger.debug(
            "Tank pressure above lower limit of"
            f" {config.MIN_PRESSURE_PSI} {sensor.UNIT}"
        )
        return stat
    return restore(stat)


def restore(stat):
    """Evaluate tank pressure and take action to restore."""
    if is_quiet_time():
        logger.info(
            "Tank pressure low: waiting for quiet time end to restore.")
        return

    logger.info("Tank pressure low: restoring pressure.")
    pump = PressurePumpController()
    Thread(target=pump.refill).start()
    return stat
