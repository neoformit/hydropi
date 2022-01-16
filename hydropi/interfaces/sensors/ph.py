"""Interface for reading nutrient pH level."""

import os
import time
import json
import logging

from hydropi.config import config
from .analog import AnalogInterface

logger = logging.getLogger('hydropi')


class PHSensor(AnalogInterface):
    """Interface for analog pressure sensor.

    Call .read() to get current pressure.
    """

    CHANNEL = config.CHANNEL_PH
    TEXT = 'pH'
    UNIT = ''
    MIN_UNITS = 1.351
    MAX_UNITS = 12
    MIN_VOLTS = 1.8857
    MAX_VOLTS = 3.3
    INVERSE = True
    RANGE_LOWER = config.PH_MIN
    RANGE_UPPER = config.PH_MAX
    DECIMAL_POINTS = 2
    DEFAULT_MEDIAN_SAMPLES = 200

    # Calibration
    CALIBRATE_REPLICATES = 5
    CALIBRATE_INTERVAL_SECONDS = 2
    CALIBRATE_TOLERANCE = 0.002  # volts
    CALIBRATE_STANDARDS = (4.0, 6.86)
    CALIBRATION_CONFIGFILE = os.path.join(
        config.CONFIG_DIR,
        'calibration/ph/coefficients.json')

    # Default linear equation coefficients
    M = -7.53323
    C = 26.1926

    def __init__(self):
        """Initialize pH sensor."""
        # Linear equation coefficients
        super().__init__()
        self.M, self.C = self._get_coefficients()

    def _volts_to_units(self, v):
        """Override units calculation with linear equation."""
        return self.M * v + self.C

    def calibrate(self):
        """Calibrate the sensor with standard solutions (pH 4.0 & 6.86).

        This requires interaction with the user to place the probe in the
        different solutions.
        """
        data = {}
        for std in self.CALIBRATE_STANDARDS:
            input(
                f"Place sensor in pH {std} standard,"
                " then hit ENTER to continue.")
            data[std] = self.take_calibration_reading(std)

        self._set_new_calibration(data)
        logger.info(
            "Calibration complete. Return the sensor to the nutrient tank.")

    def take_calibration_reading(self, standard):
        """Wait for sensor to settle and take a reading."""
        readings = [self.get_value(as_volts=True)]
        while True:
            time.sleep(self.CALIBRATE_INTERVAL_SECONDS)
            readings.append(self.get_value(as_volts=True))
            logger.info(f"CALIBRATE pH {standard}: Read {readings[-1]}")
            if len(readings) < self.CALIBRATE_REPLICATES:
                continue
            variance = max(readings[-5:]) - min(readings[-5:])
            if variance > self.CALIBRATE_TOLERANCE:
                continue
            return readings[-1]

    def _set_new_calibration(self, data):
        """Calculate and set new coefficients for pH reading equation."""
        y = tuple(data.keys())
        x = (data[y[0]], data[y[1]])
        M = (y[1] - y[0]) / (x[1] - x[0])
        C = -1 * M * x[0] + y[0]
        data = {
            "M": M,
            "C": C,
        }
        self.M, self.C = M, C

        config_dir = os.path.dirname(self.CALIBRATION_CONFIGFILE)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(self.CALIBRATION_CONFIGFILE, 'w') as f:
            json.dump(data, f)

    def _get_coefficients(self):
        """Read calibrated equation coefficients from file."""
        if not os.path.exists(self.CALIBRATION_CONFIGFILE):
            logger.warning(
                'Using default pH coefficients - consider calibrating.')
            return self.M, self.C
        try:
            with open(self.CALIBRATION_CONFIGFILE) as f:
                data = json.load(f)
            return data['M'], data['C']
        except Exception:
            logger.warning("Error loading pH calibration - removing file")
            os.remove(self.CALIBRATION_CONFIGFILE)
            return self._get_coefficients()
