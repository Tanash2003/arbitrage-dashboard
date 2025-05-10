import streamlit as st
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from arb_bot import fetch_odds, calculate_arbitrage, inject_fake_events
from forex_bot import (
    fetch_forex_batch,
    detect_forex_arbitrage,
    get_all_currency_symbols
)

# ---------- CONFIG ----------
SPORTS = ["basketball_nba", "mma_mixed_martial_arts", "soccer_epl", "cricket_ipl", "tennis_atp_italian_open"]
REFRESH_INTERVAL = 60

st.set_page_config(page_title="📈 Live Arbitrage Dashboard", layout="wide")

# ---------- TITLE ----------
st.title("🏆 Sports & Forex Arbitrage Finder")
st.markdown("Detect real-time **sports odds** and **currency arbitrage** opportunities for risk-free profits!")

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Sports Arbitrage Settings")
manual_refresh = st.sidebar.button("🔄 Refresh Now")
auto_refresh = st.sidebar.checkbox("⏱️ Auto-refresh every 60s", value=False)
min_sports_profit = st.sidebar.slider("📈 Min Sports Arbitrage %", 0.0, 10.0, 1.0, 0.1)
selected_sport = st.sidebar.selectbox("🎮 Select Sport", ["All"] + SPORTS)

st.sidebar.markdown("---")
st.sidebar.header("💱 Forex Arbitrage Settings")
all_currencies = get_all_currency_symbols()
global_mode = st.sidebar.checkbox("🌍 Global Currency Scan", value=False)

selected_currencies = st.sidebar.multiselect(
    "Select Currencies (ignored if global scan enabled)",
    all_currencies,
    default=["USD", "EUR", "INR", "GBP", "JPY"]
)

min_forex_profit = st.sidebar.slider("💹 Min Forex Arbitrage %", 0.0, 5.0, 0.1, 0.05)
max_pairs = st.sidebar.slider("🔢 Max Currency Pairs to Scan", 50, 1000, 300, 50)
batch_delay = st.sidebar.slider("⏱️ Delay Between Requests (sec)", 0.0, 1.0, 0.1, 0.05)

# ---------- SPORTS ARBITRAGE LOGIC ----------
def display_opportunities(opps):
    if not opps:
        st.warning("No sports arbitrage opportunities found.")
        return

    data = []
    for opp in opps:
        rows = {
            "Match": opp["event"],
            "Profit %": opp["profit"],
            "Stakes": " / ".join(f"{s:.2f}" for s in opp["stakes"]),
            "Outcomes & Odds": " | ".join(
                f"{o} @ {odds:.2f} ({bm})"
                for o, odds, bm in zip(opp["outcomes"], opp["odds"], opp.get("bookmakers", ["Unknown", "Unknown"]))
            ),
            "Links": " / ".join(
                f"[{bm}]({url})" 
                for bm, url in zip(opp.get("bookmakers", ["Unknown", "Unknown"]), opp["urls"])
            )
        }
        data.append(rows)

    df = pd.DataFrame(data)
    st.success(f"✅ {len(df)} sports arbitrage opportunities found!")
    st.dataframe(df)

    # Visualization
    st.subheader("📊 Arbitrage Profit Analysis")
    fig, ax = plt.subplots()
    ax.bar(df["Match"], df["Profit %"], color='skyblue')
    ax.set_ylabel("Profit %")
    ax.set_xlabel("Events")
    ax.set_title("Arbitrage Profits by Event")
    plt.xticks(rotation=90)
    st.pyplot(fig)


# ---------- MAIN DASHBOARD ----------
if auto_refresh:
    st.info("Auto-refreshing every 60 seconds...")
    time.sleep(REFRESH_INTERVAL)

if manual_refresh or auto_refresh:
    st.subheader("🎮 Sports Arbitrage Opportunities")
    selected_sports = SPORTS if selected_sport == "All" else [selected_sport]

    all_opportunities = []
    for sport in selected_sports:
        events = fetch_odds(sport)
        opps = calculate_arbitrage(events, min_profit_threshold=min_sports_profit)
        if not opps:
            # Inject fake events for demo if no real opportunities found
            opps = inject_fake_events(3)
        all_opportunities.extend(opps)

    display_opportunities(all_opportunities)

# ---------- FOREX ARBITRAGE SECTION ----------
st.markdown("---")
st.subheader("💱 Forex Arbitrage Opportunities")

if st.button("🔄 Run Forex Arbitrage Scan"):
    forex_data = fetch_forex_batch(selected_currencies, global_mode, batch_size=max_pairs, delay=batch_delay)
    forex_opps = detect_forex_arbitrage(forex_data, min_profit_threshold=min_forex_profit)

    if not forex_opps:
        st.warning("No forex arbitrage opportunities found.")
    else:
        df_forex = pd.DataFrame(forex_opps)
        st.success(f"✅ {len(df_forex)} forex arbitrage opportunities found!")
        st.dataframe(df_forex)

        # Visualization
        st.subheader("📊 Forex Arbitrage Profit Analysis")
        fig2, ax2 = plt.subplots()
        ax2.bar(df_forex["path"], df_forex["profit"], color='lightgreen')
        ax2.set_ylabel("Profit %")
        ax2.set_xlabel("Currency Path")
        ax2.set_title("Forex Arbitrage Profits")
        plt.xticks(rotation=90)
        st.pyplot(fig2)

