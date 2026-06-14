import requests
from dotenv import load_dotenv
import os
import json
import time
from datetime import datetime, timedelta

load_dotenv()


def save_to_cache(weather_data: dict, cache_file: str = "weather_cache.json"):
    """Сохраняет данные погоды в кэш с меткой времени"""
    cache = {
        "data": weather_data,
        "timestamp": datetime.now().isoformat()
    }
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def load_from_cache(cache_file: str = "weather_cache.json") -> tuple:
    """Загружает данные из кэша. Возвращает (данные, возраст в часах) или (None, None)"""
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        timestamp = datetime.fromisoformat(cache.get("timestamp"))
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        return cache.get("data"), age_hours
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None, None


def is_cache_fresh(age_hours: float, max_age: float = 3.0) -> bool:
    """Проверяет, не старше ли кэш max_age часов"""
    return age_hours is not None and age_hours <= max_age


def get_coordinates(city: str) -> tuple:
    API_KEY = os.getenv("API_KEY")
    headers = {
        'User-Agent': 'WeatherApp/1.0'
    }
    url = f'https://nominatim.openstreetmap.org/search?q={city}&format=json'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            return lat, lon
    return None, None


def get_weather_by_coordinates(latitude: float, longitude: float, retries: int = 3) -> dict:
    """Получает погоду с повторными попытками при ошибках"""
    API_KEY = os.getenv("API_KEY")
    headers = {
        'X-Yandex-Weather-Key': API_KEY
    }
    url = f'https://api.weather.yandex.ru/v2/forecast?lat={latitude}&lon={longitude}'
    
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                last_error = "Ошибка 429: Слишком много запросов"
                if attempt < retries - 1:
                    delay = 2 ** attempt
                    print(f"Получена ошибка 429. Повтор через {delay} секунд...")
                    time.sleep(delay)
                    continue
            else:
                last_error = f"Ошибка: {response.status_code}"
                if attempt < retries - 1:
                    delay = 2 ** attempt
                    print(f"Получена ошибка {response.status_code}. Повтор через {delay} секунд...")
                    time.sleep(delay)
                    continue
                    
        except requests.exceptions.RequestException as e:
            last_error = f"Сетевая ошибка: {str(e)}"
            if attempt < retries - 1:
                delay = 2 ** attempt
                print(f"Сетевая ошибка. Повтор через {delay} секунд...")
                time.sleep(delay)
                continue
    
    print(last_error)
    return None


def get_current_weather(city: str = None, latitude: float = None, longitude: float = None) -> dict:
    if city:
        print(f"Получаем погоду для города: {city}")
        lat, lon = get_coordinates(city)
        if lat and lon:
            print(f"Координаты: {lat}, {lon}")
            return get_weather_by_coordinates(lat, lon)
        else:
            print("Не удалось найти координаты города")
            return None
    if latitude and longitude:
        print(f"Получаем погоду для координат: {latitude}, {longitude}")
        return get_weather_by_coordinates(latitude, longitude)


def save_weather_to_file(weather_data: dict, filename: str = "weather.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)
    print(f"Погода сохранена в файл: {filename}")


if __name__ == "__main__":
    from weather_info import read_weather_from_file, print_weather_summary
    
    while True:
        print("\n" + "="*50)
        print("== Прогноз погоды на основе API Яндекс.Погоды ==")
        print("="*50)
        print("1. По названию города")
        print("2. По координатам")
        print("3. Выход")
        print("="*50)
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == "1":
            city = input("\nВведите название города: ").strip()
            if city:
                weather = get_current_weather(city=city)
                if weather:
                    save_weather_to_file(weather)
                    save_to_cache(weather)
                    print_weather_summary(weather)
                else:
                    cache_data, cache_age = load_from_cache()
                    if cache_data and is_cache_fresh(cache_age):
                        print(f"\nНе удалось получить данные. Показываем из кэша (возраст: {cache_age:.1f} ч)")
                        save_weather_to_file(cache_data)
                        print_weather_summary(cache_data)
                    else:
                        print("Не удалось получить данные о погоде и кэш устарел")
            else:
                print("Название города не введено")
                
        elif choice == "2":
            try:
                lat = float(input("\nВведите широту (latitude): ").strip())
                lon = float(input("Введите долготу (longitude): ").strip())
                weather = get_current_weather(latitude=lat, longitude=lon)
                if weather:
                    save_weather_to_file(weather)
                    save_to_cache(weather)
                    print_weather_summary(weather)
                else:
                    cache_data, cache_age = load_from_cache()
                    if cache_data and is_cache_fresh(cache_age):
                        print(f"\nНе удалось получить данные. Показываем из кэша (возраст: {cache_age:.1f} ч)")
                        save_weather_to_file(cache_data)
                        print_weather_summary(cache_data)
                    else:
                        print("Не удалось получить данные о погоде и кэш устарел")
            except ValueError:
                print("Некорректные координаты. Введите числа.")
                
        elif choice == "3":
            print("\nДо свидания!")
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1, 2 или 3")
