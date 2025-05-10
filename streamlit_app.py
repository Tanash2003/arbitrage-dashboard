# streamlit_app.py

import streamlit as st
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from arb_bot import fetch_odds, calculate_arbitrage
from forex_bot import (
    fetch_forex_batch,
    detect_forex_arbitrage,
    get_all_currency_symbols
)

from itertools import permutations

# ---------- CONFIG ----------
SPORTS = ["basketball_nba", "mma_mixed_martial_arts", "soccer_epl", "cricket_ipl", "tennis_atp_italian_open"]

import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from arb_bot import fetch_odds, calculate_arbitrage, inject_fake_events
from forex_bot import fetch_forex_batch, detect_forex_arbitrage, get_all_currency_symbols

from itertools import permutations

# ---------- CONFIG ----------
SPORTS = ["basketball_nba", "mma_mixed_martial_arts", "soccer_epl", "cricket_ipl", "tennis_atp_italian_open"]
REFRESH_INTERVAL = 60

st.set_page_config(page_title="Live Arbitrage Dashboard", layout="wide")

# ---------- TITLE ----------
st.title("🏆 Sports & Forex Arbitrage Finder")
st.markdown("Scan real-time **sports odds** and **currency rates** to detect arbitrage opportunities.")

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Sports Arbitrage Settings")
manual_refresh = st.sidebar.button("🔄 Refresh Now")
auto_refresh = st.sidebar.checkbox("⏱️ Auto-refresh every 60s", value=False)
min_sports_profit = st.sidebar.slider("📈 Min Sports Arbitrage %", 0.0, 5.0, 1.0, 0.1)
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
        return pd.DataFrame()

    data = []
    for opp in opps:
        rows = {
            "Match": " vs ".join(opp["event"]),
            "Profit %": opp["profit"],
            "Stakes": " / ".join(f"{s:.2f}" for s in opp["stakes"]),
            "Outcomes & Odds": " | ".join(
                f"{o} @ {odds:.2f} ({bm})"
                for o, odds, bm in zip(opp["outcomes"], opp["odds"], opp["bookmakers"])
            ),
            "Links": " / ".join(f"[Link]({url})" for url in opp["urls"])
        }
        data.append(rows)

    df = pd.DataFrame(data)
    st.success(f"✅ {len(df)} sports arbitrage opportunities found")
    st.dataframe(df, use_container_width=True)
    return df

def run_analysis():
    all_opps = []
    total_events = 0
    with st.spinner("Fetching sports odds..."):
        for sport in SPORTS:
            if selected_sport != "All" and sport != selected_sport:
                continue
            events = fetch_odds(sport)
            total_events += len(events)
            opps = calculate_arbitrage(events)
            all_opps.extend(opps)

    # Inject fake events for demo purposes
    all_opps.extend(inject_fake_events())

    filtered_opps = [o for o in all_opps if o["profit"] >= min_sports_profit]
    st.caption(f"⏱️ Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Events scanned: {total_events}")
    return filtered_opps

# ---------- REFRESH HANDLING ----------
should_run = manual_refresh or not auto_refresh
if should_run:
    opps = run_analysis()
    df = display_opportunities(opps)
else:
    opps = []
    df = pd.DataFrame()
    countdown_placeholder = st.empty()
    with st.spinner("Waiting for opportunities... refreshing every 60 seconds"):
        for remaining in range(REFRESH_INTERVAL, 0, -1):
            countdown_placeholder.info(f"⏳ Refreshing in **{remaining}** seconds")
            time.sleep(1)
        st.rerun()

# ---------- UI TABS ----------
tab1, tab2, tab3 = st.tabs([
    "💰 Sports Arbitrage",
    "📊 Sports Chart & Download",
    "💱 Forex Arbitrage"
])

with tab1:
    st.header("🎯 Sports Arbitrage Table")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

with tab2:
    if not df.empty:
        st.markdown("### 📈 Arbitrage Profit % Distribution")
        fig, ax = plt.subplots()
        df_sorted = df.sort_values(by="Profit %", ascending=False)
        ax.barh(df_sorted["Match"], df_sorted["Profit %"])
        ax.invert_yaxis()
        ax.set_xlabel("Profit %")
        ax.set_ylabel("Match")
        ax.set_title("Profit by Arbitrage Opportunity")
        st.pyplot(fig)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Sports Arbitrage CSV",
            data=csv,
            file_name=f"sports_arbitrage_{datetime.now().strftime('%H%M%S')}.csv",
            mime='text/csv'
        )

with tab3:
    st.header("💱 Forex Arbitrage Opportunities")
    with st.spinner("Scanning forex rates..."):
        if global_mode:
            currency_pairs = list(permutations(all_currencies, 2))[:max_pairs]
        else:
            currency_pairs = list(permutations(selected_currencies, 2))[:max_pairs]

        fx_data = fetch_forex_batch(currency_pairs, delay=batch_delay)
        fx_opps = detect_forex_arbitrage(fx_data, threshold=min_forex_profit)

    if not fx_opps:
        st.info("No forex arbitrage opportunities found.")
    else:
        fx_df = pd.DataFrame(fx_opps)
        st.success(f"✅ {len(fx_df)} forex arbitrage opportunities found.")
        st.dataframe(fx_df, use_container_width=True)

        csv_fx = fx_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Forex Arbitrage CSV",
            data=csv_fx,
            file_name=f"forex_arbitrage_{datetime.now().strftime('%H%M%S')}.csv",
            mime='text/csv'
        )

