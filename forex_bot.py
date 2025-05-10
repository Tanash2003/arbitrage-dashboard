import requests
from itertools import permutations
import time

EXCHANGES = ["Bet365 Forex", "FXTM"]  # Simulated exchange names

def get_all_currency_symbols():
    """
    Fetch all available currency codes from exchangerate.host.
    """
    url = "https://api.exchangerate.host/symbols"
    try:
        res = requests.get(url).json()
        return sorted(list(res["symbols"].keys()))
    except Exception as e:
        print(f"Error fetching currency symbols: {e}")
        return ["USD", "EUR", "GBP", "INR", "JPY"]  # Fallback

def fetch_forex_batch(selected_currencies, global_mode=False, batch_size=300, delay=0.1):
    """
    Fetches forex rates in batch. Supports global scan and simulates exchange spreads.
    """
    results = {}
    if global_mode:
        all_currencies = get_all_currency_symbols()
        pairs = list(permutations(all_currencies, 2))
    else:
        pairs = list(permutations(selected_currencies, 2))

    pairs = pairs[:batch_size]  # Limit total pairs processed

    for base, quote in pairs:
        url = f"https://api.exchangerate.host/latest?base={base}&symbols={quote}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                print(f"Error fetching {base}/{quote}: {response.status_code} - {response.text}")
                continue

            res = response.json()
            mid = res["rates"].get(quote)
            if mid:
                # Simulate a variable spread between exchanges (0.1% to 0.5%)
                spread_percent = round(random.uniform(0.001, 0.005), 5)
                spread = mid * spread_percent

                results[f"{base}/{quote}"] = {
                    EXCHANGES[0]: round(mid - spread / 2, 5),
                    EXCHANGES[1]: round(mid + spread / 2, 5)
                }
        except Exception as e:
            print(f"Error fetching forex rate for {base}/{quote}: {e}")
            continue

        time.sleep(delay)  # Avoid API rate limits

    return results

def detect_forex_arbitrage(fx_data, min_profit_threshold=0.1):
    """
    Identifies arbitrage opportunities between simulated exchanges.
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
            if profit >= min_profit_threshold:
                opps.append({
                    "Currency Pair": pair,
                    "Buy From": min(rates, key=rates.get),
                    "Sell To": max(rates, key=rates.get),
                    "Buy Rate": round(buy, 5),
                    "Sell Rate": round(sell, 5),
                    "Profit %": round(profit, 2)
                })
    return opps
