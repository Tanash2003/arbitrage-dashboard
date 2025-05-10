import requests
import random
import os

# API Configuration
API_KEY = os.getenv("dcf4fc271ce80bf8fc89009d33d8aef4")  # Store API Key securely
API_URL = "https://api.sportsgameodds.com/v1/odds"  # Example URL, confirm with documentation
REGION = "us"  # Adjust based on your market focus
MARKET = "moneyline"  # Assuming 2-way markets; change if needed

def fetch_odds(sport):
    """
    Fetches live odds from Sports Game Odds API for a given sport.
    Returns raw event data as JSON.
    """
    params = {
        "apiKey": API_KEY,
        "sport": sport,  # Example: 'basketball_nba', 'soccer_epl'
        "region": REGION,
        "market": MARKET
    }

    try:
        response = requests.get(API_URL, params=params)
        if response.status_code != 200:
            print(f"Error fetching {sport} odds: {response.status_code} - {response.text}")
            return []
        return response.json()
    except Exception as e:
        print(f"Exception while fetching odds: {e}")
        return []

def calculate_arbitrage(events, min_profit_threshold=0.5):
    """
    Calculates arbitrage opportunities from event data.
    Returns a list of dictionaries with event, profit %, stakes, outcomes, and bookmaker URLs.
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
                markets = bookmaker.get("markets", [])
                market = next((m for m in markets if m.get("key") == MARKET), None)
                if market and len(market.get("outcomes", [])) >= 2:
                    prices = [float(outcome["price"]) for outcome in market["outcomes"][:2]]
                    odds_data.append({
                        "bookmaker": bookmaker["title"],
                        "url": bookmaker.get("url", ""),
                        "odds": prices,
                        "outcomes": [outcome["name"] for outcome in market["outcomes"][:2]]
                    })

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
                if profit_percent >= min_profit_threshold:
                    capital = 1000  # Base capital for stake calculations
                    stakes = [
                        round((capital / best_odds[0]) / implied_sum, 2),
                        round((capital / best_odds[1]) / implied_sum, 2)
                    ]

                    arbitrage_opportunities.append({
                        "event": event.get("name", "Unknown Event"),
                        "odds": best_odds,
                        "outcomes": best_outcomes,
                        "profit": round(profit_percent, 2),
                        "stakes": stakes,
                        "urls": best_urls
                    })

        except Exception as e:
            print(f"Error processing event: {e}")
            continue

    return arbitrage_opportunities

def inject_fake_events(num_events=3):
    """
    Generates realistic-looking fake arbitrage events for demonstration purposes.
    Rotates events dynamically to simulate live data with realistic profit margins and bookmaker names.
    """
    sample_events = [
        ("Lakers", "Celtics"),
        ("Arsenal", "Manchester City"),
        ("Oscar Piastri", "Lando Norris"),
        ("Djokovic", "Alcaraz"),
        ("Red Bull", "Ferrari"),
        ("Real Madrid", "Barcelona"),
        ("Golden State Warriors", "Miami Heat"),
        ("Liverpool", "Chelsea"),
        ("Oklahoma Athletics", "Boston Red Sox"),
        ("Nadal", "Medvedev")
    ]

    fake_events = []
    selected_matches = random.sample(sample_events, num_events)

    for team_a, team_b in selected_matches:
        odds = [round(random.uniform(1.5, 3.5), 2), round(random.uniform(1.5, 3.5), 2)]
        implied_sum = sum(1 / odd for odd in odds)

        if implied_sum < 1:
            profit_percent = round(random.uniform(2.0, 15.0), 2)  # Realistic profit margin
            capital = 1000
            stakes = [round((capital / odd) / implied_sum, 2) for odd in odds]

            bookmakers = random.sample(['Bet365', 'William Hill', 'DraftKings', 'Betway', 'Bwin'], 2)
            urls = [f"https://{bk.lower().replace(' ', '')}.com" for bk in bookmakers]

            fake_events.append({
                "event": f"{team_a} vs {team_b}",
                "odds": odds,
                "outcomes": [team_a, team_b],
                "profit": profit_percent,
                "stakes": stakes,
                "urls": urls,
                "bookmakers": bookmakers
            })

    return fake_events



#c9d909ac36dc48112ff780556fd076fa
