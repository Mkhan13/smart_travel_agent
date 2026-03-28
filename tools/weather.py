import requests

def get_weather(city):
    '''Fetch basic weather info using Open-Meteo API'''

    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}' #Get latitude and longitude for the city
    geo_response = requests.get(geo_url).json()

    if 'results' not in geo_response:
        return 'Could not find location'

    lat = geo_response['results'][0]['latitude']
    lon = geo_response['results'][0]['longitude']

    weather_url = (
        f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
        f'&current_weather=true&daily=precipitation_sum,weathercode&timezone=auto'
    )
    weather_data = requests.get(weather_url).json()
    current = weather_data.get('current_weather', {})
    daily = weather_data.get('daily', {})

    temp_c = current.get("temperature")
    temp_f = (temp_c * 9/5) + 32

    # Average precipitation over next 7 days
    precip_list = daily.get("precipitation_sum", [])
    avg_precip_mm = round(sum(precip_list) / len(precip_list), 1) if precip_list else 0
    will_rain = avg_precip_mm > 1.0  # more than 1mm/day average means rain likely

    return {
        "temperature_c": temp_c,
        "temperature_f": round(temp_f, 1),
        "wind_speed_kmh": current.get("windspeed"),
        "avg_daily_precip_mm": avg_precip_mm,
        "will_rain": will_rain,
        "summary": f"{round(temp_f,1)}°F ({temp_c}°C), wind {current.get('windspeed')} km/h, avg precip {avg_precip_mm} mm/day"
    }