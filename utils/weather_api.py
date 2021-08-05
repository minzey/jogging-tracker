import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from django.conf import settings

class WeatherAPI:

    APIKEY = settings.WEATHER_API_ACCESS_KEY
    BASE_URL = "http://api.weatherapi.com/v1/history.json"

    def __init__(self, location, date):
        """
        Args:
            location: Accepts valid city names (eg. New York), lat-long (eg. 40.714,-74.006), and US/UK/Canada zipcode
            (eg. 10001)
            date: Accepted format yyyy-mm-dd
        """
        self.location = location
        self.date = date

    def get_weather_conditions(self):
        """
        Returns the weather condition as text
        """

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        http = requests.Session()
        http.mount("http://", HTTPAdapter(max_retries=retry_strategy))

        query_params = {
            "key": self.APIKEY,
            "q": self.location,
            "dt": self.date,
            "hour": 0  # returns weather condition for 0th hour of the day too
        }

        try:
            api_result = http.get(self.BASE_URL, params=query_params, timeout=2)
            api_result.raise_for_status()
            api_response = api_result.json()
            return api_response["forecast"]["forecastday"][0]["day"]["condition"]["text"]
        except Exception as e:
            return "Unknown"



