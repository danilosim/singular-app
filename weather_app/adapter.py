from typing import List

import requests

from weather_app.constants import WEATHER_VARS


class OpenMeteoAPIAdapter:
    """Adapter class for interacting with the Open-Meteo weather and geocoding APIs"""

    def get_city_lat_long(self, city: str) -> dict:
        """
        Get latitude and longitude coordinates for a city name.

        Args:
            city (str): Name of the city to look up

        Returns:
            dict: JSON response containing city coordinates and metadata

        Raises:
            ConnectionError: If the API request fails
            ValueError: If the API returns an invalid response
        """
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to geocoding API: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from geocoding API: {str(e)}")

    def get_weather(self, lat: List[float], long: List[float]) -> List[dict]:
        """
        Get current weather data for multiple cities simultaneously.

        Args:
            lat (List[float]): List of latitude coordinates
            long (List[float]): List of longitude coordinates

        Returns:
            List[dict]: List of weather data dictionaries for each location

        Raises:
            ConnectionError: If the API request fails
            ValueError: If the API returns an invalid response
            TypeError: If input coordinates are not in the correct format
        """
        if not lat or not long or len(lat) != len(long):
            raise ValueError(
                "Must provide matching lists of latitude and longitude coordinates"
            )

        try:
            lat_str = ",".join(str(x) for x in lat)
            long_str = ",".join(str(x) for x in long)
        except TypeError:
            raise TypeError("Coordinates must be numeric values")

        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat_str}"
            f"&longitude={long_str}&current={','.join(WEATHER_VARS)}"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Ensure response is always returned as a list
            if not isinstance(data, list):
                data = [data]
            return data

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to weather API: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid JSON response from weather API: {str(e)}")
