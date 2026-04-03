from datetime import datetime
from .weather import get_weather

BASE_LIST = [
    # Essentials
    'Passport / ID',
    'Travel insurance documents',
    'Credit/debit cards',
    'Local currency (cash)',
    # Clothing
    'Underwear',
    'Socks',
    'T-shirts / tops',
    'Pants / jeans',
    'Comfortable walking shoes',
    'Pajamas',
    # Toiletries
    'Toothbrush and toothpaste',
    'Shampoo and conditioner',
    'Deodorant',
    'Sunscreen',
    'Perfume / cologne',
    'Hairbrush / comb',
    'Makeup (if used)',
    'Feminine hygiene products (if needed)',
    # Tech and other
    'Phone charger',
    'Universal outlet adapter',
    'Earphones',
    'Daily medications',
    'Reusable water bottle',
    'Everyday bag / backpack',
]

COLD_THRESHOLD_C = 15   # below this, bring cold weather items
VERY_COLD_THRESHOLD_C = 5  # below this, bring heavy winter items
HOT_THRESHOLD_C = 28    # above this, bring hot weather items

def get_packing_list(city, start_date=None, end_date=None):
    '''Generate a packing list for a trip to a city. Uses live weather data to add weather-appropriate items.'''
    weather = get_weather(city, start_date, end_date)

    # Calculate trip length from dates
    if start_date and end_date:
        trip_days = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days
    else:
        trip_days = 7

    if isinstance(weather, str):
        return {'error': f'Could not fetch weather for {city}: {weather}'}

    temp_c = weather['temperature_c']
    will_rain = weather['will_rain']
    wind_kmh = weather['wind_speed_kmh']

    packing_list = list(BASE_LIST)
    weather_additions = []

    # Rain items
    if will_rain:
        weather_additions += ['Compact umbrella', 'Waterproof rain jacket', 'Waterproof shoes / shoe covers']

    # Temperature dependent items
    if temp_c < VERY_COLD_THRESHOLD_C:
        weather_additions += [
            'Heavy winter coat',
            'Thermal underlayers',
            'Warm hat / beanie',
            'Scarf',
            'Gloves / mittens',
            'Thick wool socks',
            'Insulated waterproof boots',
        ]
    elif temp_c < COLD_THRESHOLD_C:
        weather_additions += [
            'Light jacket or fleece',
            'Sweater / hoodie',
            'Long pants',
            'Light gloves',
            'Warm scarf',
        ]
    elif temp_c >= HOT_THRESHOLD_C:
        weather_additions += [
            'Light, breathable clothing',
            'Shorts',
            'Sandals / flip-flops',
            'Wide-brim hat / baseball cap',
            'Sunglasses',
            'Extra sunscreen',
        ]

    # Wind items
    if wind_kmh > 30 and 'Light jacket or fleece' not in weather_additions and 'Heavy winter coat' not in weather_additions:
        weather_additions.append('Windbreaker jacket')

    # Longer trip items
    if trip_days > 5:
        packing_list.append('Laundry bag / travel detergent')
    if trip_days > 10:
        packing_list.append('Extra luggage space or foldable bag')

    return packing_list + weather_additions