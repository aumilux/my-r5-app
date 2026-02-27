import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="NSE R5 Scanner", layout="wide")
st.title("🔍 Aumilux Full NSE R5 Scanner")

# 1. Fetch the official Nifty 500 list from NSE
@st.cache_data
def get_full_market_list():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return [s + ".NS" for s in df['Symbol'].tolist()]
    except:
        return ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "HDFCBANK.NS", "INFY.NS"]

def get_r5_values(ticker):
    try:
        df = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(df) < 2: return None
        prev = df.iloc[-2]
        h, l, c = float(prev['High']), float(prev['Low']), float(prev['Close'])
        p = (h + l + c) / 3
        # Direct R5 Formula
        r5 = (h + 2 * (p - l)) + (2 * (h - l))
        return round(r5, 2)
    except:
        return None

all_symbols = get_full_market_list()
st.info(f"Scanning {len(all_symbols)} NSE scripts. Only stocks near R5 will appear.")
table_placeholder = st.empty()

while True:
    hits = []
    # Scanning in small batches to keep the app live
    for s in all_symbols:
        r5_val = get_r5_values(s)
        if r5_val is None: continue
        
        t = yf.Ticker(s)
        hist = t.history(period="1d")
        if hist.empty: continue
        ltp = round(float(hist['Close'].iloc[-1]), 2)
        
        # Criteria: Only show if price is within 0.3% of R5 or already above it
        if ltp >= (r5_val * 0.997):
            status = "🚨 R5 BREAKOUT" if ltp >= r5_val else "Near R5"
            hits.append({
                "Stock": s.replace(".NS", ""), 
                "LTP": ltp, 
                "R5 Level": r5_val, 
                "Status": status
            })
    
    if hits:
        df_hits = pd.DataFrame(hits)
        with table_placeholder.container():
            st.table(df_hits.style.map(
                lambda x: 'background-color: #ff4b4b; color: white; font-weight: bold' if x == "🚨 R5 BREAKOUT" else 'background-color: #ffa500; color: black', 
                subset=['Status']
            ))
    else:
        table_placeholder.warning("Scanning... No stocks currently meeting R5 criteria.")
    
    time.sleep(60) # Full market scan every 60 seconds
    st.rerun()
