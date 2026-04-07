import streamlit as st
from datetime import date, datetime, timedelta
from agent import run_agent

st.set_page_config(page_title='Smart Travel Agent', layout='wide')

# Styling
st.markdown('''
<style>
    .country-box {
        background-color: #e8f4e8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        margin-bottom: 15px;
    }
    [data-key="weather_container"] {
        background-color: #e3f2fd !important;
        border-left: 5px solid #1565c0 !important;
        border-radius: 10px;
    }
    .airport-box {
        background-color: #fff3e0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #e65100;
        margin-bottom: 15px;
    }
    .currency-box {
        background-color: #fce4ec;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ad1457;
        margin-bottom: 15px;
    }
    [data-key="packing_container"] {
        background-color: #f3e5f5 !important;
        border-left: 5px solid #6a1b9a !important;
        border-radius: 10px;
    }
    .country-heading { color: #2e7d32; text-align: center; }
    .weather-heading { color: #1565c0; text-align: center; }
    .airport-heading { color: #e65100; text-align: center; }
    .currency-heading { color: #ad1457; text-align: center; }
    .packing-heading { color: #6a1b9a; text-align: center; }
</style>
''', unsafe_allow_html=True)

def celsius_to_fahrenheit(temp_c):
    '''Convert Celsius to Fahrenheit'''
    if temp_c is None:
        return 'N/A'
    return round(temp_c * 9/5 + 32, 1)


def format_date(date_str):
    '''Convert YYYY-MM-DD to MM/DD/YYYY'''
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%m/%d/%Y')


def format_population(population):
    '''Format population with commas, or N/A if not a number'''
    if isinstance(population, int):
        return f'{population:,}'
    return 'N/A'


def get_currency_code(info):
    '''Extract the currency code from the country info currency string.
    Example: "euro (EUR)" returns "EUR"'''
    if not isinstance(info, dict):
        return ''
    currency_str = info.get('currency', '')
    if '(' not in currency_str:
        return ''
    return currency_str.split('(')[-1].replace(')', '').strip()


def clear_packing():
    '''Remove all packing checkbox states from session'''
    for key in list(st.session_state.keys()):
        if key.startswith('pack_'):
            del st.session_state[key]


def show_country_info(info):
    '''Display the country info section'''
    st.markdown('<h3 class="country-heading">Country Info</h3>', unsafe_allow_html=True)

    if not isinstance(info, dict):
        st.warning(info)
        return

    population = format_population(info.get('population', 'N/A'))

    st.markdown(f'''
<div class="country-box">

| | |
|---|---|
| **Capital** | {info.get('capital', 'N/A')} |
| **Language** | {info.get('language', 'N/A')} |
| **Currency** | {info.get('currency', 'N/A')} |
| **Timezone** | {info.get('timezone', 'N/A')} |
| **Calling Code** | {info.get('calling_code', 'N/A')} |
| **Driving Side** | {info.get('driving_side', 'N/A')} |
| **Population** | {population} |

</div>
''', unsafe_allow_html=True)


def show_airports(airports):
    '''Display the nearest airports section'''
    st.markdown('<h3 class="airport-heading">Nearest Airports</h3>', unsafe_allow_html=True)

    if not isinstance(airports, list):
        st.warning(airports)
        return

    airport_items = ''
    for airport in airports:
        airport_items += f'<li>{airport}</li>'
    st.markdown(f'<div class="airport-box"><ul>{airport_items}</ul></div>', unsafe_allow_html=True)


def show_weather(weather):
    '''Display the weather forecast section'''
    st.markdown('<h3 class="weather-heading">Weather Forecast</h3>', unsafe_allow_html=True)

    if not isinstance(weather, dict):
        st.warning(weather)
        return

    with st.container(border=True, key='weather_container'):
        # Summary metrics
        m1, m2, m3 = st.columns(3)
        m1.metric('Temperature', f"{weather.get('temperature_c', 'N/A')}C / {weather.get('temperature_f', 'N/A')}F")
        m2.metric('Wind', f"{weather.get('wind_speed_kmh', 'N/A')} km/h")
        m3.metric('Avg Precip', f"{weather.get('avg_daily_precip_mm', 'N/A')} mm/day")

        if weather.get('will_rain'):
            st.info('Rain is likely during your trip. Pack an umbrella.')

        # Daily breakdown table
        daily = weather.get('daily', {})
        if daily and 'time' in daily:
            with st.expander('Daily Breakdown'):
                rows = []
                for i, day in enumerate(daily['time']):
                    high_c = daily.get('temperature_2m_max', [None])[i]
                    low_c = daily.get('temperature_2m_min', [None])[i]
                    high_f = celsius_to_fahrenheit(high_c)
                    low_f = celsius_to_fahrenheit(low_c)
                    precip = daily.get('precipitation_sum', [None])[i]
                    rows.append(f'| {format_date(day)} | {high_c}C / {high_f}F | {low_c}C / {low_f}F | {precip} mm |')

                table = '| Date | High | Low | Precipitation |\n|---|---|---|---|\n' + '\n'.join(rows)
                st.markdown(table)

