from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class City:
    """
    Represents a city with its geographical coordinates.

    Attributes:
        name (str): The name of the city
        latitude (str): The latitude coordinate of the city
        longitude (str): The longitude coordinate of the city
    """

    name: str
    latitude: str
    longitude: str


@dataclass
class Weather:
    """
    Represents weather data for a specific city at a point in time.

    Attributes:
        city (City): The city this weather data is for
        timezone (str): The timezone of the weather reading
        time (datetime): The timestamp of the weather reading
        temperature_c (float): Temperature in Celsius
        humidity (float): Relative humidity percentage
        wind_speed_kph (float): Wind speed in kilometers per hour
        temperature_f (Optional[float]): Temperature in Fahrenheit, if converted
        wind_speed_mph (Optional[float]): Wind speed in miles per hour, if converted
    """

    city: City
    timezone: str
    time: datetime
    temperature_c: float
    humidity: float
    wind_speed_kph: float
    temperature_f: Optional[float] = None
    wind_speed_mph: Optional[float] = None
