import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="NSE R5 Market Scanner", layout="wide")
st.title("🔍 Aumilux Full NSE R5 Scanner")

# Fetch Nifty 500 symbols automatically
@st.cache_data
def get_nifty_500():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return [s + ".NS" for s in df['Symbol'].tolist()]
    except:
        return ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "INFY.NS", "HDFCBANK.NS"]

def get_levels(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        if len(data) < 2: return None
        prev = data.iloc[-2]
        h, l, c = float(prev['High']), float(prev['Low']), float(prev['Close'])
        p = (h + l + c) / 3
        r3 = h + 2 * (p - l)
        r4 = r3 + (h - l)
        r5 = r4 + (h - l)
        return round(r5, 2)
    except:
        return None

all_stocks = get_nifty_500()
st.info(f"Scanning {len(all_stocks)} stocks. Only those near R5 will appear below.")
table_placeholder = st.empty()

while True:
    hits = []
    # Scanning top 100 stocks for speed; increase as needed
    for s in all_stocks[:100]: 
        r5_val = get_levels(s)
        if r5_val is None: continue
        
        tick = yf.Ticker(s)
        hist = tick.history(period="1d")
        if hist.empty: continue
        ltp = round(float(hist['Close'].iloc[-1]), 2)
        
        # Filter: Show only if price is within 0.5% of R5 or higher
        if ltp >= (r5_val * 0.995):
            status = "🚨 BREAKOUT" if ltp >= r5_val else "Near R5"
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
                lambda x: 'background-color: #ff4b4b; color: white; font-weight: bold' if x == "🚨 BREAKOUT" else 'background-color: #ffa500; color: black', 
                subset=['Status']
            ))
    else:
        table_placeholder.warning("Scanning... No stocks currently meeting R5 criteria.")
    
    time.sleep(60) # Refresh every minute
    st.rerun()
