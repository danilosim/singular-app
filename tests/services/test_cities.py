from unittest.mock import patch

import pytest

from weather_app.models import City
from weather_app.services.cities import CityService


@pytest.fixture
def city_service():
    return CityService()


@pytest.fixture
def mock_cities_constant():
    return [
        {"City": "London", "Latitude": 51.5074, "Longitude": -0.1278},
        {"City": "Paris", "Latitude": 48.8566, "Longitude": 2.3522},
    ]


@pytest.fixture
def mock_api_response():
    return {"results": [{"name": "London", "latitude": 51.5074, "longitude": -0.1278}]}


class TestCityService:
    def test_get_cities_from_constants_success(
        self, city_service, mock_cities_constant
    ):
        with patch("weather_app.services.cities.CITIES", mock_cities_constant):
            cities = city_service.get_cities_from_constants()

            assert len(cities) == 2
            assert isinstance(cities[0], City)
            assert cities[0].name == "London"
            assert cities[0].latitude == "51.5074"
            assert cities[0].longitude == "-0.1278"

    def test_get_cities_from_constants_missing_field(self, city_service):
        invalid_cities = [{"City": "London", "Latitude": 51.5074}]  # Missing Longitude

        with patch("weather_app.services.cities.CITIES", invalid_cities):
            with pytest.raises(KeyError) as exc_info:
                city_service.get_cities_from_constants()
            assert "Longitude" in str(exc_info.value)

    def test_get_cities_from_api_success(self, city_service, mock_api_response):
        with patch.object(
            city_service.adapter, "get_city_lat_long", return_value=mock_api_response
        ):
            cities = city_service.get_cities_from_api(["London"])

            assert len(cities) == 1
            assert isinstance(cities[0], City)
            assert cities[0].name == "London"
            assert cities[0].latitude == "51.5074"
            assert cities[0].longitude == "-0.1278"

    def test_get_cities_from_api_no_results(self, city_service):
        empty_response = {"results": []}

        with patch.object(
            city_service.adapter, "get_city_lat_long", return_value=empty_response
        ):
            cities = city_service.get_cities_from_api(["NonexistentCity"])
            assert len(cities) == 0

    def test_get_cities_from_api_invalid_response(self, city_service):
        invalid_response = "not a dict"

        with patch.object(
            city_service.adapter, "get_city_lat_long", return_value=invalid_response
        ):
            with pytest.raises(ValueError) as exc_info:
                city_service.get_cities_from_api(["London"])
            assert "Invalid API response format" in str(exc_info.value)

    def test_get_cities_from_api_missing_fields(self, city_service):
        invalid_response = {
            "results": [
                {
                    "name": "London",
                    # missing latitude and longitude
                }
            ]
        }

        with patch.object(
            city_service.adapter, "get_city_lat_long", return_value=invalid_response
        ):
            with pytest.raises(ValueError) as exc_info:
                city_service.get_cities_from_api(["London"])
            assert "Missing required fields" in str(exc_info.value)

    def test_get_cities_from_api_connection_error(self, city_service):
        with patch.object(
            city_service.adapter,
            "get_city_lat_long",
            side_effect=ConnectionError("API unavailable"),
        ):
            with pytest.raises(ConnectionError) as exc_info:
                city_service.get_cities_from_api(["London"])
            assert "Failed to connect to API" in str(exc_info.value)
