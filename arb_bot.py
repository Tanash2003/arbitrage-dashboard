# arb_bot.py

import requests
from itertools import combinations

# ---------------- CONFIG ----------------
API_KEY = "c877e9ab83c3d248cce31e03c3338369"  # Replace with your actual API key
REGIONS = "us,uk,eu,au"
MARKETS = "h2h"
API_URL = "https://api.the-odds-api.com/v4/sports/{sport}/odds"

# ---------------- FETCH ODDS ----------------
def fetch_odds(sport):
    """
    Fetches live odds from The Odds API for a given sport.
    Returns a list of events with bookmaker odds data.
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