
# 🏆 Sports & Forex Arbitrage Dashboard

A real-time **Streamlit web app** to detect profitable arbitrage opportunities across **sports odds** and **forex exchange rates** using live APIs.

---

## 🔧 Features

### ✅ Sports Arbitrage
- Real-time odds using The Odds API (or other APIs like Sportmonks)
- Supports 2–4 outcome arbitrage detection
- Displays:
  - Event matchups
  - Stake distribution
  - Arbitrage profit %
  - Bookmakers and bet links
- CSV export and profit distribution chart

### ✅ Forex Arbitrage
- Uses exchangerate.host for live forex rates
- Simulates buy/sell spreads across exchanges
- Detects profitable currency arbitrage opportunities
- Multiselect currencies or global scan mode
- CSV export

---

## 🛠️ Technologies Used

- **Streamlit** – Web app framework
- **Pandas** – Data manipulation
- **Matplotlib** – Charting
- **Requests** – API calls
- **Python Dotenv** – Environment variable management

---

## 📂 Folder Structure

```

.
├── streamlit\_app.py         # Main Streamlit dashboard
├── arb\_bot.py               # Sports arbitrage logic
├── forex\_bot.py             # Forex arbitrage logic
├── requirements.txt         # Dependencies
├── .env                     # API keys (not pushed to GitHub)
└── .streamlit/
└── config.toml          # Theme settings

````

---

## 🚀 How to Run Locally

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/arbitrage-dashboard.git
   cd arbitrage-dashboard
````

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your `.env` file with:

   ```env
   API_KEY=your_sports_api_key_here
   ```

4. Run the app:

   ```bash
   streamlit run streamlit_app.py
   ```

---

## ☁️ Deployment

Deployed using **[Streamlit Cloud](https://streamlit.io/cloud)**. Set `API_KEY` in the **Secrets** section during deployment.

---

## 📜 License

MIT License. Feel free to use and customize.

---

## 🙌 Acknowledgements

* [The Odds API](https://the-odds-api.com/)
* [exchangerate.host](https://exchangerate.host/)
* [Sportmonks](https://www.sportmonks.com/) *(if used)*

```

---


