from typing import Any

from clients.rates import get_rate
from clients.weather import get_weather
from processing.preprocessing import preprocess_rate, preprocess_weather


def build_city_summary(city: str, currency: str = "USD") -> dict[str, Any]:
    clean_city = city.strip()
    clean_currency = currency.strip().upper()

    raw_weather = get_weather(clean_city)
    raw_rate = get_rate(clean_currency)

    return {
        "city": clean_city,
        "weather": preprocess_weather(raw_weather),
        "rates": preprocess_rate(clean_currency, raw_rate),
    }
