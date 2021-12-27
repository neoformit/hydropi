"""Read generic analogue signals.

https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008

Not recommended library (deprecated) but the recommended one didn't work!

"""

import time
import logging
import statistics
try:
    from Adafruit_MCP3008 import MCP3008
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    MCP3008 = io = None

from config import config

logger = logging.getLogger(__name__)


class AnalogueInterface:
    """Abstract interface for an analogue sensor input."""

    UNIT = None
    DECIMAL_POINTS = 4
    VREF = 3.3
    V0_OFFSET = 0
    MIN_UNITS = None
    MAX_UNITS = None
    MIN_VOLTS = None
    MAX_VOLTS = None
    MEDIAN_INTERVAL_SECONDS = None

    def __init__(self, channel):
        """Create interface for the MCP3008 analogue converter chip.

        Pass the required channel and request readings with interface.read().
        """
        self.CHANNEL = channel
        if not getattr(self, 'MEDIAN_INTERVAL_SECONDS'):
            self.MEDIAN_INTERVAL_SECONDS = config.MEDIAN_INTERVAL_SECONDS
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
        self._setup()

    def __del__(self):
        """Clean up on delete."""
        io.cleanup()

    def _setup(self):
        """Create interface to MCP3008 chip."""
        self.mcp = MCP3008(
            cs=config.PIN_CS,
            miso=config.PIN_MISO,
            mosi=config.PIN_MOSI,
            clk=config.PIN_CLK,
        )

    @property
    def value(self):
        """Calculate current channel reading."""
        ref_range = self.MAX_VOLTS - self.MIN_VOLTS

        try:
            # Sometimes RPi 'forgets' the pin IO state
            bits = self.mcp.read_adc(self.CHANNEL)
        except RuntimeError:
            self._setup()
            bits = self.mcp.read_adc(self.CHANNEL)

        logger.debug(f"READ BITS: {bits}")
        volts = self.VREF * bits / 1024
        logger.debug(f"READ VOLTS: {round(volts, 6)}")
        volts_offset = volts + self.V0_OFFSET
        logger.debug(f"READ VOLTS OFFSET: {round(volts_offset, 6)}")
        fraction = (volts_offset - self.MIN_VOLTS) / ref_range
        return fraction * self.MAX_UNITS

    def read(self, n=1):
        """Return channel reading."""
        self._setup()
        if n == 1:
            r = self.value
        else:
            r = self.read_median(n)
        logger.debug(
            f"{type(self).__name__}"
            f" READ: {round(r, self.DECIMAL_POINTS)} {self.UNIT} (n={n})")
        return round(r, 4)

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
            logger.info(f"READING: {self.read()} {self.UNIT}")
            time.sleep(0.5)
