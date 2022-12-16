"""Not really a sensor, but getting atmospheric pressure from an API."""

import requests
from hydropi.config import config
from hydropi.process.errors import catchme


class WeatherAPI:
    """Read ambient pressure from a weather API."""

    BASE_URL = "https://api.weatherapi.com/v1/current.json"
    CITY = "Mooloolaba"

    def __init__(self):
        self.API_KEY = config.WEATHER_API_KEY

    @catchme
    def get_ambient_pressure_hpa(self):
        """Return current pressure in hPa."""
        r = requests.get(self.BASE_URL, params={
            'key': self.API_KEY,
            'q': self.CITY,
        })
        try:
            return r.json()['current']['pressure_mb']
        except KeyError:
            raise KeyError(
                'Key "pressure_mb" not found in weather API response')
