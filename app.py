import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="NSE R5 Scanner", layout="wide")
st.title("🔍 Aumilux Full NSE R5 Scanner")

@st.cache_data
def get_nifty_500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        # Fix for certain symbols that cause errors
        return [s.strip() + ".NS" for s in df['Symbol'].tolist() if s.strip() != "TATAMOTORS"]
    except:
        return ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "INFY.NS", "HDFCBANK.NS"]

def get_r5(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        if data.empty or len(data) < 2: return None
        prev = data.iloc[-2]
        h, l, c = float(prev['High'].iloc[0]), float(prev['Low'].iloc[0]), float(prev['Close'].iloc[0])
        p = (h + l + c) / 3
        r5 = (h + 2 * (p - l)) + (2 * (h - l))
        return round(r5, 2)
    except:
        return None

all_symbols = get_nifty_500()
st.info(f"Scanning {len(all_symbols)} NSE scripts. Opportunities will appear below.")
progress_bar = st.progress(0)
table_placeholder = st.empty()

while True:
    hits = []
    for i, s in enumerate(all_symbols):
        progress_bar.progress((i + 1) / len(all_symbols))
        r5_val = get_r5(s)
        if r5_val is None: continue
        
        try:
            tick = yf.Ticker(s)
            hist = tick.history(period="1d")
            if hist.empty: continue
            ltp = round(float(hist['Close'].iloc[-1]), 2)
            
            if ltp >= (r5_val * 0.95):
                status = "🚨 R5 BREAKOUT" if ltp >= r5_val else "Near R5"
                hits.append({"Stock": s.replace(".NS", ""), "LTP": ltp, "R5": r5_val, "Status": status})
                
                # Update the table immediately when a hit is found
                df_hits = pd.DataFrame(hits)
                with table_placeholder.container():
                    st.table(df_hits.style.map(
                        lambda x: 'background-color: #ff4b4b; color: white' if x == "🚨 R5 BREAKOUT" else 'background-color: #ffa500',
                        subset=['Status']
                    ))
        except:
            continue
    
    time.sleep(60)
    st.rerun()

