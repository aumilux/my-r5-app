import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="NSE R5 & Narrow CPR Scanner", layout="wide")
st.title("🚀 Aumilux Pro: Market-Wide R5 Scanner")

@st.cache_data
def get_stock_list():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        # Filter for high-volume leaders to keep the app fast
        return [s.strip() + ".NS" for s in df['Symbol'].tolist()[:150]]
    except:
        return ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "INFY.NS", "HDFCBANK.NS"]

def scan_market():
    symbols = get_stock_list()
    # Batch download previous 2 days of daily data for pivot calculations
    data = yf.download(symbols, period="2d", interval="1d", progress=False, group_by='ticker')
    
    hits = []
    for s in symbols:
        try:
            ticker_data = data[s]
            if len(ticker_data) < 2: continue
            
            prev = ticker_data.iloc[-2]
            h, l, c = float(prev['High']), float(prev['Low']), float(prev['Close'])
            ltp = float(ticker_data['Close'].iloc[-1]) # Current Day LTP
            
            # CPR Calculations
            pivot = (h + l + c) / 3
            bc = (h + l) / 2
            tc = (pivot - bc) + pivot
            width_pct = (abs(tc - bc) / pivot) * 100
            
            # R5 Calculation
            r5 = (h + 2 * (pivot - l)) + (2 * (h - l))
            
            # Filter Logic: Show if Narrow OR Near R5
            is_narrow = width_pct < 0.25
            is_near_r5 = ltp >= (r5 * 0.99) # Within 1% of R5 target
            
            if is_narrow or is_near_r5:
                status = "🚨 R5 BREAKOUT" if ltp >= r5 else "Approaching R5"
                cpr_type = "🎯 NARROW" if is_narrow else "Normal"
                
                hits.append({
                    "Stock": s.replace(".NS", ""),
                    "LTP": round(ltp, 2),
                    "R5 Target": round(r5, 2),
                    "CPR Width%": round(width_pct, 3),
                    "CPR Type": cpr_type,
                    "Status": status
                })
        except:
            continue
    return hits

# UI Controls
st.info("Scanning the top 150 NSE stocks for high-probability setups...")
table_placeholder = st.empty()

while True:
    results = scan_market()
    if results:
        df = pd.DataFrame(results)
        with table_placeholder.container():
            st.table(df.style.map(
                lambda x: 'background-color: #ff4b4b; color: white' if x == "🚨 R5 BREAKOUT" else ('background-color: #00ff00; color: black' if x == "🎯 NARROW" else ''),
                subset=['Status', 'CPR Type']
            ))
    else:
        table_placeholder.warning("Scanning... No stocks currently match the R5 or Narrow CPR criteria.")
    
    time.sleep(60)
    st.rerun()
