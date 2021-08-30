"""Abstract controller for single pin output signals."""

import RPi.GPIO as io


class AbstractController:
    """Control a single pin output device."""

    ON = 0
    OFF = 1

    def __init__(self, pin):
        """Initialize interface."""
        self.PIN = pin
        self.state = self.OFF
        io.setmode(io.BCM)
        io.setup(self.PIN, io.OUT)
        io.output(self.PIN, self.state)

    def on(self):
        """Activate the device."""
        self.state = self.ON
        io.output(self.PIN, self.state)

    def off(self):
        """Deactivate the device."""
        self.state = self.OFF
        io.output(self.PIN, self.state)
