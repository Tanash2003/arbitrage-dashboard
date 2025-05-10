import streamlit as st
import time
import pandas as pd
import matplotlib.pyplot as plt
import os
import random

from arb_bot import fetch_odds, calculate_arbitrage, inject_fake_events
from forex_bot import (
    fetch_forex_batch,
    detect_forex_arbitrage,
    get_all_currency_symbols
)

# ---------- CONFIG ----------
SPORTS = ["basketball_nba", "mma_mixed_martial_arts", "soccer_epl", "cricket_ipl", "tennis_atp_italian_open"]
EXCHANGES = ["Bet365 Forex", "FXTM"]
BOOKMARKS = []  # Temporary in-memory store
SESSION_PROFITS = []  # To track profit trends

st.set_page_config(page_title="📈 Arbitrage Dashboard", layout="wide")

# ---------- SIDEBAR CONTROLS ----------
st.sidebar.header("🎛️ Dashboard Settings")
if st.sidebar.checkbox("🌙 Enable Dark Mode"):
    st.markdown("""<style>body { background-color: #111; color: #eee; }</style>""", unsafe_allow_html=True)

st.sidebar.header("🎮 Sports Arbitrage Settings")
manual_refresh = st.sidebar.button("🔄 Refresh Sports Now")
auto_refresh = st.sidebar.checkbox("⏱️ Auto-refresh Sports every 60s", value=False)
min_sports_profit = st.sidebar.slider("📈 Min Sports Arbitrage %", 0.0, 10.0, 1.0, 0.1)
selected_sport = st.sidebar.selectbox("Select Sport", ["All"] + SPORTS)
bookmaker_filter = st.sidebar.multiselect("Filter by Bookmakers", ["Bet365", "William Hill", "DraftKings", "Betway", "Bwin"])

st.sidebar.markdown("---")
st.sidebar.header("💱 Forex Arbitrage Settings")
all_currencies = get_all_currency_symbols()
global_mode = st.sidebar.checkbox("🌍 Global Currency Scan", value=False)
selected_currencies = st.sidebar.multiselect("Select Currencies", all_currencies, default=["USD", "EUR", "INR", "GBP", "JPY"])
min_forex_profit = st.sidebar.slider("💹 Min Forex Arbitrage %", 0.0, 5.0, 0.1, 0.05)
max_pairs = st.sidebar.slider("🔢 Max Currency Pairs to Scan", 50, 1000, 300, 50)
batch_delay = st.sidebar.slider("⏱️ Delay Between Requests (sec)", 0.0, 1.0, 0.1, 0.05)

# ---------- SPORTS ARBITRAGE ----------
def display_opportunities(opps):
    if not opps:
        st.warning("No sports arbitrage opportunities found.")
        return

    data = []
    total_profit = 0
    for opp in opps:
        total_profit += opp["profit"]
        rows = {
            "Match": opp["event"],
            "Profit %": opp["profit"],
            "Stakes": " / ".join(f"{s:.2f}" for s in opp["stakes"]),
            "Outcomes & Odds": " | ".join(
                f"{o} @ {odds:.2f} ({bm})" for o, odds, bm in zip(opp["outcomes"], opp["odds"], opp.get("bookmakers", ["Unknown"] * 2))
            ),
            "Links": " / ".join(
                f"[{bm}]({url})" for bm, url in zip(opp.get("bookmakers", ["Unknown"] * 2), opp["urls"])
            ),
            "Bookmark": "⭐ Add"
        }
        data.append(rows)

    df = pd.DataFrame(data)
    st.success(f"✅ {len(df)} sports arbitrage opportunities found!")
    st.dataframe(df)

    for idx, row in df.iterrows():
        if st.button(f"⭐ Bookmark", key=f"bookmark_{idx}"):
            BOOKMARKS.append(row)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Sports Data as CSV", csv, "sports_arbitrage.csv", "text/csv")

    st.subheader("📊 Arbitrage Profit Analysis")
    fig, ax = plt.subplots()
    ax.bar(df["Match"], df["Profit %"], color='skyblue')
    ax.set_ylabel("Profit %")
    ax.set_xlabel("Events")
    ax.set_title("Arbitrage Profits by Event")
    plt.xticks(rotation=90)
    st.pyplot(fig)

    # Pie Chart for Stake Distribution
    st.subheader("🥧 Stake Distribution")
    fig_pie, ax_pie = plt.subplots()
    stakes_values = [float(s.split("/")[0]) for s in df["Stakes"]]
    ax_pie.pie(stakes_values, labels=df["Match"], autopct='%1.1f%%')
    ax_pie.axis('equal')
    st.pyplot(fig_pie)

    # Track profit trend
    SESSION_PROFITS.append(total_profit)

    # Profit Trend Chart
    st.subheader("📈 Profit Trend During Session")
    fig_trend, ax_trend = plt.subplots()
    ax_trend.plot(SESSION_PROFITS, marker='o', linestyle='-', color='green')
    ax_trend.set_ylabel("Total Profit %")
    ax_trend.set_xlabel("Scan Iterations")
    ax_trend.set_title("Session Profit Trend")
    st.pyplot(fig_trend)

# ---------- MAIN DASHBOARD ----------
st.title("🏆 Sports & Forex Arbitrage Finder")
st.markdown("Detect real-time **sports odds** and **currency arbitrage** opportunities for risk-free profits!")

if auto_refresh:
    st.info("Auto-refreshing every 60 seconds...")
    time.sleep(60)

if manual_refresh or auto_refresh:
    st.subheader("🎮 Sports Arbitrage Opportunities")
    selected_sports = SPORTS if selected_sport == "All" else [selected_sport]
    all_opportunities = []

    for sport in selected_sports:
        events = fetch_odds(sport)
        opps = calculate_arbitrage(events, min_profit_threshold=min_sports_profit)
        if not opps:
            opps = inject_fake_events(3)
        all_opportunities.extend(opps)

    if bookmaker_filter:
        all_opportunities = [op for op in all_opportunities if any(bm in bookmaker_filter for bm in op.get("bookmakers", []))]

    display_opportunities(all_opportunities)

# ---------- FOREX ARBITRAGE ----------
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

        csv_forex = df_forex.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Forex Data as CSV", csv_forex, "forex_arbitrage.csv", "text/csv")

        st.subheader("📊 Forex Arbitrage Profit Analysis")
        fig2, ax2 = plt.subplots()
        ax2.bar(df_forex["Currency Pair"], df_forex["Profit %"], color='lightgreen')
        ax2.set_ylabel("Profit %")
        ax2.set_xlabel("Currency Pair")
        ax2.set_title("Forex Arbitrage Profits")
        plt.xticks(rotation=90)
        st.pyplot(fig2)

# ---------- BOOKMARKED OPPORTUNITIES ----------
if BOOKMARKS:
    st.markdown("---")
    st.subheader("⭐ Bookmarked Opportunities")
    df_bookmarks = pd.DataFrame(BOOKMARKS)
    st.dataframe(df_bookmarks)
    csv_bookmarks = df_bookmarks.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Bookmarked Data", csv_bookmarks, "bookmarked_opportunities.csv", "text/csv")
