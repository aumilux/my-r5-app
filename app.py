import streamlit as st
import pandas as pd
import yfinance as yf
import time

st.set_page_config(page_title="NSE R5 & Narrow CPR Scanner", layout="wide")
st.title("🚀 Aumilux Pro: R5 & Narrow CPR Scanner")

@st.cache_data
def get_nifty_list():
    try:
        url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
        df = pd.read_csv(url)
        return [s.strip() + ".NS" for s in df['Symbol'].tolist() if s.strip() != "TATAMOTORS"]
    except:
        return ["RELIANCE.NS", "TCS.NS", "SBIN.NS", "INFY.NS", "HDFCBANK.NS"]

def get_cpr_details(ticker):
    try:
        # Fetching 2 days of daily data for pivot calculation
        data = yf.download(ticker, period="2d", interval="1d", progress=False)
        if data.empty or len(data) < 2: return None
        prev = data.iloc[-2]
        h, l, c = float(prev['High'].iloc[0]), float(prev['Low'].iloc[0]), float(prev['Close'].iloc[0])
        
        # CPR Calculations
        pivot = (h + l + c) / 3
        bc = (h + l) / 2
        tc = (pivot - bc) + pivot
        width_pct = (abs(tc - bc) / pivot) * 100
        
        # R5 Calculation
        r5 = (h + 2 * (pivot - l)) + (2 * (h - l))
        return {"R5": round(r5, 2), "Width%": round(width_pct, 3)}
    except:
        return None

all_symbols = get_nifty_list()
st.info(f"Scanning {len(all_symbols)} scripts. Matches will appear below instantly.")
progress_bar = st.progress(0)
table_placeholder = st.empty()

while True:
    hits = []
    for i, s in enumerate(all_symbols):
        progress_bar.progress((i + 1) / len(all_symbols))
        details = get_cpr_details(s)
        if not details: continue
        
        try:
            tick = yf.Ticker(s)
            hist = tick.history(period="1d")
            if hist.empty: continue
            ltp = round(float(hist['Close'].iloc[-1]), 2)
            
            # Logic: Narrow CPR (< 0.2%) OR Price near/above R5
            is_narrow = details['Width%'] < 0.2
            is_at_r5 = ltp >= (details['R5'] * 0.995) # Loosened to 0.5% so you see data
            
            if is_narrow or is_at_r5:
                status = "🚨 R5 BREAKOUT" if ltp >= details['R5'] else ("Watching" if is_at_r5 else "Consolidating")
                cpr_type = "🎯 NARROW" if is_narrow else "Normal"
                
                hits.append({
                    "Stock": s.replace(".NS", ""), 
                    "LTP": ltp, "R5": details['R5'], 
                    "CPR Width%": details['Width%'],
                    "CPR Type": cpr_type, "Status": status
                })
                
                # Live table update as stocks are found
                df_hits = pd.DataFrame(hits)
                with table_placeholder.container():
                    st.table(df_hits.style.map(
                        lambda x: 'background-color: #ff4b4b; color: white' if x == "🚨 R5 BREAKOUT" else ('background-color: #00ff00; color: black' if x == "🎯 NARROW" else ''),
                        subset=['Status', 'CPR Type']
                    ))
        except:
            continue
    time.sleep(60)
    st.rerun()
