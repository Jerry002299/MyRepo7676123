import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from india_corp_actions import IndiaCorpActions

client = IndiaCorpActions()
start_date = datetime.today().strftime('%d-%m-%Y')
end_date = (datetime.today() + timedelta(days=7)).strftime('%d-%m-%Y')

try:
    df = client.get_actions_df(from_date=start_date, to_date=end_date, source="both")
except Exception as e:
    print(f"Error fetching data: {e}")
    df = pd.DataFrame()

if not df.empty:
    df = df[['symbol', 'action_type', 'ex_date', 'details']].drop_duplicates()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(dataframe):
    if dataframe.empty:
        print("No events to send.")
        return
    
    message = "<b>📅 Upcoming Corporate Action Alerts</b>\n\n"
    for _, row in dataframe.head(15).iterrows():
        message += f"• <b>{row['symbol']}</b> | {row['action_type'].upper()}\n"
        message += f"  🗓 Ex-Date: {row['ex_date']}\n"
        message += f"  ℹ️ {str(row['details'])[:100]}...\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Telegram response status: {response.status_code}")

if __name__ == "__main__":
    if not df.empty:
        send_telegram_alert(df)
