from datetime import datetime
from unittest.mock import Mock

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from weather_app.models import City
from weather_app.services.weather import WeatherService


@pytest.fixture
def weather_service():
    return WeatherService()


@pytest.fixture
def sample_cities():
    return [
        City(name="London", latitude="51.5074", longitude="-0.1278"),
        City(name="Paris", latitude="48.8566", longitude="2.3522"),
    ]


@pytest.fixture
def sample_weather_response():
    return [
        {
            "timezone": "Europe/London",
            "current": {
                "time": "2024-01-01T12:00:00",
                "temperature_2m": 20.5,
                "relative_humidity_2m": 65,
                "wind_speed_10m": 10.0,
            },
        },
        {
            "timezone": "Europe/Paris",
            "current": {
                "time": "2024-01-01T13:00:00",
                "temperature_2m": 22.0,
                "relative_humidity_2m": 70,
                "wind_speed_10m": 12.0,
            },
        },
    ]


@pytest.fixture
def sample_csv_data():
    return pd.DataFrame(
        {"city": ["London"], "temperature_c": [20.5], "wind_speed_kph": [10.0]}
    )


class TestWeatherService:
    def test_get_weather_for_cities_success(
        self, weather_service, sample_cities, sample_weather_response
    ):
        # Mock the API adapter
        weather_service.adapter.get_weather = Mock(return_value=sample_weather_response)

        result = weather_service.get_weather_for_cities(sample_cities)

        expected_df = pd.DataFrame(
            {
                "city": ["London", "Paris"],
                "latitude": ["51.5074", "48.8566"],
                "longitude": ["-0.1278", "2.3522"],
                "timezone": ["Europe/London", "Europe/Paris"],
                "time": [
                    datetime.fromisoformat("2024-01-01T12:00:00"),
                    datetime.fromisoformat("2024-01-01T13:00:00"),
                ],
                "temperature_c": [20.5, 22.0],
                "humidity": [65, 70],
                "wind_speed_kph": [10.0, 12.0],
                "temperature_f": [68.9, 71.6],
                "wind_speed_mph": [6.21371, 7.456452],
            }
        )

        assert_frame_equal(result, expected_df)

    def test_get_weather_for_cities_empty_list(self, weather_service):
        with pytest.raises(ValueError, match="Cities list cannot be empty"):
            weather_service.get_weather_for_cities([])

    def test_get_weather_for_cities_invalid_coordinates(self, weather_service):
        invalid_cities = [City(name="Invalid", latitude="invalid", longitude="0.0")]

        with pytest.raises(ValueError, match="Invalid coordinate value"):
            weather_service.get_weather_for_cities(invalid_cities)

    def test_get_weather_for_cities_missing_field(self, weather_service, sample_cities):
        invalid_response = [{"current": {}}]  # Missing required fields
        weather_service.adapter.get_weather = Mock(return_value=invalid_response)

        with pytest.raises(KeyError, match="Missing required field in weather data"):
            weather_service.get_weather_for_cities(sample_cities)

    def test_get_weather_from_csv_success(
        self, weather_service, sample_csv_data, tmp_path
    ):
        # Create a temporary CSV file
        csv_path = tmp_path / "weather_data.csv"
        sample_csv_data.to_csv(csv_path, index=False)

        result = weather_service.get_weather_from_csv(str(csv_path))
        assert_frame_equal(result, sample_csv_data)

    def test_get_weather_from_csv_file_not_found(self, weather_service):
        with pytest.raises(FileNotFoundError, match="Weather data file not found"):
            weather_service.get_weather_from_csv("nonexistent.csv")

    def test_get_weather_from_csv_empty_file(self, weather_service, tmp_path):
        # Create an empty CSV file
        csv_path = tmp_path / "empty.csv"
        pd.DataFrame().to_csv(csv_path, index=False)

        with pytest.raises(
            pd.errors.EmptyDataError,
            match="Error reading CSV: No columns to parse from file",
        ):
            weather_service.get_weather_from_csv(str(csv_path))

    def test_add_imperial_units(self, weather_service):
        input_df = pd.DataFrame({"temperature_c": [0, 100], "wind_speed_kph": [1, 10]})

        result = weather_service._add_imperial_units(input_df)

        expected_df = pd.DataFrame(
            {
                "temperature_c": [0, 100],
                "wind_speed_kph": [1, 10],
                "temperature_f": [32.0, 212.0],
                "wind_speed_mph": [0.621371, 6.21371],
            }
        )

        assert_frame_equal(result, expected_df)

    def test_add_imperial_units_missing_columns(self, weather_service):
        input_df = pd.DataFrame({"other_column": [1, 2]})

        with pytest.raises(KeyError, match="Missing required metric column"):
            weather_service._add_imperial_units(input_df)
