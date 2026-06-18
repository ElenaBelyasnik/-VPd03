#!/usr/bin/env python3
"""
Виртуальное окружение:
  cd Vpd04_wether_app
  python -m venv venv
  .\\venv\\Scripts\\Activate.ps1  # Windows PowerShell
  .\\venv\\Scripts\\activate.bat  # Windows CMD
  source venv/bin/activate  # Linux/Mac
  pip install -r requirements.txt
"""

import os
import sys
import json
import time
import datetime
import logging
import argparse
from typing import Optional, Tuple, Dict, Any

import requests
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    logger.error("API_KEY не найден в .env")
    sys.exit(1)

YANDEX_WEATHER_URL = "https://api.weather.yandex.ru/v2/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

CACHE_FILE = "weather_cache.json"
CURRENT_FILE = "weather.json"
CACHE_TTL = 3 * 3600  # 3 часа в секундах
MAX_RETRIES = 3


def get_coordinates(city: str) -> Optional[Tuple[float, float]]:
    """
    Получить координаты города через OpenStreetMap Nominatim.

    Args:
        city: Название города

    Returns:
        Кортеж (lat, lon) или None при ошибке
    """
    headers = {"User-Agent": "WeatherApp/1.0"}
    url = f"{NOMINATIM_URL}?q={city}&format=json"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return lat, lon
        return None
    except requests.RequestException as e:
        logger.error("Ошибка геокодирования: %s", e)
        return None


def get_weather_by_coordinates(
    latitude: float, longitude: float, days: int = 1, extended: bool = False
) -> Optional[dict]:
    """
    Получить прогноз погоды по координатам.

    Args:
        latitude: Широта
        longitude: Долгота
        days: Количество дней (1-7), по умолчанию 1
        extended: Расширенный режим с качеством воздуха

    Returns:
        Словарь с данными API или None при ошибке
    """
    if days < 1 or days > 7:
        logger.warning("days=%d вне диапазона 1-7. Установлено days=1.", days)
        days = 1

    headers = {"X-Yandex-Weather-Key": API_KEY}
    params = {"lat": latitude, "lon": longitude, "lang": "ru_RU", "limit": days}
    if extended:
        params["extra"] = "true"

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                YANDEX_WEATHER_URL, headers=headers, params=params, timeout=15
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                last_error = "Ошибка 429: Слишком много запросов"
                if attempt < MAX_RETRIES - 1:
                    delay = 2 ** attempt
                    logger.warning("%s. Повтор через %d сек...", last_error, delay)
                    time.sleep(delay)
                    continue
            else:
                last_error = f"Ошибка {response.status_code}"
                if attempt < MAX_RETRIES - 1:
                    delay = 2 ** attempt
                    logger.warning("%s. Повтор через %d сек...", last_error, delay)
                    time.sleep(delay)
                    continue
                    
        except requests.RequestException as e:
            last_error = f"Сетевая ошибка: {e}"
            if attempt < MAX_RETRIES - 1:
                delay = 2 ** attempt
                logger.warning("%s. Повтор через %d сек...", last_error, delay)
                time.sleep(delay)
                continue
    
    logger.error(last_error)
    return None


