import requests
import math
from . import get_coordinates

def distance(lat1, lon1, lat2, lon2):
    '''Haversine distance between lat and lon points'''
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_closest_airport(city):
    '''Find the closest international airports to a city using OpenStreetMap Overpass API'''

    coordinates = get_coordinates(city)
    if coordinates is None:
        return 'City not found'

    lat, lon = coordinates

    # Query for international airports within 200km radius of the city
    overpass_query = f'[out:json][timeout:25];nwr[aeroway=aerodrome][iata][aerodrome=international](around:300000,{lat},{lon});out center;'
    response = requests.post('https://overpass-api.de/api/interpreter', data={'data': overpass_query})
    if response.status_code != 200 or not response.text.strip():
        return 'Airport search temporarily unavailable'
    data = response.json()
    airports = data.get('elements', [])

    if not airports:
        return 'No airports found within 200km'

    for airport in airports:
        if 'center' in airport: # Get lat and lon from the 'center' field if available
            airport['lat'] = airport['center']['lat']
            airport['lon'] = airport['center']['lon']

    for airport in airports: 
        airport['dist'] = round(distance(lat, lon, airport['lat'], airport['lon'])) # Calculate distance from city to each airport

    airports.sort(key=lambda airport: airport['dist']) # Sort by closest airports first
    
    results = []
    for airport in airports[:3]:
        name = airport['tags'].get('name', 'Unknown Airport')
        iata = airport['tags'].get('iata', '')

        if iata:
            results.append(f'{name} ({iata})')
        else:
            results.append(name)
    return results