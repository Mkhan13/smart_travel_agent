import requests

def get_weather(city):
    '''Fetch basic weather info using Open-Meteo API'''

    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}' #Get latitude and longitude for the city
    geo_response = requests.get(geo_url).json()

    if 'results' not in geo_response:
        return 'Could not find location'

    lat = geo_response['results'][0]['latitude']
    lon = geo_response['results'][0]['longitude']

    weather_url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true') # Get weather data
    weather_data = requests.get(weather_url).json()
    current = weather_data.get('current_weather', {})

    temp_c = current.get("temperature")
    temp_f = (temp_c * 9/5) + 32

    return {
        "temperature_c": temp_c,
        "temperature_f": round(temp_f, 1),
        "wind_speed_kmh": current.get("windspeed"),
        "summary": f"{round(temp_f,1)}°F ({temp_c}°C), wind {current.get('windspeed')} km/h"
    }