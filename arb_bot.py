import requests
import random

API_KEY = "c9d909ac36dc48112ff780556fd076fa"  # Replace with your real API Key
API_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds/"
REGIONS = "us,uk,in"  # Example: US, UK, India regions
MARKETS = "h2h"  # Head-to-head market for two-outcome events


def fetch_odds(sport):
    """
    Fetches live odds from The Odds API for a given sport.
    Returns raw event data as JSON.
    """
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "decimal"
    }

    try:
        response = requests.get(API_URL.format(sport=sport), params=params)
        if response.status_code != 200:
            print(f"Error fetching {sport} odds: {response.status_code} - {response.text}")
            return []
        return response.json()
    except Exception as e:
        print(f"Exception while fetching odds: {e}")
        return []


def calculate_arbitrage(events):
    """
    Processes raw event data to calculate arbitrage opportunities.
    Returns a list of dictionaries with event, profit %, stakes, and outcome details.
    """
    arbitrage_opportunities = []

    for event in events:
        try:
            teams = event.get("teams", [])
            bookmakers = event.get("bookmakers", [])

            if not teams or not bookmakers:
                continue

            odds_data = []
            for bookmaker in bookmakers:
                market = next((m for m in bookmaker["markets"] if m["key"] == "h2h"), None)
                if market and len(market["outcomes"]) >= 2:
                    prices = [outcome["price"] for outcome in market["outcomes"][:2]]
                    odds_data.append({
                        "bookmaker": bookmaker["title"],
                        "url": bookmaker["url"],
                        "odds": prices,
                        "outcomes": [o["name"] for o in market["outcomes"][:2]]
                    })

            # Simple 2-way arbitrage check
            if len(odds_data) < 2:
                continue

            best_odds = [0, 0]
            best_urls = ["", ""]
            best_outcomes = ["", ""]

            for data in odds_data:
                if data["odds"][0] > best_odds[0]:
                    best_odds[0] = data["odds"][0]
                    best_urls[0] = data["url"]
                    best_outcomes[0] = data["outcomes"][0]
                if data["odds"][1] > best_odds[1]:
                    best_odds[1] = data["odds"][1]
                    best_urls[1] = data["url"]
                    best_outcomes[1] = data["outcomes"][1]

            implied_sum = (1 / best_odds[0]) + (1 / best_odds[1])

            if implied_sum < 1:
                profit_percent = (1 - implied_sum) * 100
                capital = 1000  # Fixed test capital
                stakes = [
                    round((capital / best_odds[0]) / implied_sum, 2),
                    round((capital / best_odds[1]) / implied_sum, 2)
                ]

                arbitrage_opportunities.append({
                    "event": event.get("event", "Unknown Event"),
                    "odds": best_odds,
                    "outcomes": best_outcomes,
                    "profit": round(profit_percent, 2),
                    "stakes": stakes,
                    "urls": best_urls
                })

        except Exception as e:
            print(f"Error processing event: {e}")

    return arbitrage_opportunities


def inject_fake_events():
    """
    Returns two fake arbitrage events processed through calculate_arbitrage().
    """
    fake_events = [
        {
            "teams": ["Boston Celtics", "Golden State Warriors"],
            "bookmakers": [{
                "title": "bet365",
                "url": "https://www.bet365.com",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Boston Celtics", "price": 2.12},
                        {"name": "Golden State Warriors", "price": 2.08}
                    ]
                }]
            }]
        },
        {
            "teams": ["India", "Australia"],
            "bookmakers": [{
                "title": "1xBet",
                "url": "https://www.1xbet.com",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "India", "price": 2.20},
                        {"name": "Australia", "price": 2.06}
                    ]
                }]
            }]
        },
        {
            "teams": ["Barcelona", "Real Madrid"],
            "bookmakers": [{
                "title": "Betway",
                "url": "https://www.betway.com",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Barcelona", "price": 2.15},
                        {"name": "Real Madrid", "price": 2.10}
                    ]
                }]
            }]
        }
    ]

    return calculate_arbitrage(random.sample(fake_events, 2))


#c9d909ac36dc48112ff780556fd076fa
