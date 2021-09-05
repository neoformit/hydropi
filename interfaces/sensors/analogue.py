"""Utilities for reading sensor input.

```
pip3 install adafruit-blinka
pip3 install adafruit-circuitpython-mcp3xxx
```

See https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi
"""

import time
import board
import busio
import logging
import digitalio
import statistics
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

logger = logging.getLogger(__name__)


class AnalogueInterface:
    """Abstract interface for an analogue sensor input."""

    UNIT = None
    MEDIAN_INTERVAL_SECONDS = 0.1

    def __init__(self, channel):
        """Build interface to MCP3008 chip.

        Pass the required channel and request readings with ai.read().
        """
        SPI = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        CS = digitalio.DigitalInOut(board.D22)
        mcp = MCP.MCP3008(SPI, CS)

        # Create analog input channel
        pin = getattr(MCP, f"P{channel}")
        self.interface = AnalogIn(mcp, pin)
        if self.UNIT is None:
            raise AttributeError("AnalogueInterface must define a UNIT")

    def read(self, n=1):
        """Return channel reading."""
        if n == 1:
            r = self.interface.value
        else:
            r = self.read_median(n)
        logger.debug(
            f"{type(self).__name__} READ: {r} {self.UNIT} (n={n})")
        return r

    def read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.interface.value)
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        return statistics.median(readings)

    def test(self):
        """Test channel readings."""
        logger.info(f"Testing {type(self).__name__} analogue sensor...")
        logger.info("~~~~~~ Press CTRL+C to end test ~~~~~~")
        time.sleep(1)
        while True:
            logger.info(f"READING: {self.interface.value}{self.UNIT}")
            time.sleep(3)
