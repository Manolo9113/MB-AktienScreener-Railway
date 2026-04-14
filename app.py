import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import requests
import os

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Aktien Tool PRO",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== API KEY (RAILWAY SAFE) ====================
FMP_API_KEY = os.getenv("FMP_API_KEY", "")

# ==================== SAFE CACHE ====================
@st.cache_data(ttl=3600)
def load_yfinance(ticker: str):
    stock = yf.Ticker(ticker)

    info = {}
    hist = pd.DataFrame()

    try:
        info = stock.get_info() if hasattr(stock, "get_info") else stock.info
    except:
        info = {}

    try:
        hist = stock.history(period="5y", auto_adjust=True)
    except:
        hist = pd.DataFrame()

    return info, hist


@st.cache_data(ttl=86400)
def load_fmp_metrics(ticker: str):
    if not FMP_API_KEY:
        return {}

    try:
        url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return {}

        data = r.json()
        return data[0] if isinstance(data, list) and len(data) > 0 else {}

    except:
        return {}


# ==================== HELPERS ====================
def safe(v, digits=2):
    try:
        return f"{float(v):.{digits}f}"
    except:
        return "N/A"


def fmt(value):
    try:
        value = float(value)
    except:
        return "N/A"

    if value >= 1e12:
        return f"{value/1e12:.2f}T"
    if value >= 1e9:
        return f"{value/1e9:.2f}B"
    if value >= 1e6:
        return f"{value/1e6:.2f}M"
    return str(value)


def safe_pct(a, b):
    try:
        return (a - b) / b * 100
    except:
        return 0


# ==================== UI ====================
st.title("📈 Aktien Tool PRO (Production)")

ticker = st.text_input("Ticker", "AAPL").upper().strip()

if not ticker:
    st.stop()

# ==================== LOAD DATA ====================
with st.spinner("Lade Daten..."):
    info, hist = load_yfinance(ticker)
    fmp = load_fmp_metrics(ticker)

if hist is None or hist.empty:
    st.error("❌ Keine Kursdaten gefunden")
    st.stop()

# ==================== PRICE ====================
price = float(hist["Close"].iloc[-1])
prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price

change = price - prev
change_pct = safe_pct(price, prev)

# ==================== HEADER ====================
st.subheader(f"{info.get('longName', ticker)} ({ticker})")
st.metric("Preis", f"${price:.2f}", f"{change:.2f} ({change_pct:.2f}%)")

# ==================== CHART ====================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist["Close"],
    name="Price",
    line=dict(width=2)
))

fig.update_layout(
    template="plotly_dark",
    height=500,
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ==================== METRICS ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Market Cap", fmt(info.get("marketCap")))

with col2:
    st.metric("P/E", safe(info.get("trailingPE")))

with col3:
    st.metric("Beta", safe(info.get("beta")))

with col4:
    st.metric("Dividend", safe(info.get("dividendYield")))

# ==================== ADVANCED FMP METRICS ====================
st.markdown("### 📊 FMP Metrics")

if not fmp:
    st.info("FMP API nicht aktiv oder kein Key gesetzt")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("ROIC", safe(fmp.get("returnOnInvestedCapitalTTM")))

    with col2:
        st.metric("Gross Profit Margin", safe(fmp.get("grossProfitMarginTTM")))

    with col3:
        st.metric("Revenue Growth", safe(fmp.get("revenueGrowthTTM")))

# ==================== DEBUG ====================
with st.expander("🔍 Debug"):
    st.write("API Key vorhanden:", bool(FMP_API_KEY))
    st.write("Ticker:", ticker)
    st.write("Hist rows:", len(hist))
    st.json(info)
