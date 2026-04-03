import requests

def get_coordinates(city):
    '''Return lat and lon for a city'''
    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}' # Open-Meteo geocoding API
    geo_response = requests.get(geo_url).json()

    if 'results' not in geo_response:
        return None

    result = geo_response['results'][0] # First result is most relevant
    return result['latitude'], result['longitude']

def get_weather(city, start_date=None, end_date=None):
    '''Fetch weather info using Open-Meteo API. If dates are provided, returns forecast for that date range (up to 16 days out). Otherwise returns current weather and 7-day forecast.'''

    coordinates = get_coordinates(city)
    if coordinates is None:
        return 'Could not find location'

    lat, lon = coordinates

    # Build URL with date range if provided
    base_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max&current_weather=true&timezone=auto'
    if start_date and end_date:
        base_url += f'&start_date={start_date}&end_date={end_date}'

    weather_data = requests.get(base_url).json()
    current = weather_data.get('current_weather', {})
    daily = weather_data.get('daily', {})

    # Average temperature across the date range
    max_temps = daily.get('temperature_2m_max', [])
    min_temps = daily.get('temperature_2m_min', [])
    if max_temps and min_temps:
        avg_temp_c = round(sum(max_temps + min_temps) / (len(max_temps) + len(min_temps)), 1)
    else:
        avg_temp_c = current.get('temperature', 0)
    avg_temp_f = round((avg_temp_c * 9/5) + 32, 1)

    precipitation_list = daily.get('precipitation_sum', [])
    if precipitation_list:
        avg_precipitation = round(sum(precipitation_list) / len(precipitation_list), 1)
    else:
        avg_precipitation = 0
    will_rain = avg_precipitation > 1.0 # more than 1mm per day average means rain likely

    wind_speeds = daily.get('windspeed_10m_max', [])
    avg_wind = round(sum(wind_speeds) / len(wind_speeds), 1) if wind_speeds else current.get('windspeed', 0)

    return {
        'temperature_c': avg_temp_c,
        'temperature_f': avg_temp_f,
        'wind_speed_kmh': avg_wind,
        'avg_daily_precip_mm': avg_precipitation,
        'will_rain': will_rain,
        'daily': daily, # Raw daily data for the UI to display per-day breakdown
        'summary': f'{avg_temp_f}°F ({avg_temp_c}°C), wind {avg_wind} km/h, avg precip {avg_precipitation} mm/day'
    }