import time

from clients.errors import NotFoundError, ServiceUnavailableError
from clients.http import fetch_json

FRANKFURTER_URL = "https://api.frankfurter.dev/v2/rate/{currency}/RUB"
CACHE_TTL_SECONDS = 300

_rates_cache: dict[str, tuple[float, float]] = {}


def get_rate(currency: str) -> float:
    code = currency.strip().upper()
    if len(code) != 3 or not code.isalpha():
        raise NotFoundError(f"Invalid currency code: {currency}")

    now = time.monotonic()
    if code in _rates_cache:
        cached_rate, cached_at = _rates_cache[code]
        if now - cached_at < CACHE_TTL_SECONDS:
            return cached_rate

    url = FRANKFURTER_URL.format(currency=code)
    data = fetch_json(url)

    if not isinstance(data, dict) or "rate" not in data:
        raise ServiceUnavailableError("Unexpected response format from rates API")

    rate = data["rate"]
    if not isinstance(rate, (int, float)):
        raise ServiceUnavailableError("Invalid rate value in response")

    result = float(rate)
    _rates_cache[code] = (result, now)
    return result
