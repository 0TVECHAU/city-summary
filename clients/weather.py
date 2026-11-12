from typing import Any

from clients.errors import NotFoundError, ServiceUnavailableError
from clients.http import fetch_json

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    95: "thunderstorm",
}


def get_weather(city: str) -> dict[str, Any]:
    geo_data = fetch_json(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
    )
    if not isinstance(geo_data, dict):
        raise ServiceUnavailableError("Unexpected geocoding response format")

    results = geo_data.get("results")
    if not results or not isinstance(results, list):
        raise NotFoundError(f"City '{city}' not found")

    location = results[0]
    lat = location.get("latitude")
    lon = location.get("longitude")
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        raise ServiceUnavailableError("Missing coordinates in geocoding response")

    weather_data = fetch_json(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
        },
    )
    if not isinstance(weather_data, dict) or "current" not in weather_data:
        raise ServiceUnavailableError("Missing 'current' block in weather response")

    current = weather_data["current"]
    temp = current.get("temperature_2m")
    code = current.get("weather_code")

    if not isinstance(temp, (int, float)):
        raise ServiceUnavailableError("Invalid temperature in weather response")

    description = WEATHER_CODES.get(code, "") if isinstance(code, int) else ""

    return {
        "temp_c": float(temp),
        "description": description,
    }
