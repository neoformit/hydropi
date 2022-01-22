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

from hydropi.config import config

logger = logging.getLogger('hydropi')


class AbstractController:
    """Control a single pin output device."""

    # Yes, how strange that low is 'on' for this relay board...
    ON = 0      # GPIO low
    OFF = 1     # GPIO high
    PIN = None  # Must be set in subclass

    def __init__(self):
        """Initialize interface."""
        if self.PIN is None:
            raise AttributeError(
                "Subclass of AbstractController must set self.PIN to"
                " a valid output pin.")
        self.ID = ''.join(random.choices(string.ascii_lowercase, k=12))
        self._set_state(self.OFF)

    def __del__(self):
        """Clean up IO hardware on termination."""
        if os.path.exists(self._deed):
            os.remove(self._deed)
        if config.DEVMODE:
            logger.warning("DEVMODE: skip IO cleanup")
            return
        io.setmode(io.BCM)
        io.cleanup(self.PIN)

    def run(self, seconds=None):
        """Run interactively (CLI only)."""
        self.on()
        if seconds is not None:
            input(f'Running {type(self).__name__} for {seconds} seconds')
            time.sleep(seconds)
        else:
            input(f'Running {type(self).__name__}... press enter to stop')
        self.off()

    def on(self):
        """Activate the device."""
        logger.info(
            f"{type(self).__name__}: switch output state to {self.ON}:ON")
        self._set_state(self.ON)
        self._claim_ownership()

    def off(self):
        """Deactivate the device."""
        owners = self._revoke_ownership()
        if owners:
            return logger.info(
                f"{type(self).__name__}:"
                " OWNERSHIP REVOKED FROM SHARED INTERFACE: ownership has been"
                f" delegated to threads {owners}")
        logger.info(
            f"{type(self).__name__}: switch output state to {self.OFF}:OFF")
        self._set_state(self.OFF)

    def _set_state(self, state):
        """Change the state of the controller."""
        self.state = state
        if config.DEVMODE:
            logger.warning("DEVMODE: spoofed IO operation")
            return
        io.setmode(io.BCM)
        io.setup(self.PIN, io.OUT)
        io.output(self.PIN, state)

    def _get_owners(self):
        """Return list of owners of this interface."""
        if not os.path.exists(self._deed_dir):
            return []
        return os.listdir(self._deed_dir)

    def _claim_ownership(self):
        """Claim ownership of this interface by writing a deed."""
        if self.ID not in self._get_owners():
            logger.debug(f'Writing deed for ID {self.ID}: {self._deed}')
            with open(self._deed, 'w'):
                pass

    def _revoke_ownership(self):
        """Revoke ownership of this interface from the deed."""
        logger.debug(f'Revoke deed for {self.ID}')
        owners = self._get_owners()
        try:
            owners.remove(self.ID)
            os.remove(self._deed)
        except ValueError:
            # Somehow not an owner... but that's ok we're revoking anyways
            pass
        if owners:
            logger.debug(f'Remaining owners: {owners}')
            return owners
        return False

    @property
    def _deed_dir(self):
        """Return path of the deed directory for this interface."""
        path = os.path.join(config.TEMP_DIR, 'deeds', f"{type(self).__name__}")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @property
    def _deed(self):
        """Return path of the deed directory for this interface."""
        return os.path.join(self._deed_dir, f"{self.ID}")

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
