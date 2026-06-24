import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# High-momentum target list (.NS for NSE listings)
WATCHLIST = [
    "ADANIENT.NS", "HFCL.NS", "HAL.NS", "BEL.NS", 
    "MAZDOCK.NS", "COCHINSHIP.NS", "SUZLON.NS", "IREDA.NS",
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "ZOMATO.NS"
]

events_list = []
today = datetime.today().date()
one_week_out = today + timedelta(days=7)

print("Starting Watchlist scan via Yahoo Finance Engine...")

for ticker in WATCHLIST:
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.get_calendar()
        
        # Check if an upcoming corporate calendar exists
        if calendar and not calendar.empty:
            # Check for Earnings Announcements
            if "Earnings Date" in calendar.index:
                earn_dates = calendar.loc["Earnings Date"].values[0]
                if isinstance(earn_dates, (list, tuple, pd.Series)):
                    earn_date = earn_dates[0].date()
                else:
                    earn_date = pd.to_datetime(earn_dates).date()
                
                if today <= earn_date <= one_week_out:
                    events_list.append({
                        "symbol": ticker.replace(".NS", ""),
                        "action_type": "Earnings Release",
                        "date": earn_date.strftime('%d-%m-%Y')
                    })
                    
            # Check for Ex-Dividend Dates
            if "Ex-Dividend Date" in calendar.index:
                div_val = calendar.loc["Ex-Dividend Date"].values[0]
                div_date = pd.to_datetime(div_val).date()
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
        print("No earnings or dividends scheduled for watchlist stocks this week.")
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
