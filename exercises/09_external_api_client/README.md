# Exercise 09: External API Client

A weather API client that fetches temperatures and forecasts using `urllib.request`. The implementation has **3 bugs** for you to find and fix.

This exercise demonstrates **mocking external APIs** in tests. The test file uses `unittest.mock.patch` to replace `urllib.request.urlopen` so that no real HTTP requests are made. Study the test mocks carefully -- this is one of the most important testing patterns for production Python code.

## How to run the tests

```bash
cd exercises/09_external_api_client
python3 -m unittest test_weather_client
```

Your goal is to edit `weather_client.py` until all tests pass. Do **not** modify the test file.

## Class: WeatherClient

- `__init__(self, base_url="http://api.weather.example.com")` -- configures the API base URL.
- `get_temperature(self, city)` -- fetches the current temperature for a city and returns it as a float.
- `get_forecast(self, city, days=5)` -- fetches a multi-day forecast and returns a list of daily temperatures.
- `get_temperature_with_retry(self, city, retries=3)` -- same as `get_temperature`, but retries up to `retries` times on network errors.

## Hints

<details>
<summary>Hint 1 (gentle)</summary>
Look carefully at the JSON key names the code uses. Do they match what the API actually returns?
</details>

<details>
<summary>Hint 2 (moderate)</summary>
One function builds a URL from user input. What happens when the city name contains a space?
</details>

<details>
<summary>Hint 3 (specific)</summary>

1. `get_temperature` accesses `data["main"]["temperature"]`, but the API returns the key `"temp"`.
2. `get_temperature_with_retry` gives up one attempt too early due to an off-by-one error in the final-attempt check.
3. `get_forecast` does not URL-encode the city name, so cities like "New York" produce an invalid URL.

</details>