def show_currency(conversion, local_code):
    '''Display the currency converter section'''
    st.markdown('<h3 class="currency-heading">Currency Converter</h3>', unsafe_allow_html=True)

    # Show the initial 100 USD conversion
    if conversion and local_code:
        st.markdown(
            f'<div class="currency-box"><strong>100 USD = {conversion:.2f} {local_code}</strong></div>',
            unsafe_allow_html=True,
        )

    # Currency dropdown options
    currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'MXN', 'BRL', 'KRW', 'SEK', 'NOK', 'DKK', 'NZD', 'SGD', 'HKD', 'TRY', 'ZAR', 'THB', 'PHP', 'MYR', 'IDR', 'AED', 'SAR', 'EGP', 'PKR']

    to_index = 1
    if local_code and local_code in currencies:
        to_index = currencies.index(local_code) # Default dropdown to the destination country's currency

    # Converter form
    with st.form('currency_form'):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            amount = st.number_input('Amount', value=100.0, min_value=0.0)
        with cc2:
            from_cur = st.selectbox('From', currencies, index=0)
        with cc3:
            to_cur = st.selectbox('To', currencies, index=to_index)
        convert_btn = st.form_submit_button('Convert')

    if convert_btn:
        from tools.currency import convert_currency
        result = convert_currency(from_cur, to_cur, amount)
        if isinstance(result, str):
            st.error(result)
        else:
            st.success(f'{amount} {from_cur} = {result:.2f} {to_cur}')

def show_packing(packing):
    '''Display the packing list section'''
    st.markdown('<h3 class="packing-heading">Packing List</h3>', unsafe_allow_html=True)

    if isinstance(packing, dict) and 'error' in packing:
        st.warning(packing['error'])
    elif isinstance(packing, list):
        with st.container(border=True, key='packing_container'):
            cols = st.columns(3)
            for i, item in enumerate(packing):
                with cols[i % 3]:
                    st.checkbox(item, key=f'pack_{item}')
    else:
        st.warning(packing)


st.title('Smart Travel Agent')

# Input section
with st.form('trip_form'):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        city = st.text_input('City', placeholder='e.g. Paris')
    with col2:
        country = st.text_input('Country', placeholder='e.g. France')
    with col3:
        departure_date = st.date_input('Departure Date', value=date.today(), format='MM/DD/YYYY')
    with col4:
        return_date = st.date_input('Return Date', value=date.today(), format='MM/DD/YYYY')

    btn1, btn2 = st.columns(2)
    with btn1:
        submitted = st.form_submit_button('Plan My Trip', use_container_width=True)
    with btn2:
        reset = st.form_submit_button('Reset Trip', use_container_width=True)

# Reset to clear all results and checkboxes
if reset:
    st.session_state.pop('results', None)
    st.session_state.pop('trip_info', None)
    clear_packing()
    st.rerun()

if submitted: # Validate inputs
    if not city or not country:
        st.error('Please enter both a city and a country.')
    elif return_date <= departure_date:
        st.error('Return date must be after departure date.')
    elif (return_date - date.today()).days > 16:
        st.error('Return date must be within 16 days from today for accurate weather data.')
    else: # Get data
        with st.spinner('Planning your trip...'):
            st.session_state.results = run_agent(city, country, str(departure_date), str(return_date))
            st.session_state.trip_info = {
                'city': city,
                'country': country,
                'departure': departure_date,
                'return': return_date,
            }
            clear_packing()

if 'results' in st.session_state: # Results dashboard
    results = st.session_state.results
    trip = st.session_state.trip_info
    city = trip['city']
    country = trip['country']
    departure_date = trip['departure']
    return_date = trip['return']
    trip_days = (return_date - departure_date).days

    if 'error' in results:
        st.error(results['error'])
    else:
        st.divider()
        st.subheader(f'{city}, {country} - {trip_days} days ({departure_date.strftime("%m/%d/%Y")} to {return_date.strftime("%m/%d/%Y")})')

        info = results.get('get_country_info', {})
        local_code = get_currency_code(info)

        col_left, col_right = st.columns(2)

        with col_left:
            show_country_info(info)
            show_airports(results.get('get_closest_airport', []))

        with col_right:
            show_weather(results.get('get_weather', {}))
            show_currency(results.get('convert_currency'), local_code)

        # Full width: packing list
        show_packing(results.get('get_packing_list', []))
