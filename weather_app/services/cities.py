from typing import List

from weather_app.adapter import OpenMeteoAPIAdapter
from weather_app.constants import CITIES
from weather_app.models import City


class CityService:
    def __init__(self):
        self.adapter = OpenMeteoAPIAdapter()

    def get_cities_from_constants(self) -> List[City]:
        """
        Creates City models from the predefined CITIES constant

        Returns:
            List[City]: List of City objects created from CITIES constant

        Raises:
            KeyError: If required fields are missing from CITIES constant
        """
        try:
            return [
                City(
                    name=city["City"],
                    latitude=str(city["Latitude"]),
                    longitude=str(city["Longitude"]),
                )
                for city in CITIES
            ]
        except KeyError as e:
            raise KeyError(f"Missing required field in CITIES constant: {str(e)}")

    def get_cities_from_api(self, cities: List[str] = None) -> List[City]:
        """
        Gets city coordinates from the API using city names

        Args:
            cities: Optional list of city names to query. If None, uses CITIES constant.

        Returns:
            List[City]: List of City objects with coordinates from API

        Raises:
            ConnectionError: If API request fails
            ValueError: If API returns invalid data format
        """
        city_results = []
        cities_to_query = cities or [city["City"] for city in CITIES]

        for city in cities_to_query:
            try:
                city_data = self.adapter.get_city_lat_long(city)

                if not isinstance(city_data, dict):
                    raise ValueError(f"Invalid API response format for city: {city}")

                if not city_data.get("results"):
                    continue

                result = city_data["results"][0]

                # Validate required fields exist
                required_fields = ["name", "latitude", "longitude"]
                if not all(field in result for field in required_fields):
                    raise ValueError(
                        f"Missing required fields in API response for city: {city}"
                    )

                city_results.append(
                    City(
                        name=result["name"],
                        latitude=str(result["latitude"]),
                        longitude=str(result["longitude"]),
                    )
                )

            except ConnectionError as e:
                raise ConnectionError(
                    f"Failed to connect to API for city {city}: {str(e)}"
                )
            except Exception as e:
                raise ValueError(f"Error processing city {city}: {str(e)}")

        return city_results
