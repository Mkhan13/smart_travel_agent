import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('CURRENCY_API_KEY')

def convert_currency(from_currency, to_currency, amount):
    '''Convert currency using ExchangeRate API'''
    url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/pair/{from_currency}/{to_currency}/{amount}'
    data = requests.get(url).json()

    if data['result'] != 'success':
        return 'Conversion failed'

    return data['conversion_result']
