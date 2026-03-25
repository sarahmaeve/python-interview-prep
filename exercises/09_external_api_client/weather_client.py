"""
WeatherClient -- fetches weather data from an external API.

This module contains 3 bugs. Run the tests to find them:

    python3 -m unittest test_weather_client

Fix the bugs until all tests pass. Do not modify the test file.
"""

import json
from urllib.request import urlopen
from urllib.error import URLError


class WeatherClient:
    def __init__(self, base_url="http://api.weather.example.com"):
        self.base_url = base_url

    def get_temperature(self, city):
        """Fetch the current temperature for *city* and return it as a float."""
        url = f"{self.base_url}/temperature?city={city}"
        with urlopen(url) as response:
            data = json.loads(response.read())
        # BUG 1: wrong key -- API returns "temp", not "temperature"
        return float(data["main"]["temperature"])

    def get_forecast(self, city, days=5):
        """Return a list of daily temperatures for the next *days* days."""
        # BUG 3: city is not URL-encoded, so "New York" creates an invalid URL
        url = f"{self.base_url}/forecast?city={city}&days={days}"
        with urlopen(url) as response:
            data = json.loads(response.read())
        return [float(day["temp"]) for day in data["forecast"]]

    def get_temperature_with_retry(self, city, retries=3):
        """Like get_temperature, but retries up to *retries* times on URLError."""
        for attempt in range(retries):
            try:
                return self.get_temperature(city)
            except URLError:
                # BUG 2: off-by-one -- should be `retries - 1`, not `retries`
                if attempt == retries:
                    raise
