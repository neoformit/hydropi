"""Operate pressure pump to regulate tank pressure."""

import time
import logging

from config import config
from interfaces.sensors.pressure import PressureSensor

from .controller import AbstractController

logger = logging.getLogger(__name__)


class PressurePumpController(AbstractController):
    """Control pressure pump."""

    PIN = config.PIN_PRESSURE_PUMP

    def refill(self):
        """Activate pump to restore system pressure.

        Refill pressure in pulses of dynamic length, checking pressure status
        between pulses. The pressure sensor is very inaccurate while the pump
        is running, so pause and check is a much better strategy if done
        intelligently.
        """
        def _next_duration():
            """Calculate duration of next fill round."""
            ps = PressureSensor()
            psi = ps.read(n=5)
            if psi > config.MAX_PRESSURE_PSI:
                return psi, 0
            # Reduce the duration based on remaining fill
            duration = round(
                config.PRESSURE_REFILL_DURATION_SECONDS
                * (config.MAX_PRESSURE_PSI - psi)
                / (config.MAX_PRESSURE_PSI - config.MIN_PRESSURE_PSI)
            ) + 5  # Extra 5 seconds ensures that MAX is always reached
            logger.info(f"Current pressure: {psi}{PressureSensor.UNIT}")
            logger.info(f"Refill duration: {duration} seconds")
            return psi, duration

        logger.info(
            "ACTION: restore system pressure to"
            f" {config.MAX_PRESSURE_PSI}{PressureSensor.UNIT}")

        cumulative_duration = 0
        psi, duration = _next_duration()
        while psi < config.MAX_PRESSURE_PSI:
            self.on()
            time.sleep(duration)
            self.off()
            cumulative_duration += duration
            time.sleep(5)
            psi, duration = _next_duration()
            logger.info(
                f"Refill paused at {psi}{PressureSensor.UNIT}.")

        logger.info(
            f"System pressure restored to {psi}{PressureSensor.UNIT}"
            f" in {cumulative_duration} seconds")
