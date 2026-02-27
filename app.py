import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="R5 Live Tracker", layout="wide")
st.title("📈 Aumilux R5 Intraday Monitor")

# List of stocks to track
STOCKS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "SBIN.NS", "INFY.NS", "TATAMOTORS.NS"]

def get_r5_level(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(df) < 2: return None
        prev = df.iloc[-2]
        h, l, c = float(prev['High']), float(prev['Low']), float(prev['Close'])
        p = (h + l + c) / 3
        r3 = h + 2 * (p - l)
        r4 = r3 + (h - l)
        r5 = r4 + (h - l)
        return r5
    except:
        return None

st.info("Refreshing every 30 seconds. Alerts trigger when price touches or stays above R5.")
table_placeholder = st.empty()

while True:
    results = []
    for s in STOCKS:
        r5 = get_r5_level(s)
        if r5 is None: continue
        
        # Fetching the most recent price
        t = yf.Ticker(s)
        hist = t.history(period="1d")
        if hist.empty: continue
        ltp = float(hist['Close'].iloc[-1])
        
        # Check if price is at or staying above R5
        is_alert = ltp >= (r5 * 0.9995) 
        status = "🚨 ALERT: AT R5" if is_alert else "Below R5"
        
        results.append({
            "Stock": s.replace(".NS", ""), 
            "LTP": round(ltp, 2), 
            "R5 Level": round(r5, 2), 
            "Status": status
        })
    
    if results:
        df_display = pd.DataFrame(results)
        with table_placeholder.container():
            # Apply color only to the Status column when an alert is active
            st.table(df_display.style.map(
                lambda x: 'background-color: #ff4b4b; color: white; font-weight: bold' if x == "🚨 ALERT: AT R5" else '', 
                subset=['Status']
            ))
    
    time.sleep(30)
    st.rerun()
