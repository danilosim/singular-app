from datetime import datetime

import click

from weather_app.services.cities import CityService
from weather_app.services.weather import WeatherService


@click.command()
@click.option(
    "--use-api", is_flag=True, help="Use API to fetch city data instead of constants"
)
@click.option(
    "--city", "-c", multiple=True, help="List of cities to get weather for", default=[]
)
def main(use_api, city):
    """
    Fetch and display current weather information for specified cities.

    Args:
        use_api (bool): If True, fetch city data from API instead of constants
        city (tuple): Optional list of city names to get weather for

    Raises:
        ConnectionError: If API requests fail
        ValueError: If invalid city names or data formats are provided
        OSError: If there are issues writing output files
    """
    try:
        # Initialize services
        weather_service = WeatherService()
        city_service = CityService()

        # Get cities based on flag
        try:
            if use_api or city:
                cities = city_service.get_cities_from_api(city)
            else:
                cities = city_service.get_cities_from_constants()

            if not cities:
                raise ValueError("No valid cities found to process")

        except (ConnectionError, ValueError) as e:
            click.echo(f"Error getting city data: {str(e)}", err=True)
            raise

        # Get weather for all cities
        try:
            weather_data = weather_service.get_weather_for_cities(cities)
        except Exception as e:
            click.echo(f"Error fetching weather data: {str(e)}", err=True)
            raise

        # Display weather information in console
        click.echo("\nCurrent Weather Information:")
        click.echo("-" * 80)
        for _, row in weather_data.iterrows():
            click.echo(f"\nCity: {row['city']}")
            click.echo(
                f"Temperature: {row['temperature_c']:.1f}°C ({row['temperature_f']:.1f}°F)"
            )
            click.echo(f"Humidity: {row['humidity']}%")
            click.echo(
                f"Wind Speed: {row['wind_speed_kph']:.1f} km/h ({row['wind_speed_mph']:.1f} mph)"
            )
            click.echo(f"Time: {row['time']} {row['timezone']}")
        click.echo("\n" + "-" * 80)

        # Get current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure data directory exists
        import os

        os.makedirs("data", exist_ok=True)

        try:
            # Save complete dataset
            weather_data.to_csv("data/weather_data.csv", index=False)

            # Save top 5 hottest cities
            df_hot = weather_data.nlargest(5, "temperature_c")
            df_hot.to_csv(f"data/weather_data_{timestamp}_top5_temp.csv", index=False)

            # Save all cities ranked by wind speed
            df_wind = weather_data.sort_values("wind_speed_kph")
            df_wind.to_csv(
                f"data/weather_data_{timestamp}_wind_ranked.csv", index=False
            )

        except OSError as e:
            click.echo(f"Error saving output files: {str(e)}", err=True)
            raise

    except Exception as e:
        click.echo(f"An unexpected error occurred: {str(e)}", err=True)
        raise


if __name__ == "__main__":
    main()
