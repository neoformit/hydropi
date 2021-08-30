"""Interface for reading nutrient reservoir depth.

See https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
"""

from config import config
import RPi.GPIO as io

SONIC_SPEED = 34300  # cm/sec


class DepthSensor:
    """Interface for digital depth sensor."""

    def __init__(self):
        """Initialise interface."""
        io.setmode(io.BCM)
        io.setup(config.PIN_DEPTH_TRIG, io.OUT)
        io.setup(config.PIN_DEPTH_ECHO, io.IN)

    def read(self):
        """Return current depth in mm."""
        io.output(GPIO_TRIGGER, 1)
        time.sleep(0.00001)
        io.output(GPIO_TRIGGER, 0)

        start = time.time()
        stop = time.time()

        # save start time
        while io.input(config.PIN_DEPTH_ECHO) == 0:
            start = time.time()

        # save time of arrival
        while io.input(config.PIN_DEPTH_ECHO) == 1:
            stop = time.time()

        elapsed = stop - start
        return (
            (elapsed * SONIC_SPEED)  # time -> distance
            / 2                      # There and back
            / 10                     # cm -> mm
        )
