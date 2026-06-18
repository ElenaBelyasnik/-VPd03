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

import json
from typing import Optional, Dict, Any
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)


# Константы для отображения условий
CONDITION_EMOJI = {
    "clear": "☀️",
    "partly-cloudy": "⛅",
    "cloudy": "☁️",
    "overcast": "☁️",
    "drizzle": "🌦️",
    "light-rain": "🌦️",
    "rain": "🌧️",
    "moderate-rain": "🌧️",
    "heavy-rain": "🌧️",
    "continuous-heavy-rain": "🌧️",
    "showers": "🌦️",
    "wet-snow": "🌨️",
    "light-snow": "🌨️",
    "snow": "❄️",
    "snow-showers": "🌨️",
    "hail": "🌨️",
    "thunderstorm": "⛈️",
    "thunderstorm-with-rain": "⛈️",
    "thunderstorm-with-hail": "⛈️",
    "fog": "🌫️",
    "smoke": "🌫️",
}

TIME_LABELS = {
    "night": "🌙 Ночь",
    "morning": "🌅 Утро",
    "day": "☀️ День",
    "evening": "🌆 Вечер",
}


def _get_condition_emoji(condition: str) -> str:
    """Вернуть эмодзи для условия погоды."""
    return CONDITION_EMOJI.get(condition.lower(), "🌡️")


def _format_temp(temp: Any, feels_like: Optional[Any] = None) -> str:
    """Форматировать температуру."""
    result = f"{Fore.CYAN}{temp}°C{Style.RESET_ALL}"
    if feels_like is not None:
        result += f" (ощущается как {Fore.GREEN}{feels_like}°C{Style.RESET_ALL})"
    return result


