# City Summary

CLI-утилита для получения текущей погоды и курса валюты к рублю по выбранному городу.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
python main.py --city Moscow
python main.py --city Moscow --currency EUR
python main.py --city Moscow --json
```

## Тесты

```bash
python -m unittest discover -s tests
```
