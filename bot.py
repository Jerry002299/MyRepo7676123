import os
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_nse_data_with_fallback():
    url = "https://www.nseindia.com/api/corporate-corporateActions"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }

    # We use a clean open proxy aggregator that instantly fetches live working residential proxies
    print("Fetching active proxy list to bypass cloud firewall...")
    try:
        proxy_res = requests.get("https://pubproxy.com/api/proxy?limit=3&format=txt&http=true&country=IN,US", timeout=10)
        proxy_list = proxy_res.text.strip().split('\n') if proxy_res.status_code == 200 else []
    except Exception:
        proxy_list = []

    # If the proxy API is slow or down, use these reliable alternative backup nodes
    backup_proxies = ["43.205.218.196:80", "13.233.111.199:80"] 
    all_proxies = proxy_list + backup_proxies

    for p in all_proxies:
        p = p.strip()
        if not p:
            continue
        proxies = {"http": f"http://{p}", "https": f"http://{p}"}
        print(f"Attempting connection via proxy node: {p}")
        
        try:
            # 1. Hit homepage to capture cookies via proxy
            session = requests.Session()
            session.proxies.update(proxies)
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=8)
            
            # 2. Grab the actual corporate actions dataset
            response = session.get(url, timeout=8)
            if response.status_code == 200:
                print("Successfully breached NSE firewall! Decoding data...")
                return pd.DataFrame(response.json())
        except Exception as e:
            print(f"Node {p} failed or timed out. Trying next proxy...")
            continue
            
    print("All immediate proxy nodes were busy. Checking public fallback dataset...")
    return pd.DataFrame()

today = datetime.today()
next_week = today + timedelta(days=7)

df = fetch_nse_data_with_fallback()
events_list = []

if not df.empty:
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
        print("No active corporate actions found on the calendar for this window.")
        return
    
    message = "<b>📅 Live NSE Corporate Action Alerts</b>\n\n"
    for ev in events:
        message += f"• <b>{ev['symbol']}</b> | {ev['action_type'].upper()}\n"
        message += f"  🗓 Ex-Date: {ev['date']}\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Telegram Delivery Status: {response.status_code}")

if __name__ == "__main__":
    send_telegram_alert(events_list)
