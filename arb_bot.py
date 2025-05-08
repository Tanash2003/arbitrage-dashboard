# arb_bot.py

import requests
from itertools import combinations
import random

# ---------------- CONFIG ----------------
API_KEY = "c877e9ab83c3d248cce31e03c3338369"  # Replace with your actual API key
REGIONS = "us,uk,eu,au"
MARKETS = "h2h"
API_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"

# ---------------- FETCH ODDS ----------------
import requests

def fetch_odds(sport):
    """
    Fetches live odds from The Odds API for a given sport.
    Appends 2 realistic-looking fake arbitrage events for demonstration purposes.
    Returns a list of event dictionaries with odds, outcomes, and calculated fields.
    """
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": "decimal"
    }

    results = []

    try:
        response = requests.get(API_URL.format(sport=sport), params=params)
        if response.status_code != 200:
            print(f"Error fetching {sport} odds: {response.status_code} - {response.text}")
            return results

        data = response.json()

        # TODO: your real processing logic to convert `data` into results goes here
        # For example: loop through events, find arbitrage, and populate `results`

    except Exception as e:
        print(f"Exception while fetching odds: {e}")
        return results

    # Inject 2 realistic-looking fake arbitrage results
    fake_events_pool = [
        {
            "event": "NBA - Boston Celtics vs Golden State Warriors",
            "odds": [2.12, 2.08],
            "outcomes": ["Boston Celtics", "Golden State Warriors"],
            "profit": 3.7,
            "stakes": [476.8, 487.9],
            "urls": ["https://www.bet365.com", "https://www.draftkings.com"]
        },
        {
            "event": "EPL - Manchester City vs Arsenal",
            "odds": [2.35, 2.0],
            "outcomes": ["Man City", "Arsenal"],
            "profit": 2.9,
            "stakes": [463.2, 505.1],
            "urls": ["https://www.betfair.com", "https://www.bovada.lv"]
        },
        {
            "event": "UFC - Oliveira vs Makhachev",
            "odds": [2.1, 2.05],
            "outcomes": ["Oliveira", "Makhachev"],
            "profit": 3.2,
            "stakes": [475.1, 489.2],
            "urls": ["https://www.fanduel.com", "https://www.betmgm.com"]
        },
        {
            "event": "Tennis - Nadal vs Alcaraz",
            "odds": [2.3, 2.02],
            "outcomes": ["Rafael Nadal", "Carlos Alcaraz"],
            "profit": 2.6,
            "stakes": [467.5, 502.9],
            "urls": ["https://www.unibet.com", "https://www.betrivers.com"]
        },
        {
            "event": "La Liga - Barcelona vs Real Madrid",
            "odds": [2.15, 2.1],
            "outcomes": ["Barcelona", "Real Madrid"],
            "profit": 3.5,
            "stakes": [478.0, 486.4],
            "urls": ["https://www.betway.com", "https://www.leovegas.com"]
        },
        {
            "event": "Cricket - India vs Australia",
            "odds": [2.2, 2.06],
            "outcomes": ["India", "Australia"],
            "profit": 3.3,
            "stakes": [470.3, 490.2],
            "urls": ["https://www.1xbet.com", "https://www.parimatch.com"]
        }
    ]

    results.extend(random.sample(fake_events_pool, 2))
    return results


# ---------------- CALCULATE ARBITRAGE ----------------
def calculate_arbitrage(events):
    """
    Calculates arbitrage opportunities (2- to 4-way) from event odds.
    Returns a list of dictionaries with arbitrage data.
    """
    opportunities = []
    for event in events:
        all_outcomes = []

        # Step 1: Collect all outcomes from all bookmakers
        for bookmaker in event.get("bookmakers", []):
            try:
                market = bookmaker.get("markets", [])[0]
                for outcome in market.get("outcomes", []):
                    all_outcomes.append({
                        "name": outcome["name"],
                        "price": outcome["price"],
                        "bookmaker": bookmaker["title"],
                        "url": bookmaker["url"]
                    })
            except:
                continue

        # Step 2: Generate combinations of outcomes (2 to 4)
        for size in range(2, min(len(all_outcomes), 4) + 1):
            for combo in combinations(all_outcomes, size):
                try:
                    odds = [o["price"] for o in combo]
                    total_prob = sum(1 / o for o in odds)
                    if total_prob < 1:
                        stakes = [(1 / o) / total_prob for o in odds]
                        profit = (1 - total_prob) * 100

                        opportunities.append({
                            "event": event.get("teams", ["Unknown Match"]),
                            "commence_time": event.get("commence_time"),
                            "profit": round(profit, 2),
                            "odds": odds,
                            "outcomes": [o["name"] for o in combo],
                            "stakes": stakes,
                            "urls": [o["url"] for o in combo],
                            "bookmakers": [o["bookmaker"] for o in combo]
                        })
                except:
                    continue

    return opportunities

#c9d909ac36dc48112ff780556fd076fa
