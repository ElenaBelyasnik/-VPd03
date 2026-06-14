# Промпт для создания погодного приложения

## Исходный запрос

Создай Python приложение для получения прогноза погоды с использованием API.

## Требования

### Функциональность

1. **Получение погоды по координатам**
   - Функция `get_weather_by_coordinates(latitude, longitude)`
   - Использование Yandex Weather API
   - Заголовки: `X-Yandex-Weather-Key`
   - Базовый URL: `https://api.weather.yandex.ru/v2/forecast`

2. **Получение погоды по названию города**
   - Функция `get_coordinates(city)` — геокодирование через OpenStreetMap Nominatim
   - URL: `https://nominatim.openstreetmap.org/search?q={city}&format=json`
   - Возвращает lat и lon первого результата
   - Затем вызывается `get_weather_by_coordinates(lat, lon)`

3. **Сохранение данных**
   - Сохранение JSON ответа в `weather.json`
   - Функция `save_weather_to_file(weather_data, filename)`

4. **Отображение данных**
   - Чтение из `weather.json`
   - Красивое форматирование с цветами (библиотека `colorama`)
   - Вывод: температура, влажность, давление, ветер, прогноз на день

5. **Интерактивное меню**
   - Цикл с опциями:
     1. По названию города
     2. По координатам
     3. Выход

6. **Кэширование**
   - Сохранение данных в `weather_cache.json` с меткой времени
   - При сетевых ошибках — проверка кэша (< 3 часов)
   - Показ данных из кэша если он свежий

7. **Повторные запросы (Retry)**
   - При ошибке 429 или сетевых ошибках — до 3 повторов
   - Экспоненциальная задержка: 1с, 2с, 4с

### Структура проекта

```
weather_app/
├── weather_app.py        # Основной файл с API запросами
├── weather_info.py       # Модуль для красивого вывода
├── weather.json          # Текущие данные о погоде
├── weather_cache.json    # Кэш данных
├── requirements.txt      # Зависимости
├── .env                  # API ключ (не коммитится!)
├── .gitignore
└── README.md
```

### Зависимости

```
requests==2.34.2
python-dotenv==1.2.2
colorama==0.4.6
```

### Настройка

1. Создать `.env` с `API_KEY=<ваш_ключ_яндекс_погоды>`
2. `.gitignore` должен включать `.env` и `venv/`

### Команды запуска

```powershell
python weather_app.py           # Интерактивное меню
python weather_info.py          # Показать из файла
python weather_app.py --city Москва
```

## Примечания

- Если OpenWeatherMap или WeatherAPI недоступны, использовать Yandex Weather API
- Геокодинг через OpenStreetMap Nominatim (бесплатный, без ключа)
- Все сообщения на русском языке
- Цветной вывод через colorama
