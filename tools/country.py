import requests

def get_country_info(country):
    '''Get useful travel info about a country using the REST Countries API'''

    response = requests.get(f'https://restcountries.com/v3.1/name/{country}')

    if response.status_code != 200:
        return 'Country not found'

    data = response.json()[0] # First result is most relevant

    # Get the main language and currency
    languages = data.get('languages', {})
    currencies = data.get('currencies', {})
    currency_code = list(currencies.keys())[0] if currencies else None
    currency_info = currencies.get(currency_code, {})

    return {
        'name': data.get('name', {}).get('common', country),
        'capital': data.get('capital', ['Unknown'])[0],
        'language': list(languages.values())[0] if languages else 'Unknown',
        'currency': f'{currency_info.get("name", "Unknown")} ({currency_code})' if currency_code else 'Unknown',
        'timezone': data.get('timezones', ['Unknown'])[0],
        'calling_code': data.get('idd', {}).get('root', '') + (data.get('idd', {}).get('suffixes', [''])[0]),
        'driving_side': data.get('car', {}).get('side', 'Unknown'),
        'population': data.get('population', 'Unknown'),
    }

print(get_country_info('France'))