def save_weather_to_file(weather_data: dict, filename: str = CURRENT_FILE) -> None:
    """Сохранить погоду в JSON файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=2)
    logger.info("Погода сохранена в %s", filename)


def save_to_cache(
    weather_data: dict, city: Optional[str], lat: float, lon: float, days: int
) -> None:
    """
    Сохранить данные погоды в кэш с метаданными.

    Args:
        weather_data: Данные погоды от API
        city: Название города
        lat: Широта
        lon: Долгота
        days: Количество дней прогноза
    """
    cache = {
        "timestamp": int(time.time()),
        "city": city,
        "lat": lat,
        "lon": lon,
        "days": days,
        "data": weather_data,
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    logger.info("Данные сохранены в кэш")


def load_from_cache() -> Optional[dict]:
    """
    Загрузить данные из кэша.

    Returns:
        Данные погоды или None
    """
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        return cache.get("data")
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning("Ошибка чтения кэша: %s", e)
        return None


def is_cache_valid(
    city: Optional[str], lat: float, lon: float, days: int
) -> bool:
    """
    Проверить валидность кэша (TTL + совпадение city/days).

    Args:
        city: Название города
        lat: Широта
        lon: Долгота
        days: Количество дней

    Returns:
        True если кэш свежий и совпадает
    """
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        ts_raw = cache.get("timestamp")
        # Поддержка старого формата (строка ISO) и нового (int)
        if isinstance(ts_raw, str):
            ts = datetime.datetime.fromisoformat(ts_raw).timestamp()
        else:
            ts = float(ts_raw)
        
        age_hours = (time.time() - ts) / 3600

        if age_hours > 3.0:
            logger.info("Кэш устарел (более 3 часов)")
            return False

        if cache.get("city") != city:
            logger.info("Кэш не совпадает по городу")
            return False

        if cache.get("days") != days:
            logger.info("Кэш не совпадает по количеству дней")
            return False

        logger.info("Кэш валиден")
        return True

    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False


def get_current_weather(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    days: int = 1,
    extended: bool = False,
) -> Optional[dict]:
    """
    Универсальная функция получения погоды.

    Args:
        city: Название города
        lat: Широта
        lon: Долгота
        days: Количество дней (1-7)
        extended: Расширенный режим

    Returns:
        Словарь с данными погоды или None
    """
    # Проверка кэша
    if is_cache_valid(city, lat or 0, lon or 0, days):
        cached = load_from_cache()
        if cached:
            logger.info("Использован кэш")
            return cached

    # Геокодирование
    if city and (lat is None or lon is None):
        coords = get_coordinates(city)
        if coords is None:
            print(f"{Fore.RED}Город не найден. Проверьте название.{Style.RESET_ALL}")
            return None
        lat, lon = coords

    if lat is None or lon is None:
        print(f"{Fore.RED}Укажите город или координаты.{Style.RESET_ALL}")
        return None

    # API запрос
    data = get_weather_by_coordinates(lat, lon, days=days, extended=extended)
    if data is None:
        # Попытка использовать кэш при ошибке API
        cached = load_from_cache()
        if cached:
            logger.info("Использован кэш после ошибки API")
            return cached
        print(f"{Fore.RED}Ошибка получения данных.{Style.RESET_ALL}")
        return None

    # Сохранение
    save_weather_to_file(data)
    save_to_cache(data, city, lat, lon, days)
    return data


def read_weather_from_file(filename: str = CURRENT_FILE) -> Optional[dict]:
    """Прочитать погоду из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Ошибка чтения %s: %s", filename, e)
        return None


def parse_cli_args() -> argparse.Namespace:
    """Парсить аргументы командной строки."""
    parser = argparse.ArgumentParser(description="Прогноз погоды (Яндекс.Погода)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--city", type=str, help="Название города")
    group.add_argument(
        "--coords", nargs=2, type=float, metavar=("LAT", "LON"), help="Координаты"
    )
    parser.add_argument(
        "--days", type=int, default=1, help="Количество дней (1-7), по умолчанию 1"
    )
    parser.add_argument(
        "--extended", action="store_true", help="Расширенный режим (качество воздуха)"
    )
    parser.add_argument(
        "--read", action="store_true", help="Прочитать данные из weather.json"
    )
    return parser.parse_args()


