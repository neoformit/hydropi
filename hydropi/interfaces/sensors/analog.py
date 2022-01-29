"""Read generic analog signals.

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

from hydropi.config import config, STATUS

logger = logging.getLogger('hydropi')


class AnalogInterface:
    """Abstract interface for an analog sensor input."""

    DECIMAL_POINTS = 4  # Set to None for integer
    MEDIAN_INTERVAL_SECONDS = config.MEDIAN_INTERVAL_SECONDS

    # Sensor calibration params
    VREF = 3.3
    V0_OFFSET = 0
    MIN_UNITS = None
    MAX_UNITS = None
    MIN_VOLTS = None
    MAX_VOLTS = None
    INVERSE = False     # Set True if volts are inverse of value
    DEFAULT_MEDIAN_SAMPLES = 5

    REQUIRED_ATTRIBUTES = (
        'CHANNEL',      # ADC channel to read (zero-indexed)
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
        """Create interface for the MCP3008 analog converter chip.

        Pass the required channel and request readings with interface.read().

        Attributes that may change at runtime (i.e. exposed config) should
        be declared as instance attributes in the subclass.
        """
        self._validate()
        self._setup()
        self.RANGE = self.RANGE_UPPER - self.RANGE_LOWER
        self.DANGER_LOWER = self.RANGE_LOWER - self.RANGE
        self.DANGER_UPPER = self.RANGE_UPPER + self.RANGE
        self.FLOOR = self.RANGE_LOWER - self.RANGE * 2     # Absolute min
        self.CEILING = self.RANGE_UPPER + self.RANGE * 2   # Absolute max

    def _validate(self):
        """Ensure subclass attributes are set correctly."""
        err = []
        for attr in self.REQUIRED_ATTRIBUTES:
            if getattr(self, attr, None) is None:
                err.append(attr)
        if err:
            raise AttributeError(
                f"Analog interface subclass missing required attributes:\n- "
                + '\n- '.join(err)
                + '\n\n' + __doc__
            )

    def _setup(self):
        """Create interface to MCP3008 chip."""
        if config.DEVMODE:
            logger.warning("DEVMODE: configure sensor with spoofed ADC")
            return
        self.mcp = MCP3008(
            cs=config.PIN_CS,
            miso=config.PIN_MISO,
            mosi=config.PIN_MOSI,
            clk=config.PIN_CLK,
        )

    def get_value(self, as_volts=False):
        """Calculate current channel reading."""
        if config.DEVMODE:
            if as_volts:
                range = (self.MAX_VOLTS - self.MIN_VOLTS) * 0.25
                return random.uniform(
                    self.MIN_VOLTS + range,
                    self.MAX_VOLTS - range)
            return random.uniform(self.DANGER_LOWER, self.DANGER_UPPER)

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
        if as_volts:
            return volts_offset
        return self._volts_to_units(volts_offset)

    def _volts_to_units(self, v):
        """Calculate units from analog voltage."""
        logger.debug("Calculate volts to units from default equation")
        ref_range = self.MAX_VOLTS - self.MIN_VOLTS
        fraction = (v - self.MIN_VOLTS) / ref_range
        if self.INVERSE:
            logger.debug("Calculate units against inverse voltage")
            fraction = 1 - fraction
        return self.read_transform(fraction * self.MAX_UNITS)

    def read(self, n=None):
        """Return channel reading."""
        n = n or self.DEFAULT_MEDIAN_SAMPLES
        if n > 1:
            r = self._read_median(n)
        else:
            r = self.get_value()
        rounded = round(r, self.DECIMAL_POINTS)
        logger.info(
            f"{type(self).__name__}"
            f" READ: {rounded}{self.UNIT} (n={n})")
        return(rounded)

    def read_transform(self, value):
        """Override this method to adjust reading e.g. temp correction."""
        return value

    def _read_median(self, n):
        """Return median channel reading from <n> samples."""
        readings = []
        for i in range(n):
            readings.append(self.get_value(as_volts=True))
            time.sleep(self.MEDIAN_INTERVAL_SECONDS)
        volts = statistics.median(readings)
        logger.debug(f"Median volts (n={n}): {volts}")
        return self._volts_to_units(volts)

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
        current = sensor.read(n=cls.DEFAULT_MEDIAN_SAMPLES)

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
        logger.info(f"Testing {type(self).__name__} analog sensor...")
        logger.info("~~~~~~ Press CTRL+C to end test ~~~~~~")
        time.sleep(1)
        while True:
            logger.info(f"READING: {self.read()}{self.UNIT}")
            time.sleep(0.5)
