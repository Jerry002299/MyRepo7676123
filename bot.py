import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# FREE TIER WATCHLIST (Benchmark Giants + High-Volume Momentum Plays)
# ==============================================================================
WATCHLIST = [
    # --- The High-Volume Retail & Momentum Favorites ---
    "ADANIENT.NS", "HFCL.NS", "HAL.NS", "BEL.NS", 
    "MAZDOCK.NS", "COCHINSHIP.NS", "SUZLON.NS", "IREDA.NS",
    "ZOMATO.NS", "JIOFIN.NS", "TRENT.NS", "KPIGREEN.NS",
    
    # --- Nifty 50 Heavyweights (Guarantees steady event flow) ---
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", 
    "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", 
    "LTIM.NS", "TATAMOTORS.NS", "M&M.NS", "AXISBANK.NS"
]

events_list = []
today = datetime.today().date()
one_week_out = today + timedelta(days=14)

print("Starting Watchlist scan via upgraded Yahoo Finance Engine...")

for ticker in WATCHLIST:
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.get_calendar()
        
        # Check if the dictionary is valid and contains keys
        if calendar and isinstance(calendar, dict):
            # Parse Earnings Announcements
            if "Earnings Date" in calendar:
                earn_data = calendar["Earnings Date"]
                if isinstance(earn_data, list) and len(earn_data) > 0:
                    for raw_date in earn_data:
                        earn_date = pd.to_datetime(raw_date).date()
                        if today <= earn_date <= one_week_out:
                            events_list.append({
                                "symbol": ticker.replace(".NS", ""),
                                "action_type": "Earnings Release",
                                "date": earn_date.strftime('%d-%m-%Y')
                            })
            
            # Parse Ex-Dividend Dates
            if "Ex-Dividend Date" in calendar:
                div_data = calendar["Ex-Dividend Date"]
                if div_data:
                    div_date = pd.to_datetime(div_data).date()
                    if today <= div_date <= one_week_out:
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action_type": "Ex-Dividend Date",
                            "date": div_date.strftime('%d-%m-%Y')
                        })
    except Exception as e:
        print(f"Skipping {ticker}: {e}")
        continue

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(events):
    if not events:
        print("No earnings or dividends listed for the watchlist stocks this week.")
        return
    
    message = "<b>📅 Live Watchlist Corporate Action Alerts</b>\n\n"
    for ev in events:
        message += f"• <b>{ev['symbol']}</b> | {ev['action_type'].upper()}\n"
        message += f"  🗓 Date: {ev['date']}\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Telegram Delivery Status: {response.status_code}")

if __name__ == "__main__":
    send_telegram_alert(events_list)
