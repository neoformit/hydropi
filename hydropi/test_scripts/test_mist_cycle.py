"""Test the misting cycle while maintaining tank pressure."""

import init_test
init_test.setup()

from time import sleep
from threading import Thread
from RPi import GPIO as io

from hydropi.config import config
from hydropi.process import check
from hydropi.process.delivery import mist


def watch_pressure():
    """Maintain pressure."""
    while True:
        check.pressure.level()
        sleep(60 * config.SWEEP_CYCLE_MINUTES)


try:
    Thread(target=mist).start()
    watch_pressure()
finally:
    io.cleanup()
