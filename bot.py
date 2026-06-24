import os
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_via_free_proxy():
    # Utilizing a free, open-source proxy scraper endpoint to relay our request through a clean IP
    url = "https://api.allorigins.win/get?url=" + requests.utils.quote("https://www.nseindia.com/api/corporate-corporateActions")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    
    try:
        print("Routing NSE request through clean proxy layer...")
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            raw_json = response.json()
            # allorigins returns the actual page contents inside a 'contents' string field
            actual_data = pd.read_json(raw_json['contents'])
            return actual_data
        else:
            print(f"Proxy bridge responded with status: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Proxy routing encountered an issue: {e}")
        return pd.DataFrame()

today = datetime.today()
next_week = today + timedelta(days=7)

df = fetch_via_free_proxy()
events_list = []

if not df.empty:
    print("Data decoded successfully! Filtering actions...")
    if 'exDate' in df.columns and 'symbol' in df.columns:
        df['parsed_date'] = pd.to_datetime(df['exDate'], format='%d-%b-%Y', errors='coerce')
        filtered_df = df[(df['parsed_date'] >= today) & (df['parsed_date'] <= next_week)]
        
        for _, row in filtered_df.drop_duplicates(subset=['symbol', 'purpose']).head(15).iterrows():
            events_list.append({
                "symbol": row['symbol'],
                "action_type": row['purpose'],
                "date": row['exDate']
            })

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(events):
    if not events:
        print("No corporate actions found on the calendar for this week.")
        return
    
    message = "<b>📅 Live NSE Corporate Action Alerts</b>\n\n"
    for ev in events:
        message += f"• <b>{ev['symbol']}</b> | {ev['action_type'].upper()}\n"
        message += f"  🗓 Ex-Date: {ev['date']}\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Telegram alert delivery status: {response.status_code}")

if __name__ == "__main__":
    send_telegram_alert(events_list)
