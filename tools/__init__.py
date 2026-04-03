import requests

def get_coordinates(city):
    '''Return lat and lon for a city'''
    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}'
    geo_response = requests.get(geo_url).json()

    if 'results' not in geo_response:
        return None

    result = geo_response['results'][0]
    return result['latitude'], result['longitude']
