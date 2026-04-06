import requests

def get_country_info(country):
    '''Get travel info about a country using the REST Countries API'''

    response = requests.get(f'https://restcountries.com/v3.1/name/{country}?fullText=true')

    if response.status_code != 200: # Partial match if exact match fails
        response = requests.get(f'https://restcountries.com/v3.1/name/{country}')

    if response.status_code != 200:
        return 'Country not found'

    data = response.json()[0]


    languages = data.get('languages', {}) # Get the main language
    if languages:
        language = list(languages.values())[0]  # Get the first language name
    else:
        language = 'Unknown'


    currencies = data.get('currencies', {}) # Get the main currency
    if currencies:
        currency_code = list(currencies.keys())[0]  # Get the first currency code
        currency_name = currencies[currency_code].get('name', 'Unknown')  # Get the currency name
        currency = f'{currency_name} ({currency_code})'
    else:
        currency = 'Unknown'


    timezones = data.get('timezones', ['Unknown']) # Get the timezone
    timezone = 'Unknown'
    for tz in timezones:
        if tz.startswith('UTC+'):
            timezone = tz
            break
    if timezone == 'Unknown': # Fall back if no UTC+ timezone found
        timezone = timezones[0]

    
    idd = data.get('idd', {}) # Get the phone calling code
    root = idd.get('root', '')
    suffixes = idd.get('suffixes', [''])
    calling_code = root + suffixes[0]


    return {
        'name': data.get('name', {}).get('common', country),
        'capital': data.get('capital', ['Unknown'])[0],
        'language': language,
        'currency': currency,
        'timezone': timezone,
        'calling_code': calling_code,
        'driving_side': data.get('car', {}).get('side', 'Unknown'),
        'population': data.get('population', 'Unknown'),
    }