"""Abstract controller for a doser pump to be run with mixer pump."""

import time
import logging
from threading import Thread

from hydropi.config import config

from .controller import AbstractController
from .mix import MixPumpController

logger = logging.getLogger('hydropi')


class AbstractDoseController(AbstractController):
    """Deliver additives with a peristaltic doser pump.

    Calibration:
    -----------

    - Takes 79 seconds to pump 50ml
    - Flow rate 1.57 sec/ml
    - Or 0.637 ml/sec

    N.B. Doser pump is probably inaccurate below 1ml

    """

    DEFAULT_ML = 10
    FLOW_RATE = 0.637  # Pump flow rate in ml/sec

    def deliver(self, ml=None):
        """Deliver the specified volume of additive."""
        ml = ml or self.DEFAULT_ML
        logger.info(f"ACTION: {type(self).__name__} deliver {ml}ml")

        # Start mixing pump and delay
        delay = config.MIX_ADDITION_DELAY_SECONDS
        logger.info(f"DELAY: {delay} seconds")
        mixer = MixPumpController()
        Thread(target=mixer.mix).start()
        time.sleep(delay)

        # Deliver additive
        self.on()
        time.sleep(ml / self.FLOW_RATE)
        self.off()
