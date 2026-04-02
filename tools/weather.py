import requests

def get_coordinates(city):
    '''Return lat and lon for a city'''
    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}' # Open-Meteo geocoding API
    geo_response = requests.get(geo_url).json()

    if 'results' not in geo_response:
        return None

    result = geo_response['results'][0] # First result is most relevant
    return result['latitude'], result['longitude']

def get_weather(city):
    '''Fetch basic weather info using Open-Meteo API'''

    coordinates = get_coordinates(city)
    if coordinates is None:
        return 'Could not find location'

    lat, lon = coordinates

    weather_url = (f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum,weathercode&timezone=auto')
    weather_data = requests.get(weather_url).json() # Forcast for the next 7 days
    current = weather_data.get('current_weather', {})
    daily = weather_data.get('daily', {})

    temp_c = current.get('temperature')
    temp_f = (temp_c * 9/5) + 32 # Convert Celsius to Fahrenheit

    precipitation_list = daily.get('precipitation_sum', []) # Average precipitation over next 7 days
    if precipitation_list:
        total_precipitation = sum(precipitation_list)
        avg_precipitation = round(total_precipitation / len(precipitation_list), 1)
    else:
        avg_precipitation = 0
    will_rain = avg_precipitation > 1.0  # more than 1mm per day average means rain likely

    return {
        'temperature_c': temp_c,
        'temperature_f': round(temp_f, 1),
        'wind_speed_kmh': current.get('windspeed'),
        'avg_daily_precip_mm': avg_precipitation,
        'will_rain': will_rain,
        'summary': f'{round(temp_f,1)}°F ({temp_c}°C), wind {current.get('windspeed')} km/h, avg precip {avg_precipitation} mm/day'
    }