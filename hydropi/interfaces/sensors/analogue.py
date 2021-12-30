"""Read generic analogue signals.

https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008

Required attributes:
--------------------
CHANNEL     | Relay channel to operate (zero-indexed)
TEXT        | Display text for sensor e.g. "temperature"
UNIT        | Units of measurement e.g. "°C"
MIN_UNITS   | Min units sensor can measure - often zero
MAX_UNITS   | Max units sensor can measure e.g. 100
MIN_VOLTS   | Voltage output at minimum reading
MAX_VOLTS   | Voltage output at maximum reading, often 3.3v
RANGE_LOWER | Lower limital of optimal range
RANGE_UPPER | Upper limital of optimal range
DANGER_DIFF | Danger zone variance from optimal range

"""

import time
import random
import logging
import statistics
try:
    from Adafruit_MCP3008 import MCP3008
    import RPi.GPIO as io
except ModuleNotFoundError:
    print("WARNING: Can't import Pi packages - assume developer mode")
    MCP3008 = io = None

from hydropi.config import config

logger = logging.getLogger(__name__)


class STATUS:
    """Status options."""

    NORMAL = 'normal'
    WARNING = 'warning'
    DANGER = 'danger'


class AnalogueInterface:
    """Abstract interface for an analogue sensor input."""

    DECIMAL_POINTS = 4  # Set to None for integer
    MEDIAN_INTERVAL_SECONDS = None

    # Sensor calibration params
    VREF = 3.3
    V0_OFFSET = 0
    MIN_UNITS = None
    MAX_UNITS = None
    MIN_VOLTS = None
    MAX_VOLTS = None

    REQUIRED_ATTRIBUTES = (
        'CHANNEL',      # Relay channel to operate (zero-indexed)
        'TEXT',         # Display text for sensor e.g. "temperature"
        'UNIT',         # Units of measurement e.g. °C (may prefix with space)
        'MIN_UNITS',    # Min units sensor can measure - often zero
        'MAX_UNITS',    # Max units sensor can measure e.g. 100
        'MIN_VOLTS',    # Voltage output at minimum reading
        'MAX_VOLTS',    # Voltage output at maximum reading, often 3.3v
        'RANGE_LOWER',  # Lower limital of optimal range
        'RANGE_UPPER',  # Upper limital of optimal range
    )

    def __init__(self):
        """Create interface for the MCP3008 analogue converter chip.

        Pass the required channel and request readings with interface.read().
        """
        if not getattr(self, 'MEDIAN_INTERVAL_SECONDS'):
            self.MEDIAN_INTERVAL_SECONDS = config.MEDIAN_INTERVAL_SECONDS
        err = []
        for attr in self.REQUIRED_ATTRIBUTES:
            if getattr(self, attr, None) is None:
                err.append(attr)
        if err:
            raise AssertionError(
                f"Analogue interface subclass missing required attributes:\n- "
                + '\n- '.join(err)
                + '\n\n' + __doc__
            )
        if not self.V0_OFFSET:
            logger.warning("No V0_OFFSET set: consider zeroing this device.")
        self.RANGE = self.RANGE_UPPER - self.RANGE_LOWER
        self.DANGER_LOWER = self.RANGE_LOWER - self.RANGE
        self.DANGER_UPPER = self.RANGE_UPPER + self.RANGE
        self.FLOOR = self.RANGE_LOWER - self.RANGE * 2     # Absolute min
        self.CEILING = self.RANGE_UPPER + self.RANGE * 2   # Absolute max
        self._setup()

    def _setup(self):
        """Create interface to MCP3008 chip."""
        if config.DEVMODE:
            logger.warning("DEVMODE: configure sensor without ADC interface")
            return
        self.mcp = MCP3008(
            cs=config.PIN_CS,
            miso=config.PIN_MISO,
            mosi=config.PIN_MOSI,
            clk=config.PIN_CLK,
        )

    @property
    def value(self):
        """Calculate current channel reading."""
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
        ref_range = self.MAX_VOLTS - self.MIN_VOLTS
        fraction = (volts_offset - self.MIN_VOLTS) / ref_range
        return fraction * self.MAX_UNITS

    def read(self, n=1):
        """Return channel reading."""
        self._setup()
        if n > 1:
            r = self._read_median(n)
        else:
            r = self.value
        rounded = round(r, self.DECIMAL_POINTS)
        logger.info(
            f"{type(self).__name__}"
            f" READ: {rounded}{self.UNIT} (n={n})")
        return(rounded)

    def _read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.value)
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        return statistics.median(readings)

    def get_status_text(self, value):
        """Return appropriate status text for given value."""
        if (value > self.RANGE_LOWER
                and value < self.RANGE_UPPER):
            return STATUS.NORMAL
        elif (value > self.DANGER_LOWER
                and value < self.DANGER_UPPER):
            return STATUS.WARNING
        return STATUS.DANGER

    @classmethod
    def get_status(cls):
        """Create interface and return current status data."""
        sensor = cls()
        if config.DEVMODE:
            logger.warning("DEVMODE: Return random reading")
            current = round(
                random.uniform(sensor.DANGER_LOWER, sensor.DANGER_UPPER),
                sensor.DECIMAL_POINTS)
        else:
            current = sensor.read(n=5)

        # Represent reading as a percent of absolute limits such that 0.5 is in
        # the middle of the optimal range (for display on dials).
        if current > sensor.CEILING:
            percent = 1
        elif current < sensor.FLOOR:
            percent = 0
        else:
            percent = round(
                (current - sensor.FLOOR) / (sensor.CEILING - sensor.FLOOR), 4)

        return {
            'text': cls.TEXT,
            'status': sensor.get_status_text(current),
            'value': current,
            'percent': percent,
            'unit': cls.UNIT,
        }

    def test(self):
        """Test channel readings."""
        logger.info(f"Testing {type(self).__name__} analogue sensor...")
        logger.info("~~~~~~ Press CTRL+C to end test ~~~~~~")
        time.sleep(1)
        while True:
            logger.info(f"READING: {self.read()}{self.UNIT}")
            time.sleep(0.5)
