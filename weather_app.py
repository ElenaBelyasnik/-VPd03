import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()


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


def get_weather_by_coordinates(latitude: float, longitude: float) -> dict:
    API_KEY = os.getenv("API_KEY")
    headers = {
        'X-Yandex-Weather-Key': API_KEY
    }
    url = f'https://api.weather.yandex.ru/v2/forecast?lat={latitude}&lon={longitude}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка: {response.status_code}")
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
        print("1. Прогноз по названию города")
        print("2. Выход")
        print("="*50)
        
        choice = input("\nВыберите действие (1-2): ").strip()
        
        if choice == "1":
            city = input("\nВведите название города: ").strip()
            if city:
                weather = get_current_weather(city=city)
                if weather:
                    save_weather_to_file(weather)
                    print_weather_summary(weather)
                else:
                    print("Не удалось получить данные о погоде")
            else:
                print("Название города не введено")
        elif choice == "2":
            print("\nДо свидания!")
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1 или 2")
