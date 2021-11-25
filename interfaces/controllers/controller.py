"""Abstract controller for single pin output signals."""

import os
import time
import string
import random
import logging
import RPi.GPIO as io

from config import config

logger = logging.getLogger(__name__)


class AbstractController:
    """Control a single pin output device."""

    # Yes, how strange that low is 'on' for this relay...
    ON = 0   # GPIO low
    OFF = 1  # GPIO high

    def __init__(self, pin):
        """Initialize interface."""
        self.PIN = pin
        self.ID = random_string()
        self.state = self.OFF
        self.claim_ownership()
        io.setmode(io.BCM)
        io.setup(self.PIN, io.OUT)
        io.output(self.PIN, self.state)

    def __del__(self):
        """Clean up on delete."""
        io.cleanup()

    def on(self):
        """Activate the device."""
        self.state = self.ON
        logger.debug(
            f"{type(self).__name__}: switch output state to {self.state}")
        io.output(self.PIN, self.state)

    def off(self):
        """Deactivate the device."""
        if not self.has_ownership():
            return
        self.state = self.OFF
        logger.debug(
            f"{type(self).__name__}: switch output state to {self.state}")
        io.output(self.PIN, self.state)

    def claim_ownership(self):
        """Claim ownership of this interface."""
        with open(self.deed, 'w') as f:
            f.write(self.ID)

    def has_ownership(self):
        """Figure out whether self is present owner of this interface."""
        with open(self.deed) as f:
            is_owner = self.ID == f.read().strip('\n ')
        if not is_owner:
            logger.warning(
                type(self).__name__
                + ": OWNERSHIP REVOKED: cannot switch state")
        return is_owner

    @property
    def deed(self):
        """Return filepath of deed."""
        path = os.path.join(config.TEMP_DIR, f"{type(self).__name__}.deed")
        if not os.path.exists(os.path.dirname(path)):
            os.mkdir(os.path.dirname(path))
        return path

    def test(self):
        """Test the controller."""
        logger.info(f"Testing {type(self).__name__} controller...")
        logger.info("~~~~~~ Press CTRL+C to end test ~~~~~~")
        time.sleep(1)
        while True:
            logger.info("SWITCH ON")
            self.on()
            time.sleep(3)
            logger.info("SWITCH OFF")
            self.off()
            time.sleep(3)


def random_string():
    """Return a random ID."""
    return ''.join(random.choices(string.ascii_lowercase, k=12))
