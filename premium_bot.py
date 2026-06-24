import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from google import genai

# INITIALIZE GEMINI CLIENT NATIVELY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# PREMIUM HIGH-VOLUME MOMENTUM LIST
PREMIUM_WATCHLIST = [
    "ADANIENT.NS", "HFCL.NS", "HAL.NS", "BEL.NS", 
    "MAZDOCK.NS", "COCHINSHIP.NS", "SUZLON.NS", "IREDA.NS",
    "RELIANCE.NS", "TCS.NS", "INFY.NS"
]

events_list = []
today = datetime.today().date()
three_days_out = today + timedelta(days=3)

def analyze_news_sentiment(ticker, headlines):
    """Feeds news headlines to Gemini to extract intraday trading biases."""
    if not ai_client or not headlines:
        return "N/A", "Neutral news environment. Monitor price action normally."
        
    prompt = f"""
    You are an elite institutional intraday momentum trader in the Indian Stock Market (NSE/BSE).
    Analyze these recent news headlines for the stock {ticker}:
    {headlines}
    
    Provide your output strictly in this exact format:
    SCORE: [Give a numerical rating from 1 to 10 where 1 is hyper-bearish panic and 10 is explosive bullish momentum breakout]
    BIAS: [Provide a sharp, 1-sentence tactical intraday trade execution strategy for market open based on this news context]
    """
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text
        
        # Parse output fields cleanly
        score = "7.0"
        bias = "Watch volume expansion."
        for line in text.split('\n'):
            if line.startswith("SCORE:"):
                score = line.replace("SCORE:", "").strip()
            elif line.startswith("BIAS:"):
                bias = line.replace("BIAS:", "").strip()
        return score, bias
    except Exception:
        return "N/A", "AI engine busy. Trade according to technical chart setup."

print("Starting Premium AI Scan Engine...")

for ticker in PREMIUM_WATCHLIST:
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.get_calendar()
        
        # Pull live raw headlines for news extraction
        news_data = stock.news
        headline_summary = ""
        if news_data:
            headline_summary = "\n".join([f"- {item['title']}" for item in news_data[:3]])
            
        if calendar and isinstance(calendar, dict):
            # 1. AI Analysis on Pre-Earnings Catalysts
            if "Earnings Date" in calendar:
                earn_data = calendar["Earnings Date"]
                if isinstance(earn_data, list) and len(earn_data) > 0:
                    earn_date = pd.to_datetime(earn_data[0]).date()
                    if today <= earn_date <= three_days_out:
                        ai_score, ai_bias = analyze_news_sentiment(ticker, headline_summary)
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action_type": "🔥 PRE-EARNINGS MOMENTUM",
                            "date": earn_date.strftime('%d-%m-%Y'),
                            "score": ai_score,
                            "bias": ai_bias
                        })
            
            # 2. AI Analysis on Dividend Adjustments
            if "Ex-Dividend Date" in calendar:
                div_data = calendar["Ex-Dividend Date"]
                if div_data:
                    div_date = pd.to_datetime(div_data).date()
                    if today <= div_date <= three_days_out:
                        ai_score, ai_bias = analyze_news_sentiment(ticker, headline_summary)
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action_type": "💰 URGENT DIVIDEND CUTOFF",
                            "date": div_date.strftime('%d-%m-%Y'),
                            "score": ai_score,
                            "bias": ai_bias
                        })
    except Exception:
        continue

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_PREMIUM_CHAT_ID = os.getenv("TELEGRAM_PREMIUM_CHAT_ID")

def send_premium_alert(events):
    if not events:
        print("No immediate premium trade setups found on the radar today.")
        return
    
    message = "<b>👑 PREMIUM AI MARKET RADAR</b>\n"
    message += "<i>Automated News Sentiment & Catalyst Strategies</i>\n\n"
    
    for ev in events:
        message += f"⚡ <b>{ev['symbol']}</b> | {ev['action_type']}\n"
        message += f"  🗓 Target Date: {ev['date']}\n"
        message += f"  🤖 AI Sentiment Score: <b>{ev['score']}/10</b>\n"
        message += f"  💡 <i>Tactical Strategy: {ev['bias']}</i>\n\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_PREMIUM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    response = requests.post(url, json=payload)
    print(f"Premium Telegram Delivery Status: {response.status_code}")

if __name__ == "__main__":
    send_premium_alert(events_list)
