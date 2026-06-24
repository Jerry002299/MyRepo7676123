import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# GET API KEYS FROM ENVIRONMENT
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================================
# EXPANDED MAXIMUM LIQUIDITY & MOMENTUM WATCHLIST (70+ Alpha Targets)
# ==============================================================================
PREMIUM_WATCHLIST = [
    # --- Defense, Engineering & Railway Momentum ---
    "HAL.NS", "BEL.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "BEML.NS", "BDL.NS", 
    "IRFC.NS", "RVNL.NS", "IRCON.NS", "TITAGARH.NS", "RAILTEL.NS", "TEXRAIL.NS",

    # --- Green Energy, Power & EV Wave ---
    "IREDA.NS", "SUZLON.NS", "NHPC.NS", "SJVN.NS", "KPIGREEN.NS", "TATAPOWER.NS", 
    "POWERGRID.NS", "NTPC.NS", "RECLTD.NS", "PFC.NS", "GENSOL.NS", "AWL.NS",

    # --- High-Volume Retail & Institutional Favorites ---
    "ADANIENT.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ADANIGREEN.NS", "ATGL.NS", 
    "JIOFIN.NS", "TRENT.NS", "ZOMATO.NS", "HUDCO.NS", "NBCC.NS", "GMRINFRA.NS", 
    "HFCL.NS", "IRB.NS", "RVHL.NS", "PPLPHARMA.NS", "VEDL.NS", "BSE.NS",

    # --- Nifty Index Heavyweights (Steady Event Flows) ---
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", 
    "BHARTIARTL.NS", "ITC.NS", "TATAMOTORS.NS", "AXISBANK.NS", "M&M.NS", "LT.NS", 
    "MARUTI.NS", "SUNPHARMA.NS", "BAJAJFINSV.NS", "KOTAKBANK.NS", "HCLTECH.NS",
    "COFORGE.NS",  # Added

    # --- Midcap Volume Outliers ---
    "CDSL.NS", "ANGELONE.NS", "TATAMTRDV.NS", "IRCTC.NS", "YESBANK.NS", "SAIL.NS", 
    "NMDC.NS", "TATASTEEL.NS", "GATI.NS", "JINDALSTEL.NS", "COHANCE.NS"
]


events_list = []
today = datetime.today().date()
three_days_out = today + timedelta(days=3)

def generate_profit_booking_strategy(ticker, event_type, headlines):
    """Calls Gemini API directly via raw HTTP POST requests to prevent SDK import errors."""
    if not GEMINI_API_KEY:
        return "5/10", "Neutral framework.", "Hold core technical support."
        
    prompt = f"""
    You are an elite, highly aggressive institutional money manager for Indian Equities (NSE/BSE).
    Analyze this corporate event '{event_type}' and recent headlines for {ticker}:
    {headlines if headlines else 'No recent breaking news.'}
    
    Provide target execution entries and exits in this exact format string:
    SCORE: [1-10 momentum rank]
    INTRADAY: [Strict opening action rule, target resistance to book quick profits, and invalidation stop-loss]
    LONGTERM: [Explicit investment allocation rule, and trailing price target or percentage milestone to partially book capital profits]
    """
    
    # Pure HTTP direct call to Gemini 2.5 Flash endpoints
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            text = res_json['candidates'][0]['content']['parts'][0]['text']
            
            score, intraday, longterm = "5.0", "Monitor open.", "Hold structural base."
            for line in text.split('\n'):
                if line.startswith("SCORE:"):
                    score = line.replace("SCORE:", "").strip()
                elif line.startswith("INTRADAY:"):
                    intraday = line.replace("INTRADAY:", "").strip()
                elif line.startswith("LONGTERM:"):
                    longterm = line.replace("LONGTERM:", "").strip()
            return score, intraday, longterm
        else:
            return "N/A", "Scan raw chart pivots.", "Hold according to structural portfolio guidelines."
    except Exception:
        return "N/A", "Scalp near technical pivot lines.", "Book partial gains at standard Fibonacci extensions."

print(f"Starting Alpha AI HTTP Scan across {len(PREMIUM_WATCHLIST)} institutional tickers...")

for ticker in PREMIUM_WATCHLIST:
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.get_calendar()
        
        # Capture raw headline vectors
        news_data = stock.news
        headlines = "\n".join([f"- {item['title']}" for item in news_data[:3]]) if news_data else ""
        
        if calendar and isinstance(calendar, dict):
            # 1. Parse Pre-Earnings Volume Windows
            if "Earnings Date" in calendar:
                earn_data = calendar["Earnings Date"]
                if isinstance(earn_data, list) and len(earn_data) > 0:
                    earn_date = pd.to_datetime(earn_data[0]).date()
                    if today <= earn_date <= three_days_out:
                        score, intra, long_strat = generate_profit_booking_strategy(ticker, "Pre-Earnings Release", headlines)
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action": "🔥 PRE-EARNINGS HIGH VOLATILITY",
                            "date": earn_date.strftime('%d-%m-%Y'),
                            "score": score, "intraday": intra, "longterm": long_strat
                        })
            
            # 2. Parse Imminent Ex-Dividend Deadlines
            if "Ex-Dividend Date" in calendar:
                div_data = calendar["Ex-Dividend Date"]
                if div_data:
                    div_date = pd.to_datetime(div_data).date()
                    if today <= div_date <= three_days_out:
                        score, intra, long_strat = generate_profit_booking_strategy(ticker, "Ex-Dividend Adjustment", headlines)
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action": "💰 DIVIDEND PRICE CUTOFF",
                            "date": div_date.strftime('%d-%m-%Y'),
                            "score": score, "intraday": intra, "longterm": long_strat
                        })
    except Exception:
        continue

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_PREMIUM_CHAT_ID = os.getenv("TELEGRAM_PREMIUM_CHAT_ID")

def send_premium_alert(events):
    if not events:
        print("No high-alpha short term trade configurations matched the radar today.")
        return
    
    for ev in events:
        message = f"<b>👑 PREMIUM INSIDER ALPHA RADAR</b>\n"
        message += f"⚡ <b>{ev['symbol']}</b> | {ev['action']}\n"
        message += f"🗓 <b>Target Date:</b> {ev['date']}\n"
        message += f"📊 <b>Momentum Score:</b> <code>{ev['score']}/10</code>\n\n"
        message += f"🏹 <b>Intraday Setup & Profit Booking:</b>\n<i>{ev['intraday']}</i>\n\n"
        message += f"💼 <b>Long-Term Capital Allocation & Scale-Out:</b>\n<i>{ev['longterm']}</i>\n"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_PREMIUM_CHAT_ID, "text": message, "parse_mode": "HTML"})
        
    print(f"Successfully processed and delivered {len(events)} premium alerts.")

if __name__ == "__main__":
    send_premium_alert(events_list)
