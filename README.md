# Smart Travel Agent

## How It Works

The agent loop is in `agent.py`. After the user enters a city, country, and travel dates, the agent sends the user's trip details to the LLM along with tool definitions. The model decides which tools to call and with what arguments. The agent uses Groq's API with Llama 3.3 70B to plan tool calls, and presents results through a Streamlit dashboard.

## Tools

| Tool | Description | API |
|---|---|---|
| **Weather Forecast** | Returns average temperature, wind speed, precipitation, and daily breakdown for the travel dates | Open-Meteo |
| **Closest Airports** | Finds the 3 nearest international airports to the destination city | OpenStreetMap Overpass |
| **Packing List** | Generates a packing list with weather-appropriate items based on live forecast data | Uses weather tool internally |
| **Country Info** | Returns capital, language, currency, timezone, calling code, driving side, and population | REST Countries |
| **Currency Converter** | Converts between currencies (defaults to 100 USD to local currency) | ExchangeRate API |

## Evaluation

The evaluation uses custom test cases that were written to cover a range of scenarios: different continents, different climates, alias inputs, and varying country data formats. Each test case includes the expected country name and capital so the evaluation can verify correctness automatically.

The evaluation tests three areas:

**Alias Handling** - Tests that city and country aliases (e.g. "usa", "nyc", "uk") are correctly normalized before being sent to the tools. 12 test cases covering common abbreviations and nicknames.

**Tool Completion** - Runs the full agent for 6 cities (Paris, London, Tokyo, Chicago, Sydney, Toronto) and checks that all 5 tools return results for each.

**Data Quality** - Validates that tool outputs contain sensible data:

- Weather has a valid temperature and daily breakdown
- Country name and capital match expected values
- Airports returns a non-empty list
- Packing list has more than 5 items
- Currency conversion returns a positive number

### Results

```
Alias Handling: 12/12 (100%)
Tool Completion: 30/30 (100%)
Data Quality: 39/42 (93%)
Overall Score: 81/84 (96%)
```

The 3 data quality failures are all from the airport tool. The OpenStreetMap Overpass API has strict rate limits, so when running 6 test cases back to back, some requests get temporarily blocked. This is an API limitation, not a bug in the agent. A 5 second delay between test cases is used to reduce this, but it does not fully prevent it.

## Setup

Requires at least Python 3.12, a [Groq API key](https://console.groq.com), and an [ExchangeRate API key](https://www.exchangerate-api.com). Install project requirements:

```
pip install -r requirements.txt
```

Create a `.env` file in the project root and add your API keys:

```
GROQ_API_KEY=
CURRENCY_API_KEY=
```

Run the app:

```
streamlit run main.py
```

Run the evaluation:

```
python evaluation.py
```
