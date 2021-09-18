"""Read generic analogue signals.

https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008

Not recommended library (deprecated) but the recommended one didn't work!

"""

import time
import logging
import statistics
from Adafruit_MCP3008 import MCP3008

from config import config

logger = logging.getLogger(__name__)


class AnalogueInterface:
    """Abstract interface for an analogue sensor input."""

    UNIT = None
    MIN_UNITS = None
    MAX_UNITS = None
    MIN_VOLTS = None
    MAX_VOLTS = None
    V0_OFFSET = 0
    VREF = 3.3

    def __init__(self, channel):
        """Build interface to MCP3008 chip.

        Pass the required channel and request readings with ai.read().
        """
        self.CHANNEL = channel
        self.mcp = MCP3008(
            cs=config.PIN_CS,
            miso=config.PIN_MISO,
            mosi=config.PIN_MOSI,
            clk=config.PIN_CLK,
        )
        for attr in (
                'UNIT',
                'MIN_UNITS',
                'MAX_UNITS',
                'MIN_VOLTS',
                'MAX_VOLTS'):
            if getattr(self, attr) is None:
                raise AttributeError(
                    f"AnalogueInterface must define '{attr}'")
        if not self.V0_OFFSET:
            logger.warning("No V0_OFFSET set: consider zeroing this device.")

    @property
    def value(self):
        """Calculate current channel reading."""
        bits = self.mcp.read_adc(self.CHANNEL)
        print(f"READ BITS: {bits}")
        volts = bits / 1024 * self.VREF
        print(f"READ VOLTS: {volts}")
        volts_offset = (
            (volts - self.MIN_VOLTS)
            / ((self.MAX_VOLTS - self.MIN_VOLTS) / self.VREF)
            + self.V0_OFFSET
        )
        print(f"READ VOLTS OFFSET: {volts_offset}")
        return volts_offset * self.MAX_UNITS

    def read(self, n=1):
        """Return channel reading."""
        if n == 1:
            r = self.value
        else:
            r = self.read_median(n)
        logger.debug(
            f"{type(self).__name__} READ: {r} {self.UNIT} (n={n})")
        return r

    def read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.value)
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        return statistics.median(readings)

    def test(self):
        """Test channel readings."""
        logger.info(f"Testing {type(self).__name__} analogue sensor...")
        logger.info("~~~~~~ Press CTRL+C to end test ~~~~~~")
        time.sleep(1)
        while True:
            logger.info(f"READING: {self.value} {self.UNIT}")
            time.sleep(0.5)
