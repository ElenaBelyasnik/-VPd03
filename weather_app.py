import requests
from dotenv import load_dotenv
import os

load_dotenv()


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
        return
    if latitude and longitude:
        print(f"Получаем погоду для координат: {latitude}, {longitude}")
        return get_weather_by_coordinates(latitude, longitude)


if __name__ == "__main__":
    print(get_weather_by_coordinates(55.7558, 37.6173))