def read_weather_from_file(filename: str = "weather.json") -> Optional[Dict[str, Any]]:
    """
    Прочитать погоду из JSON файла.

    Args:
        filename: Путь к файлу

    Returns:
        Словарь с данными погоды или None
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            weather = json.load(f)
        return weather
    except FileNotFoundError:
        print(f"{Fore.RED}Файл {filename} не найден{Style.RESET_ALL}")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}Ошибка при чтении {filename}: некорректный JSON{Style.RESET_ALL}")
        return None


def print_weather_summary(weather: Dict[str, Any]) -> None:
    """
    Отобразить текущую погоду и прогноз на сегодня.

    Args:
        weather: Данные погоды от API
    """
    fact = weather.get("fact", {})
    info = weather.get("info", {})
    forecasts = weather.get("forecasts", [])

    print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    print(Fore.CYAN + f"{'📍 ТЕКУЩАЯ ПОГОДА':^50}" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

    # Координаты
    lat = info.get("lat", "N/A")
    lon = info.get("lon", "N/A")
    print(f"\n{Fore.YELLOW}Координаты:{Style.RESET_ALL} {Fore.GREEN}{lat}, {lon}{Style.RESET_ALL}")

    # Текущая температура
    temp = fact.get("temp", "N/A")
    feels_like = fact.get("feels_like", "N/A")
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Температура:{Style.RESET_ALL}        {_format_temp(temp, feels_like)}")

    # Условия
    condition = fact.get("condition", "N/A")
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Условие:{Style.RESET_ALL}           {_get_condition_emoji(condition)} {condition}")

    # Влажность и давление
    humidity = fact.get("humidity", "N/A")
    pressure_mm = fact.get("pressure_mm", "N/A")
    pressure_pa = fact.get("pressure_pa", "N/A")
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Влажность:{Style.RESET_ALL}          {Fore.BLUE}{humidity}%{Style.RESET_ALL}")
    print(
        f"{Fore.YELLOW}Давление:{Style.RESET_ALL}          {Fore.CYAN}{pressure_mm} мм рт.ст.{Style.RESET_ALL}"
        + (f" ({pressure_pa} Па)" if pressure_pa else "")
    )

    # Ветер
    wind_speed = fact.get("wind_speed", "N/A")
    wind_dir = fact.get("wind_dir", "N/A")
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(
        f"{Fore.YELLOW}Ветер:{Style.RESET_ALL}             {Fore.CYAN}{wind_speed} м/с, {wind_dir}{Style.RESET_ALL}"
    )

    # Прогноз на день
    if forecasts:
        today = forecasts[0]
        date = today.get("date", "N/A")
        sunrise = today.get("sunrise", "N/A")
        sunset = today.get("sunset", "N/A")
        parts = today.get("parts", {})

        print(f"\n{Fore.MAGENTA}{'═' * 50}{Style.RESET_ALL}")
        print(Fore.MAGENTA + f"{'📅 ПРОГНОЗ НА ДЕНЬ':^50}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"{'═' * 50}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Дата:{Style.RESET_ALL}             {Fore.GREEN}{date}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Восход:{Style.RESET_ALL}           {Fore.GREEN}{sunrise}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Закат:{Style.RESET_ALL}            {Fore.GREEN}{sunset}{Style.RESET_ALL}")

        # Прогноз по периодам
        for period_key, label in TIME_LABELS.items():
            part = parts.get(period_key, {})
            if part:
                temp_avg = part.get("temp_avg", part.get("temp", "N/A"))
                condition = part.get("condition", "")
                wind = part.get("wind_speed", "N/A")
                print(
                    f"  {label}: {Fore.CYAN}{temp_avg}°C{Style.RESET_ALL}  | "
                    f"{str(wind):>5} м/с | {_get_condition_emoji(condition)} {condition}"
                )

    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL + "\n")


def print_forecast_table(weather: Dict[str, Any]) -> None:
    """
    Отобразить прогноз на несколько дней в виде таблицы.

    Args:
        weather: Данные погоды от API
    """
    forecasts = weather.get("forecasts", [])
    if not forecasts:
        print(f"{Fore.RED}Нет данных прогноза.{Style.RESET_ALL}")
        return

    # Ширина колонок
    col_date = 12
    col_period = 10
    col_temp = 8
    col_wind = 8
    col_cond = 18

    # Словари для периодов и условий без эмодзи (для выравнивания)
    PERIOD_NAMES = {
        "night": "Ночь",
        "morning": "Утро",
        "day": "День",
        "evening": "Вечер",
    }

    print("\n" + Fore.CYAN + "=" * 60 + Style.RESET_ALL)
    print(Fore.CYAN + f"{'📅 ПРОГНОЗ НА ' + str(len(forecasts)) + ' ДНЕЙ':^60}" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL)

    # Заголовок таблицы
    header = (
        f"  {'Дата':<{col_date}} | {'Период':<{col_period}} | "
        f"{'Темп.':<{col_temp}} | {'Ветер':<{col_wind}} | {'Условие'}"
    )
    print(f"\n{Fore.YELLOW}{header}{Style.RESET_ALL}")
    print(
        f"  {'-' * col_date}-+-{'-' * col_period}-+-{'-' * col_temp}-+-{'-' * col_wind}-+-{'-' * col_cond}"
    )

    for fc in forecasts:
        date_str = fc.get("date", "N/A")
        parts = fc.get("parts", {})

        for period_key in ["night", "morning", "day", "evening"]:
            part = parts.get(period_key, {})
            if not part:
                continue

            temp_avg = part.get("temp_avg", part.get("temp", "N/A"))
            wind = part.get("wind_speed", "N/A")
            condition = part.get("condition", "")
            # Используем текст без эмодзи для корректного выравнивания
            period_text = PERIOD_NAMES.get(period_key, period_key)

            row = (
                f"  {date_str:<{col_date}} | "
                f"{period_text:<{col_period}} | "
                f"{Fore.CYAN}{str(temp_avg):>{col_temp}}°C{Style.RESET_ALL} | "
                f"{str(wind):>{col_wind}} м/с | "
                f"{condition}"
            )
            print(row)

        print(
            f"  {'-' * col_date}-+-{'-' * col_period}-+-{'-' * col_temp}-+-{'-' * col_wind}-+-{'-' * col_cond}"
        )

    print(Fore.CYAN + "=" * 60 + Style.RESET_ALL + "\n")


def print_extended_weather(weather: Dict[str, Any]) -> None:
    """
    Отобразить расширенную погоду с данными о качестве воздуха.

    Args:
        weather: Данные погоды от API
    """
    fact = weather.get("fact", {})
    info = weather.get("info", {})
    forecasts = weather.get("forecasts", [])
    today = forecasts[0] if forecasts else {}
    parts = today.get("parts", {}) if today else {}

    # Расширенные поля
    pressure_pa = fact.get("pressure_pa", None)
    visibility_m = fact.get("visibility_m", None)
    air_quality = fact.get("air_quality", None)

    print("\n" + Fore.CYAN + "=" * 50 + Style.RESET_ALL)
    print(Fore.CYAN + f"{'📍 РАСШИРЕННАЯ ПОГОДА':^50}" + Style.RESET_ALL)
    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL)

    # Координаты
    lat = info.get("lat", "N/A")
    lon = info.get("lon", "N/A")
    print(f"\n{Fore.YELLOW}Координаты:{Style.RESET_ALL} {Fore.GREEN}{lat}, {lon}{Style.RESET_ALL}")

    # Температура
    temp = fact.get("temp", "N/A")
    feels_like = fact.get("feels_like", "N/A")
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Температура:{Style.RESET_ALL}        {_format_temp(temp, feels_like)}")

    # Условия
    condition = fact.get("condition", "N/A")
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Условие:{Style.RESET_ALL}           {_get_condition_emoji(condition)} {condition}")

    # Влажность и давление
    humidity = fact.get("humidity", "N/A")
    pressure_mm = fact.get("pressure_mm", "N/A")
    print(
        f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}"
    )
    print(f"{Fore.YELLOW}Влажность:{Style.RESET_ALL}          {Fore.BLUE}{humidity}%{Style.RESET_ALL}")
    print(
        f"{Fore.YELLOW}Давление:{Style.RESET_ALL}          {Fore.CYAN}{pressure_mm} мм рт.ст.{Style.RESET_ALL}"
        + (f" / {Fore.MAGENTA}{pressure_pa} Па{Style.RESET_ALL}" if pressure_pa else "")
    )

    # Ветер и видимость
    wind_speed = fact.get("wind_speed", "N/A")
    wind_dir = fact.get("wind_dir", "N/A")
    print(
        f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.YELLOW}Ветер:{Style.RESET_ALL}             {Fore.CYAN}{wind_speed} м/с, {wind_dir}{Style.RESET_ALL}"
    )
    print(
        f"{Fore.YELLOW}Видимость:{Style.RESET_ALL}         {Fore.MAGENTA}{visibility_m} м{Style.RESET_ALL}"
        if visibility_m
        else f"{Fore.YELLOW}Видимость:{Style.RESET_ALL}         N/A"
    )

    # Качество воздуха
    print(f"\n{Fore.MAGENTA}{'─' * 50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🌬 Качество воздуха:{Style.RESET_ALL}")
    if air_quality:
        if isinstance(air_quality, dict):
            aqi = air_quality.get("aqi", "N/A")
            aqi_label = air_quality.get("aqi_label", "")
            print(
                f"  AQI: {Fore.GREEN}{aqi} ({aqi_label}){Style.RESET_ALL}"
            )
            pollutants = air_quality.get("pollutants", {})
            for key, val in pollutants.items():
                if isinstance(val, dict):
                    display_val = val.get("display_value", val.get("value", "N/A"))
                    print(f"  {key}: {display_val}")
        else:
            print(f"  {Fore.GREEN}{air_quality}{Style.RESET_ALL}")
    else:
        print(
            f"  {Fore.YELLOW}«Данные о качестве воздуха не доступны для вашего тарифного плана/региона».{Style.RESET_ALL}"
        )

    # Прогноз на день
    if today:
        date = today.get("date", "N/A")
        sunrise = today.get("sunrise", "N/A")
        sunset = today.get("sunset", "N/A")

        print(f"\n{Fore.MAGENTA}{'═' * 50}{Style.RESET_ALL}")
        print(Fore.MAGENTA + f"{'📅 ПРОГНОЗ НА ДЕНЬ':^50}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"{'═' * 50}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Дата:{Style.RESET_ALL}             {Fore.GREEN}{date}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Восход:{Style.RESET_ALL}           {Fore.GREEN}{sunrise}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Закат:{Style.RESET_ALL}            {Fore.GREEN}{sunset}{Style.RESET_ALL}")

        for period_key, label in TIME_LABELS.items():
            part = parts.get(period_key, {})
            if part:
                temp_avg = part.get("temp_avg", part.get("temp", "N/A"))
                condition = part.get("condition", "")
                wind = part.get("wind_speed", "N/A")
                print(
                    f"  {label}: {Fore.CYAN}{temp_avg}°C{Style.RESET_ALL}  | "
                    f"{str(wind):>5} м/с | {_get_condition_emoji(condition)} {condition}"
                )

    print(Fore.CYAN + "=" * 50 + Style.RESET_ALL + "\n")


if __name__ == "__main__":
    weather = read_weather_from_file()
    if weather:
        print_weather_summary(weather)
