import json
from colorama import init, Fore, Style

init(autoreset=True)


def read_weather_from_file(filename: str = "weather.json"):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            weather = json.load(f)
        return weather
    except FileNotFoundError:
        print(f"{Fore.RED}Файл {filename} не найден{Style.RESET_ALL}")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}Ошибка при чтении {filename}: некорректный JSON{Style.RESET_ALL}")
        return None


def print_weather_summary(weather: dict):
    if not weather:
        print(f"{Fore.RED}Нет данных о погоде{Style.RESET_ALL}")
        return

    fact = weather.get('fact', {})
    info = weather.get('info', {})
    forecasts = weather.get('forecasts', [])

    print("\n" + Fore.CYAN + "="*50 + Style.RESET_ALL)
    print(Fore.CYAN + f"{'ПОГОДА':^50}" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

    # Координаты
    lat = info.get('lat', 'N/A')
    lon = info.get('lon', 'N/A')
    print(f"\n{Fore.YELLOW}Координаты:{Style.RESET_ALL} {Fore.GREEN}{lat}, {lon}{Style.RESET_ALL}")

    # Текущая температура
    temp = fact.get('temp', 'N/A')
    feels_like = fact.get('feels_like', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Температура:{Style.RESET_ALL}        {Fore.WHITE}{temp}°C{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Ощущается как:{Style.RESET_ALL}     {Fore.WHITE}{feels_like}°C{Style.RESET_ALL}")

    # Условия
    condition = fact.get('condition', 'N/A')
    daytime = fact.get('daytime', 'N/A')
    icon = fact.get('icon', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Условие:{Style.RESET_ALL}           {Fore.GREEN}{condition}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Время суток:{Style.RESET_ALL}        {Fore.GREEN}{daytime}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Иконка:{Style.RESET_ALL}             {Fore.GREEN}{icon}{Style.RESET_ALL}")

    # Облачность и влажность
    cloudness = fact.get('cloudness', 0) * 100
    humidity = fact.get('humidity', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Облачность:{Style.RESET_ALL}        {Fore.BLUE}{cloudness}%{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Влажность:{Style.RESET_ALL}          {Fore.BLUE}{humidity}%{Style.RESET_ALL}")

    # Давление
    pressure_mm = fact.get('pressure_mm', 'N/A')
    pressure_pa = fact.get('pressure_pa', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Давление:{Style.RESET_ALL}          {Fore.CYAN}{pressure_mm} мм рт.ст. ({pressure_pa} Па){Style.RESET_ALL}")

    # Ветер
    wind_speed = fact.get('wind_speed', 'N/A')
    wind_dir = fact.get('wind_dir', 'N/A')
    wind_angle = fact.get('wind_angle', 'N/A')
    wind_gust = fact.get('wind_gust', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Ветер:{Style.RESET_ALL}             {Fore.CYAN}{wind_speed} м/с, {wind_dir} ({wind_angle}°){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Порывы ветра:{Style.RESET_ALL}       {Fore.CYAN}{wind_gust} м/с{Style.RESET_ALL}")

    # UV индекс
    uv_index = fact.get('uv_index', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}UV индекс:{Style.RESET_ALL}          {Fore.YELLOW}{uv_index}{Style.RESET_ALL}")

    # Прогноз на день
    if forecasts:
        today = forecasts[0]
        date = today.get('date', 'N/A')
        temp_avg = today.get('parts', {}).get('day', {}).get('temp_avg', 'N/A')
        temp_max = today.get('parts', {}).get('day', {}).get('temp_max', 'N/A')
        temp_min = today.get('parts', {}).get('day', {}).get('temp_min', 'N/A')
        sunrise = today.get('sunrise', 'N/A')
        sunset = today.get('sunset', 'N/A')

        print(f"\n{Fore.MAGENTA}{'═'*50}{Style.RESET_ALL}")
        print(Fore.MAGENTA + f"{'ПРОГНОЗ НА ДЕНЬ':^50}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"{'═'*50}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Дата:{Style.RESET_ALL}             {Fore.GREEN}{date}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Средняя температура:{Style.RESET_ALL} {Fore.WHITE}{temp_avg}°C{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Макс. температура:{Style.RESET_ALL}  {Fore.WHITE}{temp_max}°C{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Мин. температура:{Style.RESET_ALL}   {Fore.WHITE}{temp_min}°C{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Восход:{Style.RESET_ALL}           {Fore.GREEN}{sunrise}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Закат:{Style.RESET_ALL}            {Fore.GREEN}{sunset}{Style.RESET_ALL}")

    # Время обновления
    now_dt = weather.get('now_dt', 'N/A')
    print(f"\n{Fore.MAGENTA}{'─'*50}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Время обновления:{Style.RESET_ALL}  {Fore.WHITE}{now_dt}{Style.RESET_ALL}")

    print(Fore.CYAN + "="*50 + Style.RESET_ALL + "\n")


if __name__ == "__main__":
    weather = read_weather_from_file()
    print_weather_summary(weather)
