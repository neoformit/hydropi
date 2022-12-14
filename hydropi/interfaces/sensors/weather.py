"""Not really a sensor, but getting atmospheric pressure from an API."""

import requests
# from hydropi.config import config
# from hydropi.process.errors import catchme


class Barometer:
    """Read ambient pressure from a weather API."""


    BASE_URL = "https://api.weatherapi.com/v1/current.json"
    CITY = "Mooloolaba"

    def __init__(self):
        self.API_KEY = 'c79cfeffdf8144bb8a792951221412'  #config.WEATHER_API_KEY

    # @catchme
    def read(self):
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


if __name__ == '__main__':
    b = Barometer()
    print(f"Current pressure at Mooloolaba: {b.read()} hPa")
