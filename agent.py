import os
import json
import requests
from dotenv import load_dotenv

from tools.weather import get_weather
from tools.currency import convert_currency
from tools.airport import get_closest_airport
from tools.packing import get_packing_list
from tools.country import get_country_info

load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'


TOOLS = {
    'get_weather': get_weather,
    'get_closest_airport': get_closest_airport,
    'get_packing_list': get_packing_list,
    'get_country_info': get_country_info,
    'convert_currency': convert_currency,
}

TOOL_DESCRIPTIONS = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Get weather forecast for a city during specific travel dates. Returns temperature, wind, precipitation, and daily breakdown.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {'type': 'string', 'description': 'City name'},
                    'start_date': {'type': 'string', 'description': 'Start date in YYYY-MM-DD format'},
                    'end_date': {'type': 'string', 'description': 'End date in YYYY-MM-DD format'},
                },
                'required': ['city'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_closest_airport',
            'description': 'Find the 3 closest international airports to a city.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {'type': 'string', 'description': 'City name'},
                },
                'required': ['city'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_packing_list',
            'description': 'Generate a smart packing list based on destination weather and trip length.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {'type': 'string', 'description': 'City name'},
                    'start_date': {'type': 'string', 'description': 'Start date in YYYY-MM-DD format'},
                    'end_date': {'type': 'string', 'description': 'End date in YYYY-MM-DD format'},
                },
                'required': ['city'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_country_info',
            'description': 'Get useful travel info about a country: capital, language, currency, timezone, calling code, driving side.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'country': {'type': 'string', 'description': 'Country name'},
                },
                'required': ['country'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'convert_currency',
            'description': 'Convert an amount from one currency to another.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'from_currency': {'type': 'string', 'description': 'Source currency code (e.g. USD)'},
                    'to_currency': {'type': 'string', 'description': 'Target currency code (e.g. EUR)'},
                    'amount': {'type': 'number', 'description': 'Amount to convert'},
                },
                'required': ['from_currency', 'to_currency', 'amount'],
            },
        },
    },
]

# Common aliases for countries and cities
COUNTRY_ALIASES = {
    'us': 'United States of America',
    'usa': 'United States of America',
    'america': 'United States of America',
    'united states': 'United States of America',
    'uk': 'United Kingdom',
    'england': 'United Kingdom',
    'britain': 'United Kingdom',
    'great britain': 'United Kingdom',
    'south korea': 'Korea',
    'uae': 'United Arab Emirates',
    'czech republic': 'Czechia',
    'holland': 'Netherlands',
    'ivory coast': "Côte d'Ivoire",
}

CITY_ALIASES = {
    'la': 'Los Angeles',
    'nyc': 'New York City',
    'ny': 'New York City',
    'dc': 'Washington',
    'washington dc': 'Washington',
    'washington d.c.': 'Washington',
    'sf': 'San Francisco',
    'philly': 'Philadelphia',
    'vegas': 'Las Vegas',
    'dallas ft worth': 'Dallas',
    'rio': 'Rio de Janeiro',
    'sao paulo': 'São Paulo',
    'st petersburg': 'Saint Petersburg',
    'st. petersburg': 'Saint Petersburg',
}


def normalize_input(value, aliases):
    '''Convert input to match a known alias'''
    lookup = value.strip().lower()
    if lookup in aliases:
        return aliases[lookup]
    return value.strip()


SYSTEM_PROMPT = '''You are a smart travel planning assistant. The user will provide a city, country, departure date, and return date.
Your job is to call the appropriate tools to gather all the travel information they need.
Always call: get_weather, get_closest_airport, get_packing_list, and get_country_info.
For convert_currency, convert 100 USD to the local currency of the destination country.
Use the provided dates for weather and packing tools.'''


def call_groq(messages, tools):
    '''Send a chat completion request to the Groq API with tool definitions.
    Returns the parsed JSON response, or None if the request fails.'''
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json',
    }

    body = {
        'model': 'llama-3.3-70b-versatile',
        'messages': messages,
        'tools': tools,
        'tool_choice': 'auto',  # Model can decide which tools to call
    }

    response = requests.post(GROQ_URL, headers=headers, json=body)
    if response.status_code != 200: # API error handling
        print(f'API error {response.status_code}: {response.text[:500]}')
        return None
    return response.json()


def run_agent(city, country, departure_date, return_date):
    '''Send user message to the agent and call tools'''

    # Normalize user inputs
    city = normalize_input(city, CITY_ALIASES) 
    country = normalize_input(country, COUNTRY_ALIASES)

    # Build prompt
    user_message = f'I am planning a trip to {city}, {country}. I depart on {departure_date} and return on {return_date}. Please gather all the travel information I need.'

    messages = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': user_message},
    ]
    results = {}
    expected_tools = set(TOOLS.keys())

    for _ in range(3): # Limit to 3 tries so it doesnt get stuck in a loop
        response = call_groq(messages, TOOL_DESCRIPTIONS)
        if response is None:
            return {'error': 'Failed to get response from the Model'}

        choice = response['choices'][0]['message'] # Model response
        tool_calls = choice.get('tool_calls', []) # Tools the model wants to call

        if not tool_calls:
            break  # No more tools to call

        messages.append(choice) # Add response to conversation history so model has context for next call

        for call in tool_calls:
            func_name = call['function']['name']
            args = json.loads(call['function']['arguments']) # Load arguments

            if func_name in TOOLS: 
                result = TOOLS[func_name](**args) # Call tool
                results[func_name] = result
           
            messages.append({  # Add tool result to conversation so the model knows it was executed
                'role': 'tool',
                'tool_call_id': call['id'],
                'content': json.dumps(result, default=str),
            })

        if expected_tools.issubset(results.keys()): # Stop early if all tools have been called
            break

    return results