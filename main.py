import argparse
import json
import sys

from clients.errors import NotFoundError, ServiceUnavailableError
from processing.service import build_city_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Сводка погоды и курса валют по городу"
    )
    parser.add_argument(
        "--city", required=True, help="Название города (например, Moscow)"
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="ISO-код валюты (по умолчанию USD)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Вывести результат в формате JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.city.strip():
        print("Ошибка: название города не может быть пустым", file=sys.stderr)
        sys.exit(2)

    try:
        summary = build_city_summary(city=args.city, currency=args.currency)
    except NotFoundError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        sys.exit(3)
    except ServiceUnavailableError as exc:
        print(f"Сервис недоступен: {exc}", file=sys.stderr)
        sys.exit(4)

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        sys.exit(0)

    weather = summary["weather"]
    rates = summary["rates"]
    warm_text = "да" if weather["warm_clothes"] else "нет"
    expensive_text = "да" if rates["expensive"] else "нет"

    print(f"Город: {summary['city']}")
    print(f"Погода: {weather['temp_c']}°C, {weather['description']}")
    print(f"Тёплая одежда: {warm_text}")
    print(f"{rates['currency']}→RUB: {rates['rate_to_rub']}")
    print(f"Дорогой курс: {expensive_text}")
    sys.exit(0)


if __name__ == "__main__":
    main()
