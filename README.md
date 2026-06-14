# Погодное приложение с Yandex Weather API

Приложение для получения и отображения погоды по названию города или координатам.

## Файлы проекта

- `weather_app.py` — основной модуль для получения погоды
- `weather_info.py` — модуль для красивого отображения погоды в консоли
- `weather.json` — файл с данными о погоде (создаётся автоматически)
- `.env` — файл с API ключом (не коммитится!)
- `requirements.txt` — зависимости проекта

## Установка

1. Создайте виртуальное окружение:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Установите зависимости:
```powershell
pip install -r requirements.txt
```

3. Создайте файл `.env` с вашим API ключом:
```
API_KEY=d61883e2-b104-413e-96d8-25ac3c1a55c4
```

## Использование

### Получить погоду и сохранить в файл:
```powershell
python weather_app.py
```

### Получить погоду для конкретного города:
```powershell
python weather_app.py --city Москва
python weather_app.py --city "Санкт-Петербург"
python weather_app.py --city Казань
```

### Красиво отобразить погоду из файла:
```powershell
python weather_app.py --read
python weather_info.py
```

## Функции

### weather_app.py
- `get_coordinates(city)` — получает координаты города через Nominatim API
- `get_weather_by_coordinates(lat, lon)` — получает погоду от Yandex Weather API
- `get_current_weather(city=None, latitude=None, longitude=None)` — универсальный запрос погоды
- `save_weather_to_file(weather_data, filename)` — сохраняет погоду в JSON файл

### weather_info.py
- `read_weather_from_file(filename)` — читает погоду из JSON файла
- `print_weather_summary(weather)` — отображает погоду в красивом формате с цветами

## Цветовая схема (colorama)

- Заголовки — Cyan
- Подписи полей — Yellow
- Значения — White, Green, Blue, Cyan
- Разделители — Magenta
- Ошибки — Red
