from datetime import datetime
from typing import List

import pandas as pd

from weather_app.adapter import OpenMeteoAPIAdapter
from weather_app.models import City


class WeatherService:
    """Service class for retrieving and processing weather data"""

    def __init__(self):
        """Initialize WeatherService with OpenMeteo API adapter"""
        self.adapter = OpenMeteoAPIAdapter()

    def _add_imperial_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add columns for temperature in Fahrenheit and wind speed in mph

        Args:
            df (pd.DataFrame): DataFrame containing weather data with metric units

        Returns:
            pd.DataFrame: DataFrame with added imperial unit columns

        Raises:
            KeyError: If required metric columns are missing
        """
        try:
            df["temperature_f"] = df["temperature_c"] * 9 / 5 + 32
            df["wind_speed_mph"] = df["wind_speed_kph"] * 0.621371
            return df
        except KeyError as e:
            raise KeyError(f"Missing required metric column: {str(e)}")

    def get_weather_for_cities(self, cities: List[City]) -> pd.DataFrame:
        """
        Get current weather data for provided cities

        Args:
            cities (List[City]): List of City objects to get weather for

        Returns:
            pd.DataFrame: DataFrame containing weather data for all cities

        Raises:
            ValueError: If cities list is empty
            KeyError: If weather API response is missing required fields
            Exception: For other errors processing weather data
        """
        if not cities:
            raise ValueError("Cities list cannot be empty")

        # Extract lat/long lists from cities
        try:
            latitudes = [float(city.latitude) for city in cities]
            longitudes = [float(city.longitude) for city in cities]
        except ValueError as e:
            raise ValueError(f"Invalid coordinate value: {str(e)}")

        # Get weather data
        response = self.adapter.get_weather(latitudes, longitudes)

        try:
            # Convert weather data to DataFrame
            df = pd.DataFrame(
                [
                    {
                        "city": cities[i].name,
                        "latitude": cities[i].latitude,
                        "longitude": cities[i].longitude,
                        "timezone": city_weather["timezone"],
                        "time": datetime.fromisoformat(city_weather["current"]["time"]),
                        "temperature_c": city_weather["current"]["temperature_2m"],
                        "humidity": city_weather["current"]["relative_humidity_2m"],
                        "wind_speed_kph": city_weather["current"]["wind_speed_10m"],
                    }
                    for i, city_weather in enumerate(response)
                ]
            )
        except KeyError as e:
            raise KeyError(f"Missing required field in weather data: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing weather data: {str(e)}")

        # Add imperial unit columns
        df = self._add_imperial_units(df)

        return df

    def get_weather_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load weather data from a CSV file

        Args:
            csv_path (str): Path to CSV file containing weather data

        Returns:
            pd.DataFrame: DataFrame containing weather data from CSV

        Raises:
            FileNotFoundError: If CSV file does not exist
            pd.errors.EmptyDataError: If CSV file is empty
            Exception: For other errors reading CSV file
        """
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                raise pd.errors.EmptyDataError("CSV file is empty")
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"Weather data file not found: {csv_path}")
        except pd.errors.EmptyDataError as e:
            raise pd.errors.EmptyDataError(f"Error reading CSV: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing CSV file: {str(e)}")
