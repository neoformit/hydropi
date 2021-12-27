"""Abstract controller for single pin output signals."""

import os
import time
import string
import random
import logging
try:
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    io = None

from config import config

logger = logging.getLogger(__name__)


class AbstractController:
    """Control a single pin output device."""

    # Yes, how strange that low is 'on' for this relay board...
    ON = 0      # GPIO low
    OFF = 1     # GPIO high
    PIN = None  # Must be set in subclass

    def __init__(self):
        """Initialize interface."""
        if self.PIN is None:
            raise ValueError(
                "Subclass of AbstractController must set self.PIN to"
                " a valid output pin.")
        self.ID = ''.join(random.choices(string.ascii_lowercase, k=12))
        self._claim_ownership()
        self._set_state(self.OFF)

    def on(self):
        """Activate the device."""
        logger.info(
            f"{type(self).__name__}: switch output state to {self.ON}:ON")
        self._set_state(self.ON)
        self._claim_ownership()

    def off(self):
        """Deactivate the device."""
        if not self._has_ownership():
            return
        is_shared = self._revoke_ownership()
        if is_shared:
            logger.info(
                f"{type(self).__name__}:"
                " OWNERSHIP REVOKED: state has been delegated to shared owner")
            return
        logger.info(
            f"{type(self).__name__}: switch output state to {self.OFF}:OFF")
        self._set_state(self.OFF)

    def _set_state(self, state):
        """Change the state of the controller."""
        self.state = state
        io.setmode(io.BCM)
        io.setup(self.PIN, io.OUT)
        io.output(self.PIN, state)

    def _claim_ownership(self):
        """Claim ownership of this interface by writing a deed."""
        with open(self._deed, 'a') as f:
            f.write(self.ID + '\n')

    def _revoke_ownership(self):
        """Revoke ownership of this interface from the deed."""
        with open(self._deed) as f:
            owners = [x for x in f.read().split('\n') if x]
        owners.remove(self.ID)

        if owners:
            with open(self._deed, 'w') as f:
                f.write('\n'.join(owners) + '\n')
            return True
        os.remove(self._deed)
        return False

    @property
    def _deed(self):
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
