import io
from typing import Optional

import matplotlib.pyplot as plt
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from fastapi.responses import FileResponse

from weather_app.models import City, Weather
from weather_app.services.cities import CityService
from weather_app.services.weather import WeatherService

app = FastAPI()
weather_service = WeatherService()
city_service = CityService()


@app.get(
    "/weather/visualization",
    responses={
        200: {"description": "Returns a PNG image with weather visualization plots"},
        404: {"description": "Weather data file not found"},
        500: {"description": "Error generating visualization"},
    },
)
async def get_weather_visualization(background_tasks: BackgroundTasks):
    """
    Generate visualization plots for weather data showing temperature, humidity and wind speed by city.

    Args:
        background_tasks: FastAPI BackgroundTasks for cleanup

    Returns:
        Response: PNG image containing the visualization plots

    Raises:
        HTTPException: If weather data file is not found or error occurs during visualization
    """
    try:
        weather_data = weather_service.get_weather_from_csv("data/weather_data.csv")

        if weather_data.empty:
            raise ValueError("No weather data available")

        # Create subplots
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15))

            # Temperature plot
            ax1.bar(weather_data["city"], weather_data["temperature_c"])
            ax1.set_title("Temperature by City")
            ax1.set_xlabel("City")
            ax1.set_ylabel("Temperature (°C)")
            ax1.tick_params(axis="x", rotation=45)

            # Humidity plot
            ax2.bar(weather_data["city"], weather_data["humidity"])
            ax2.set_title("Humidity by City")
            ax2.set_xlabel("City")
            ax2.set_ylabel("Humidity (%)")
            ax2.tick_params(axis="x", rotation=45)

            # Wind speed plot
            ax3.bar(weather_data["city"], weather_data["wind_speed_kph"])
            ax3.set_title("Wind Speed by City")
            ax3.set_xlabel("City")
            ax3.set_ylabel("Wind Speed (km/h)")
            ax3.tick_params(axis="x", rotation=45)

            plt.tight_layout()

            # Save plot to bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            plt.close()

            background_tasks.add_task(buf.close)

            headers = {
                "Content-Disposition": 'inline; filename="weather_visualization.png"'
            }

            return Response(buf.getvalue(), headers=headers, media_type="image/png")

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating visualization: {str(e)}"
            )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Weather data file not found")
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing weather data: {str(e)}"
        )


@app.get("/weather/{city}")
async def get_all_weather(city: str, sort_by: Optional[str] = None):
    """
    Get weather data for a single city or all predefined cities.

    Args:
        city (str): City name or "all" to get data for all predefined cities
        sort_by (Optional[str]): Sort results by temperature or wind speed.
            Valid values: "temperature", "-temperature", "wind_speed", "-wind_speed"

    Returns:
        List[Weather]: List of Weather objects containing weather data

    Raises:
        HTTPException:
            - 404 if specified city not found
            - 400 if invalid sort parameter
            - 500 if error fetching weather data
    """
    try:
        if city == "all":
            cities = city_service.get_cities_from_constants()
            weather_df = weather_service.get_weather_for_cities(cities)

            # Sort data if requested
            if sort_by:
                valid_sort_params = {
                    "temperature": ("temperature_c", True),
                    "-temperature": ("temperature_c", False),
                    "wind_speed": ("wind_speed_kph", True),
                    "-wind_speed": ("wind_speed_kph", False),
                }

                if sort_by not in valid_sort_params:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid sort parameter. Must be one of: {', '.join(valid_sort_params.keys())}",
                    )

                column, ascending = valid_sort_params[sort_by]
                weather_df = weather_df.sort_values(column, ascending=ascending)
        else:
            cities = city_service.get_cities_from_api([city])
            if not cities:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found")

            weather_df = weather_service.get_weather_for_cities(cities)

        # Convert DataFrame rows to Weather objects
        try:
            weather_data = [
                Weather(
                    city=City(
                        name=row["city"],
                        latitude=str(row["latitude"]),
                        longitude=str(row["longitude"]),
                    ),
                    timezone=row["timezone"],
                    time=row["time"],
                    temperature_c=row["temperature_c"],
                    humidity=row["humidity"],
                    wind_speed_kph=row["wind_speed_kph"],
                )
                for _, row in weather_df.iterrows()
            ]
        except KeyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Missing required field in weather data: {str(e)}",
            )

        return weather_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching weather data: {str(e)}"
        )


@app.get("/weather/download/csv")
async def download_weather_csv():
    """
    Download the weather data as a CSV file.

    Returns:
        FileResponse: CSV file containing weather data

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 500 if error reading file
    """
    try:
        return FileResponse(
            "data/weather_data.csv",
            media_type="text/csv",
            filename="weather_data.csv",  # Use just filename without path
            headers={"Content-Disposition": "attachment"},  # Force download
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Weather data CSV file not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading weather data file: {str(e)}"
        )
