from typing import Any


def preprocess_weather(raw_weather: dict[str, Any]) -> dict[str, Any]:
    temp_c = float(raw_weather["temp_c"])
    raw_desc = str(raw_weather.get("description", "")).strip()
    description = raw_desc if raw_desc else "unknown conditions"
    warm_clothes = temp_c < 0

    return {
        "temp_c": temp_c,
        "description": description,
        "warm_clothes": warm_clothes,
    }


def preprocess_rate(currency: str, rate_to_rub: float) -> dict[str, Any]:
    expensive = rate_to_rub > 100.0
    return {
        "currency": currency.upper(),
        "rate_to_rub": round(rate_to_rub, 2),
        "expensive": expensive,
    }
