import time
from datetime import date, timedelta
from agent import run_agent, normalize_input, CITY_ALIASES, COUNTRY_ALIASES

TEST_CASES = [
    ('Paris', 'France', 'France', 'Paris'),
    ('London', 'UK', 'United Kingdom', 'London'),
    ('Tokyo', 'Japan', 'Japan', 'Tokyo'),
    ('Chicago', 'USA', 'United States', 'Washington, D.C.'),
    ('Sydney', 'Australia', 'Australia', 'Canberra'),
    ('Toronto', 'Canada', 'Canada', 'Ottawa'),
]

ALIAS_TESTS = [
    ('usa', COUNTRY_ALIASES, 'United States of America'),
    ('US', COUNTRY_ALIASES, 'United States of America'),
    ('america', COUNTRY_ALIASES, 'United States of America'),
    ('uk', COUNTRY_ALIASES, 'United Kingdom'),
    ('england', COUNTRY_ALIASES, 'United Kingdom'),
    ('nyc', CITY_ALIASES, 'New York City'),
    ('la', CITY_ALIASES, 'Los Angeles'),
    ('sf', CITY_ALIASES, 'San Francisco'),
    ('vegas', CITY_ALIASES, 'Las Vegas'),
    ('dc', CITY_ALIASES, 'Washington'),
    ('Paris', CITY_ALIASES, 'Paris'),
    ('Germany', COUNTRY_ALIASES, 'Germany'),
]

EXPECTED_TOOLS = ['get_weather', 'get_closest_airport', 'get_packing_list', 'get_country_info', 'convert_currency']

START_DATE = str(date.today() + timedelta(days=2))
END_DATE = str(date.today() + timedelta(days=5))

def check_alias(input_val, alias_dict, expected):
    '''Check if an alias is correctly normalized'''
    result = normalize_input(input_val, alias_dict)
    if result == expected:
        print(f'PASS: "{input_val}" - "{result}"')
        return True
    else:
        print(f'FAIL: "{input_val}" - "{result}" (expected "{expected}")')
        return False

def check_tool_completion(results):
    '''Check how many of the 5 expected tools returned results'''
    present = [t for t in EXPECTED_TOOLS if t in results]
    missing = [t for t in EXPECTED_TOOLS if t not in results]
    if missing:
        print(f'Tool Completion: {len(present)}/5 - Missing: {", ".join(missing)}')
    else:
        print(f'Tool Completion: 5/5')
    return len(present)

def check_weather(results):
    '''Check if weather data has a valid temperature and daily breakdown'''
    passed = 0
    weather = results.get('get_weather', {})

    if not isinstance(weather, dict):
        print(f'Weather: FAIL (not a dict)')
        return 0, 2

    temp = weather.get('temperature_f', 0)
    if temp and temp != 0:
        passed += 1
        print(f'Weather temp: PASS ({temp}F)')
    else:
        print(f'Weather temp: FAIL (got {temp})')

    daily = weather.get('daily', {})
    if daily and len(daily.get('time', [])) > 0:
        passed += 1
        print(f'Weather daily: PASS ({len(daily["time"])} days)')
    else:
        print(f'Weather daily: FAIL (no daily data)')

    return passed, 2

def check_country(results, expected_country, expected_capital):
    '''Check if country name and capital match expected values'''
    passed = 0
    info = results.get('get_country_info', {})

    if not isinstance(info, dict):
        print(f'Country info: FAIL (not a dict)')
        return 0, 2

    name = info.get('name', '')
    if expected_country.lower() in name.lower():
        passed += 1
        print(f'Country name: PASS ("{name}")')
    else:
        print(f'Country name: FAIL ("{name}", expected "{expected_country}")')

    capital = info.get('capital', '')
    if expected_capital.lower() in capital.lower():
        passed += 1
        print(f'Capital: PASS ("{capital}")')
    else:
        print(f'Capital: FAIL ("{capital}", expected "{expected_capital}")')

    return passed, 2

def check_airports(results):
    '''Check if airports returned a non-empty list'''
    airports = results.get('get_closest_airport', [])
    if isinstance(airports, list) and len(airports) > 0:
        print(f'Airports: PASS ({len(airports)} found)')
        return 1
    else:
        print(f'Airports: FAIL ({airports})')
        return 0

def check_packing(results):
    '''Check if packing list has more than 5 items'''
    packing = results.get('get_packing_list', [])
    if isinstance(packing, list) and len(packing) > 5:
        print(f'Packing list: PASS ({len(packing)} items)')
        return 1
    else:
        print(f'Packing list: FAIL ({type(packing)})')
        return 0

def check_currency(results):
    '''Check if currency conversion returned a positive number'''
    conversion = results.get('convert_currency')
    if isinstance(conversion, (int, float)) and conversion > 0:
        print(f'Currency: PASS ({conversion})')
        return 1
    else:
        print(f'Currency: FAIL ({conversion})')
        return 0


def run_evaluation():
    print('Test: Alias Handling')
    alias_passed = 0
    for input_val, alias_dict, expected in ALIAS_TESTS:
        if check_alias(input_val, alias_dict, expected):
            alias_passed += 1
    alias_total = len(ALIAS_TESTS)
    print(f'Alias Results: {alias_passed}/{alias_total} ({alias_passed/alias_total*100:.0f}%)\n')

    print('Test: Tool Completion and Data Quality')
    tool_score = 0
    tool_max = 0
    quality_score = 0
    quality_max = 0

    for i, (city, country, expected_country, expected_capital) in enumerate(TEST_CASES):
        if i > 0:
            time.sleep(5)
        print(f'\n[{city}, {country}]')

        results = run_agent(city, country, START_DATE, END_DATE)

        if 'error' in results:
            print(f'ERROR: {results["error"]}')
            tool_max += 5
            quality_max += 7
            continue

        # Tool completion
        tool_score += check_tool_completion(results)
        tool_max += 5

        # Data quality checks
        weather_passed, weather_total = check_weather(results)
        quality_score += weather_passed
        quality_max += weather_total

        country_passed, country_total = check_country(results, expected_country, expected_capital)
        quality_score += country_passed
        quality_max += country_total

        quality_score += check_airports(results)
        quality_max += 1

        quality_score += check_packing(results)
        quality_max += 1

        quality_score += check_currency(results)
        quality_max += 1

    # Results
    alias_percent = alias_passed / alias_total * 100
    tool_percent = tool_score / tool_max * 100 if tool_max > 0 else 0
    quality_percent = quality_score / quality_max * 100 if quality_max > 0 else 0

    print(f'\nRESULTS')
    print(f'Alias Handling: {alias_passed}/{alias_total} ({alias_percent:.0f}%)')
    print(f'Tool Completion: {tool_score}/{tool_max} ({tool_percent:.0f}%)')
    print(f'Data Quality: {quality_score}/{quality_max} ({quality_percent:.0f}%)')

    overall_score = alias_passed + tool_score + quality_score
    overall_total = alias_total + tool_max + quality_max
    overall_percent = overall_score / overall_total * 100
    print(f'Overall Score: {overall_score}/{overall_total} ({overall_percent:.0f}%)')


if __name__ == '__main__':
    run_evaluation()