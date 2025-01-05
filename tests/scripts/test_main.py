from unittest.mock import Mock, patch

import pandas as pd
import pytest
from click.testing import CliRunner

from scripts.weather.main import main


@pytest.fixture
def mock_services():
    """Fixture to mock WeatherService and CityService"""
    with (
        patch("scripts.weather.main.WeatherService") as mock_weather_service,
        patch("scripts.weather.main.CityService") as mock_city_service,
    ):
        # Create service instances
        weather_service_instance = Mock()
        city_service_instance = Mock()

        # Configure mock returns
        mock_weather_service.return_value = weather_service_instance
        mock_city_service.return_value = city_service_instance

        yield {
            "weather_service": weather_service_instance,
            "city_service": city_service_instance,
        }


@pytest.fixture
def sample_weather_data():
    """Fixture providing sample weather data DataFrame"""
    return pd.DataFrame(
        {
            "city": ["London", "Paris"],
            "temperature_c": [20.5, 22.0],
            "temperature_f": [68.9, 71.6],
            "humidity": [65, 70],
            "wind_speed_kph": [15.5, 12.0],
            "wind_speed_mph": [9.6, 7.5],
            "time": ["14:00", "15:00"],
            "timezone": ["GMT", "CET"],
        }
    )


class TestScript:
    def test_main_with_constants(self, mock_services, sample_weather_data, tmp_path):
        """Test main command using constant cities"""
        # Configure mocks
        mock_services["city_service"].get_cities_from_constants.return_value = [
            "London",
            "Paris",
        ]
        mock_services[
            "weather_service"
        ].get_weather_for_cities.return_value = sample_weather_data

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, [])

            assert result.exit_code == 0
            assert "Current Weather Information" in result.output
            assert "London" in result.output
            assert "Paris" in result.output

            # Verify service calls
            mock_services["city_service"].get_cities_from_constants.assert_called_once()
            mock_services[
                "weather_service"
            ].get_weather_for_cities.assert_called_once_with(["London", "Paris"])

    def test_main_with_api_cities(self, mock_services, sample_weather_data, tmp_path):
        """Test main command using API cities"""
        mock_services["city_service"].get_cities_from_api.return_value = [
            "London",
            "Paris",
        ]
        mock_services[
            "weather_service"
        ].get_weather_for_cities.return_value = sample_weather_data

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ["--use-api"])

            assert result.exit_code == 0
            mock_services["city_service"].get_cities_from_api.assert_called_once_with(
                ()
            )

    def test_main_with_specific_cities(
        self, mock_services, sample_weather_data, tmp_path
    ):
        """Test main command with specific cities provided"""
        mock_services["city_service"].get_cities_from_api.return_value = ["London"]
        mock_services[
            "weather_service"
        ].get_weather_for_cities.return_value = sample_weather_data

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ["-c", "London"])

            assert result.exit_code == 0
            mock_services["city_service"].get_cities_from_api.assert_called_once_with(
                ("London",)
            )

    def test_main_no_cities_found(self, mock_services, tmp_path):
        """Test main command when no cities are found"""
        mock_services["city_service"].get_cities_from_constants.return_value = []

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, [])

            assert result.exit_code != 0
            assert "No valid cities found to process" in result.output

    def test_main_weather_service_error(self, mock_services, tmp_path):
        """Test main command when weather service fails"""
        mock_services["city_service"].get_cities_from_constants.return_value = [
            "London"
        ]
        mock_services[
            "weather_service"
        ].get_weather_for_cities.side_effect = ConnectionError("API unavailable")

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, [])

            assert result.exit_code != 0
            assert "Error fetching weather data" in result.output
