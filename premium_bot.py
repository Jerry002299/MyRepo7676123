import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# GET API KEYS FROM ENVIRONMENT
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ==============================================================================
# EXPANDED WATCHLIST
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

def ask_gemini(prompt):
    """Direct HTTP POST connection to Gemini API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        pass
    return None

def parse_ai_response(text):
    score, intraday, longterm = "6.0", "Monitor key breakout levels.", "Maintain structural portfolio exposure."
    if text:
        for line in text.split('\n'):
            if line.startswith("SCORE:"):
                score = line.replace("SCORE:", "").strip()
            elif line.startswith("INTRADAY:"):
                intraday = line.replace("INTRADAY:", "").strip()
            elif line.startswith("LONGTERM:"):
                longterm = line.replace("LONGTERM:", "").strip()
    return score, intraday, longterm

print(f"Scanning {len(PREMIUM_WATCHLIST)} stocks for corporate events...")

# PHASE 1: SCAN FOR CRITICAL 3-DAY CALENDAR EVENTS
for ticker in PREMIUM_WATCHLIST:
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.get_calendar()
        
        if calendar and isinstance(calendar, dict):
            if "Earnings Date" in calendar:
                earn_data = calendar["Earnings Date"]
                if isinstance(earn_data, list) and len(earn_data) > 0:
                    earn_date = pd.to_datetime(earn_data[0]).date()
                    if today <= earn_date <= three_days_out:
                        prompt = f"Stock {ticker} has Earnings on {earn_date}. Give an aggressive short-term trading momentum plan using percentages. Format strictly as:\nSCORE: [1-10]\nINTRADAY: [Strategy text]\nLONGTERM: [Strategy text]"
                        score, intra, long_strat = parse_ai_response(ask_gemini(prompt))
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action": "🔥 IMMEDIATE EARNINGS BREAKOUT",
                            "date": earn_date.strftime('%d-%m-%Y'),
                            "score": score, "intraday": intra, "longterm": long_strat
                        })
            
            if "Ex-Dividend Date" in calendar:
                div_data = calendar["Ex-Dividend Date"]
                if div_data:
                    div_date = pd.to_datetime(div_data).date()
                    if today <= div_date <= three_days_out:
                        prompt = f"Stock {ticker} goes Ex-Dividend on {div_date}. Give an aggressive dividend arbitrage short-term plan using percentages. Format strictly as:\nSCORE: [1-10]\nINTRADAY: [Strategy text]\nLONGTERM: [Strategy text]"
                        score, intra, long_strat = parse_ai_response(ask_gemini(prompt))
                        events_list.append({
                            "symbol": ticker.replace(".NS", ""),
                            "action": "💰 URGENT DIVIDEND ARBITRAGE",
                            "date": div_date.strftime('%d-%m-%Y'),
                            "score": score, "intraday": intra, "longterm": long_strat
                        })
    except Exception:
        continue

# PHASE 2: FALLBACK ENGINE (If no immediate calendar events exist, find daily chart momentum)
if not events_list:
    print("No immediate corporate events found. Activating Daily Technical Momentum Scanner...")
    momentum_candidates = []
    
    # Check the top stocks on your list for recent aggressive price movement (past 5 sessions)
    for ticker in PREMIUM_WATCHLIST[:25]:  # Scanning a targeted batch to keep execution under runner limits
        try:
            hist = yf.Ticker(ticker).history(period="5d")
            if len(hist) >= 2:
                pct_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                # Target stocks moving over +2.5% in the previous session
                if pct_change >= 2.5:
                    momentum_candidates.append((ticker, pct_change))
        except Exception:
            continue
            
    # Take the top 2 highest momentum stocks to push to members today
    momentum_candidates = sorted(momentum_candidates, key=lambda x: x[1], reverse=True)[:2]
    
    for ticker, change in momentum_candidates:
        prompt = f"Stock {ticker} rallied +{change:.2f}% yesterday showing strong momentum. Give a professional short-term intraday scalp setup and profit booking targets strictly using percentages based on the opening price. Format strictly as:\nSCORE: [1-10]\nINTRADAY: [Strategy text]\nLONGTERM: [Strategy text]"
        score, intra, long_strat = parse_ai_response(ask_gemini(prompt))
        events_list.append({
            "symbol": ticker.replace(".NS", ""),
            "action": "🚀 DAILY PRICE MOMENTUM BREAKOUT",
            "date": datetime.today().strftime('%d-%m-%Y'),
            "score": score, "intraday": intra, "longterm": long_strat
        })

# ==============================================================================
# TELEGRAM TRANSMISSION
# ==============================================================================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_PREMIUM_CHAT_ID = os.getenv("TELEGRAM_PREMIUM_CHAT_ID")

if events_list and TELEGRAM_BOT_TOKEN and TELEGRAM_PREMIUM_CHAT_ID:
    for ev in events_list:
        message = f"<b>👑 PREMIUM INSIDER ALPHA RADAR</b>\n"
        message += f"⚡ <b>{ev['symbol']}</b> | {ev['action']}\n"
        message += f"🗓 <b>Trade Window:</b> {ev['date']}\n"
        message += f"📊 <b>Momentum Score:</b> <code>{ev['score']}/10</code>\n\n"
        message += f"🏹 <b>Intraday Setup & Profit Booking:</b>\n<i>{ev['intraday']}</i>\n\n"
        message += f"💼 <b>Long-Term Scale-Out Strategy:</b>\n<i>{ev['longterm']}</i>\n"
        
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", 
                      json={"chat_id": TELEGRAM_PREMIUM_CHAT_ID, "text": message, "parse_mode": "HTML"})
    print(f"Successfully delivered {len(events_list)} active setups to Premium.")
else:
    print("No actionable setups generated today.")
