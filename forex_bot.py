# forex_bot.py

import requests
from itertools import permutations
import time

EXCHANGES = ["Exchange A", "Exchange B"]  # Simulated spreads

# ----------------------------------------
def get_all_currency_symbols():
    """
    Fetch all available currency codes from exchangerate.host.
    """
    url = "https://api.exchangerate.host/symbols"
    try:
        res = requests.get(url).json()
        return sorted(list(res["symbols"].keys()))
    except:
        return ["USD", "EUR", "GBP", "INR", "JPY"]

# ----------------------------------------
def fetch_forex_batch(pairs, delay=1):
    """
    Fetches forex rates in batch. Simulates exchange spreads.
    """
    results = {}
    for base, quote in pairs:
        url = f"https://api.exchangerate.host/latest?base={base}&symbols={quote}"
        try:
            res = requests.get(url).json()
            mid = res["rates"].get(quote)
            if mid:
                spread = mid * 0.0025  # 0.25% simulated bid-ask
                results[f"{base}/{quote}"] = {
                    EXCHANGES[0]: round(mid - spread / 2, 5),
                    EXCHANGES[1]: round(mid + spread / 2, 5)
                }
        except:
            continue
        time.sleep(delay)  # avoid overloading API
    return results

# ----------------------------------------
def detect_forex_arbitrage(fx_data, threshold=0.1):
    """
    Identifies arbitrage between simulated exchanges.
    """
    opps = []
    for pair, rates in fx_data.items():
        vals = list(rates.values())
        if len(vals) < 2:
            continue
        buy = min(vals)
        sell = max(vals)
        if sell > buy:
            profit = ((sell - buy) / buy) * 100
            if profit > threshold:
                opps.append({
                    "Currency Pair": pair,
                    "Buy From": min(rates, key=rates.get),
                    "Sell To": max(rates, key=rates.get),
                    "Buy Rate": round(buy, 5),
                    "Sell Rate": round(sell, 5),
                    "Profit %": round(profit, 2)
                })
    return opps
