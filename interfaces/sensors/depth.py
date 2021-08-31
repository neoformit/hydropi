"""Interface for reading nutrient reservoir depth.

https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
"""

import time
import RPi.GPIO as io

from config import config

SONIC_SPEED = 34300  # cm/sec


class DepthSensor:
    """Interface for digital depth sensor."""

    def __init__(self):
        """Initialise interface."""
        io.setmode(io.BCM)
        io.setup(config.PIN_DEPTH_TRIG, io.OUT)
        io.setup(config.PIN_DEPTH_ECHO, io.IN)
        io.output(config.PIN_DEPTH_TRIG, 0)
        time.sleep(1)

    def read(self):
        """Return current depth in mm."""
        io.output(config.PIN_DEPTH_TRIG, 1)
        time.sleep(0.00001)
        io.output(config.PIN_DEPTH_TRIG, 0)

        start = time.time()
        stop = time.time()

        # collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 0:
            start = time.time()

        # collect end of echo pulse
        while io.input(config.PIN_DEPTH_ECHO) == 1:
            stop = time.time()

        elapsed = stop - start
        return (
            (elapsed * SONIC_SPEED)  # time -> distance
            / 2                      # There and back
            / 10                     # cm -> mm
        )

    def test(self):
        """Test the component interface."""
        while True:
            print(f"Reading: {self.read()}mm")
            time.sleep(1)
