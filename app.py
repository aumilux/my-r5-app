import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="R5 Live Tracker", layout="wide")
st.title("📈 Aumilux R5 Intraday Monitor")

# Add the stocks you want to track here
STOCKS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "SBIN.NS", "INFY.NS", "TATAMOTORS.NS"]

def get_levels(ticker):
    data = yf.download(ticker, period="2d", interval="1d", progress=False)
    if len(data) < 2: return None
    prev = data.iloc[-2]
    h, l, c = prev['High'], prev['Low'], prev['Close']
    p = (h + l + c) / 3
    r1 = (2 * p) - l
    r2 = p + (h - l)
    r3 = h + 2 * (p - l)
    r4 = r3 + (h - l)
    r5 = r4 + (h - l)
    return r5

st.info("Refreshing every 30 seconds. Stocks highlighted in RED are staying at or above R5.")
table_placeholder = st.empty()

while True:
    results = []
    for s in STOCKS:
        r5_val = get_levels(s)
        tick = yf.Ticker(s)
        ltp = float(tick.fast_info['last_price'])        
        status = "🚨 ALERT: AT R5" if ltp >= (r5_val * 0.999) else "Below R5"
        results.append({"Stock": s, "LTP": round(ltp, 2), "R5 Level": round(r5_val, 2), "Status": status})
    
    df = pd.DataFrame(results)
    with table_placeholder.container():
        st.table(df.style.map(lambda x: 'background-color: #ff4b4b; color: white' if x == "🚨 ALERT: AT R5" else '', subset=['Status']))
    
    time.sleep(30)

    st.rerun()