def show_main_menu() -> None:
    """Отобразить интерактивное меню."""
    menu_items = [
        ("1", "Прогноз по названию города (текущая погода)", "city_current"),
        ("2", "Прогноз по координатам (текущая погода)", "coords_current"),
        ("3", "Прогноз по названию города на 5 дней", "city_5days"),
        ("4", "Прогноз по координатам на 5 дней", "coords_5days"),
        ("5", "Расширенный режим по названию города", "city_extended"),
        ("6", "Расширенный режим по координатам", "coords_extended"),
        ("7", "Выход", "exit"),
    ]

    while True:
        print(f"\n{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  Меню прогноза погоды{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 40}{Style.RESET_ALL}")
        for code, text, _ in menu_items:
            marker = Fore.GREEN if code == "7" else Fore.YELLOW
            print(f"  {marker}[{code}] {text}{Style.RESET_ALL}")

        choice = input(f"\n{Fore.GREEN}Ваш выбор: {Style.RESET_ALL}").strip()

        for code, _, action in menu_items:
            if choice == code:
                if action == "exit":
                    print(f"{Fore.GREEN}До свидания!{Style.RESET_ALL}")
                    return
                handle_menu_action(action)
                break
        else:
            print(f"{Fore.RED}Неверный выбор. Попробуйте снова.{Style.RESET_ALL}")


def handle_menu_action(action: str) -> None:
    """Обработать действие из меню."""
    from weather_info import (
        print_weather_summary,
        print_forecast_table,
        print_extended_weather,
    )

    if action == "city_current":
        city = input("Введите название города: ").strip()
        if not city:
            return
        data = get_current_weather(city=city, days=1)
        if data:
            print_weather_summary(data)

    elif action == "coords_current":
        try:
            lat = float(input("Широта (lat): "))
            lon = float(input("Долгота (lon): "))
        except ValueError:
            print(f"{Fore.RED}Некорректный ввод.{Style.RESET_ALL}")
            return
        data = get_current_weather(lat=lat, lon=lon, days=1)
        if data:
            print_weather_summary(data)

    elif action == "city_5days":
        city = input("Введите название города: ").strip()
        if not city:
            return
        data = get_current_weather(city=city, days=5)
        if data:
            print_forecast_table(data)

    elif action == "coords_5days":
        try:
            lat = float(input("Широта (lat): "))
            lon = float(input("Долгота (lon): "))
        except ValueError:
            print(f"{Fore.RED}Некорректный ввод.{Style.RESET_ALL}")
            return
        data = get_current_weather(lat=lat, lon=lon, days=5)
        if data:
            print_forecast_table(data)

    elif action == "city_extended":
        city = input("Введите название города: ").strip()
        if not city:
            return
        data = get_current_weather(city=city, days=1, extended=True)
        if data:
            print_extended_weather(data)

    elif action == "coords_extended":
        try:
            lat = float(input("Широта (lat): "))
            lon = float(input("Долгота (lon): "))
        except ValueError:
            print(f"{Fore.RED}Некорректный ввод.{Style.RESET_ALL}")
            return
        data = get_current_weather(lat=lat, lon=lon, days=1, extended=True)
        if data:
            print_extended_weather(data)


def main() -> None:
    """Точка входа: CLI или интерактивное меню."""
    args = parse_cli_args()

    # Режим чтения из файла
    if args.read:
        from weather_info import print_weather_summary

        data = read_weather_from_file()
        if data:
            print_weather_summary(data)
        return

    # CLI режим
    if args.city or args.coords:
        days = max(1, min(7, args.days)) if 1 <= args.days <= 7 else 1
        extended = args.extended
        lat = args.coords[0] if args.coords else None
        lon = args.coords[1] if args.coords else None

        data = get_current_weather(
            city=args.city, lat=lat, lon=lon, days=days, extended=extended
        )
        if data:
            if extended:
                from weather_info import print_extended_weather

                print_extended_weather(data)
            elif days > 1:
                from weather_info import print_forecast_table

                print_forecast_table(data)
            else:
                from weather_info import print_weather_summary

                print_weather_summary(data)
        return

    # Интерактивный режим
    show_main_menu()


if __name__ == "__main__":
    main()
