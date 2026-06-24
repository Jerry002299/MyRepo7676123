import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# EXTENDED PREMIUM WATCHLIST (Midcaps + Nifty 500 Alpha Targets)
PREMIUM_WATCHLIST = [
    "ADANIENT.NS", "HFCL.NS", "HAL.NS", "BEL.NS", 
    "MAZDOCK.NS", "COCHINSHIP.NS", "SUZLON.NS", "IREDA.NS",
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", 
    "SBIN.NS", "TRENT.NS", "KPIGREEN.NS", "NHPC.NS", "SJVN.NS"
]

events_list = []
today = datetime.today().date()
# Premium Tier uses a hyper-focused 3-day radar for high-accuracy entry timing
three_days_out = today + timedelta(days=60)

print("Starting Premium Scan Engine...")

for ticker in PREMIUM_WATCHLIST:
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.get_calendar()
        
        if calendar and isinstance(calendar, dict):
            # 1. Capture Urgent Earnings Release
            if "Earnings Date" in calendar:
                earn_data = calendar["Earnings Date"]
                if isinstance(earn_data, list) and len(earn_data) > 0:
                    earn_date = pd.to_datetime(earn_data[0]).date()
                    if today <= earn_date <= three_days_out:
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action_type": "🔥 PRE-EARNINGS MOMENTUM",
                            "date": earn_date.strftime('%d-%m-%Y'),
                            "note": "Expect high volume entry window over next 48 hours."
                        })
            
            # 2. Capture Imminent Ex-Dividend Adjustments
            if "Ex-Dividend Date" in calendar:
                div_data = calendar["Ex-Dividend Date"]
                if div_data:
                    div_date = pd.to_datetime(div_data).date()
                    if today <= div_date <= three_days_out:
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action_type": "💰 URGENT DIVIDEND CUTOFF",
                            "date": div_date.strftime('%d-%m-%Y'),
                            "note": "Last day to buy for cash payout eligibility. Stock price adjusts next session."
                        })
    except Exception as e:
        continue

# Extracting tokens from Environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Notice it pulls the new premium secret key here
TELEGRAM_PREMIUM_CHAT_ID = os.getenv("TELEGRAM_PREMIUM_CHAT_ID")

def send_premium_alert(events):
    if not events:
        print("No immediate premium trade setups found on the radar today.")
        return
    
    message = "<b>👑 PREMIUM INSIDER DATA RADAR</b>\n"
    message += "<i>Hyper-focused short term market catalysts (3-Day Lookahead)</i>\n\n"
    
    for ev in events:
        message += f"⚡ <b>{ev['symbol']}</b> | {ev['action_type']}\n"
        message += f"  🗓 Target Date: {ev['date']}\n"
        message += f"  💡 <i>Strategy: {ev['note']}</i>\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_PREMIUM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Premium Telegram Delivery Status: {response.status_code}")

if __name__ == "__main__":
    send_premium_alert(events_list)
