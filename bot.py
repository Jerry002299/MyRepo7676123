import os
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_bse_corporate_actions():
    # BSE API endpoint for corporate actions - free and cloud-friendly!
    url = "https://api.bseindia.com/BseIndiaAPI/api/DefaultDataData/w"
    
    # Target parameter for Corporate Actions
    params = {
        "Type": "CorpAction",
        "period": "7D" # Fetches all actions within the next 7 days
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://www.bseindia.com/"
    }
    
    try:
        print("Fetching data directly from BSE Engine...")
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("Successfully retrieved BSE corporate actions dataset!")
            return pd.DataFrame(response.json())
        else:
            print(f"BSE API returned status code: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"BSE Fetch Error: {e}")
        return pd.DataFrame()

df = fetch_bse_corporate_actions()
events_list = []

if not df.empty:
    print("Decoding and filtering datasets...")
    # Map BSE's specific JSON keys safely
    # Standard BSE response fields: 'scrip_cd', 'symbol', 'purpose', 'ex_date'
    for _, row in df.head(15).iterrows():
        symbol = row.get('symbol', row.get('scrip_name', 'UNKNOWN'))
        purpose = row.get('purpose', 'Corporate Action')
        ex_date = row.get('ex_date', 'N/A')
        
        events_list.append({
            "symbol": str(symbol).strip(),
            "action_type": str(purpose).strip(),
            "date": str(ex_date).strip()
        })

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(events):
    if not events:
        print("No active corporate actions listed on the exchange calendar for this week.")
        return
    
    message = "<b>📅 Live Exchange Corporate Action Alerts</b>\n\n"
    for ev in events:
        message += f"• <b>{ev['symbol']}</b> | {ev['action_type'].upper()}\n"
        message += f"  🗓 Ex-Date: {ev['date']}\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Telegram Delivery Status: {response.status_code}")

if __name__ == "__main__":
    send_telegram_alert(events_list)
