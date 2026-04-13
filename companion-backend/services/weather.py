import os
import httpx
import logging

logger = logging.getLogger(__name__)

WMO_DESCRIPTIONS = {
    0: "clear skies",
    1: "partly cloudy skies",
    2: "partly cloudy skies",
    3: "partly cloudy skies",
    45: "foggy conditions",
    48: "foggy conditions",
    51: "light drizzle",
    53: "light drizzle",
    55: "light drizzle",
    61: "rain",
    63: "rain",
    65: "rain",
    71: "snow",
    73: "snow",
    75: "snow",
    80: "rain showers",
    81: "rain showers",
    82: "rain showers",
    95: "thunderstorms",
}


def get_weather_description_for_code(code):
    return WMO_DESCRIPTIONS.get(code, "mixed conditions")


async def get_weather_description(lat=None, lon=None):
    if lat is None:
        lat = os.environ.get("JOHN_LAT", "53.8317")
    if lon is None:
        lon = os.environ.get("JOHN_LON", "-2.2340")

    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        logger.warning("Invalid lat/lon values, using defaults")
        lat = 53.8317
        lon = -2.2340

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Europe/London",
        "forecast_days": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        daily = data.get("daily", {})
        weather_code = daily.get("weathercode", [None])[0] if daily.get("weathercode") else None
        temp_max = daily.get("temperature_2m_max", [None])[0] if daily.get("temperature_2m_max") else None
        temp_min = daily.get("temperature_2m_min", [None])[0] if daily.get("temperature_2m_min") else None
        precip = daily.get("precipitation_probability_max", [None])[0] if daily.get("precipitation_probability_max") else None

        if weather_code is None:
            return "The weather forecast is not available just now."

        description = get_weather_description_for_code(weather_code)

        if temp_max is not None and temp_min is not None:
            temp_str = "around {} degrees".format(int(round((temp_max + temp_min) / 2)))
        elif temp_max is not None:
            temp_str = "around {} degrees".format(int(round(temp_max)))
        else:
            temp_str = "temperatures to be confirmed"

        if precip is not None and precip > 20:
            precip_str = "with a {} percent chance of rain".format(int(precip))
        else:
            precip_str = ""

        if description and temp_str:
            if precip_str:
                return "It is going to be {} with temperatures {}, {}.".format(description, temp_str, precip_str)
            return "It is going to be {} with temperatures {}.".format(description, temp_str)
        elif description:
            return "It is going to be {}.".format(description)
        else:
            return "The weather forecast is not available just now."

    except Exception as e:
        logger.error("Error fetching weather: {}".format(e))
        return "The weather forecast is not available just now."