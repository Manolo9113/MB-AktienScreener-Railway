import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import requests
import os

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Aktien-Tool Bäumer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== API KEY (FIX) ====================
# 🔥 WICHTIG: Railway nutzt ENV VARS → os.getenv ist korrekt
FMP_API_KEY = os.getenv("FMP_API_KEY")

# Falls du lokal arbeitest UND secrets.toml hast:
if not FMP_API_KEY:
    try:
        FMP_API_KEY = st.secrets["FMP_API_KEY"]
    except Exception:
        FMP_API_KEY = ""

# ==================== CSS ====================
st.markdown(""" 
<style>
    .stApp { background: #080d18; }
</style>
""", unsafe_allow_html=True)

# ==================== CACHE ====================
@st.cache_data(ttl=3600)
def load_yfinance(ticker: str):
    stock = yf.Ticker(ticker)
    info, hist, insider = {}, pd.DataFrame(), pd.DataFrame()

    try:
        info = stock.info
    except:
        pass

    try:
        hist = stock.history(period="5y")
    except:
        pass

    try:
        insider = stock.insider_transactions
    except:
        pass

    return info, hist, insider


@st.cache_data(ttl=86400)
def load_fmp_metrics(ticker: str):
    if not FMP_API_KEY:
        return {}, [], []

    metrics, peers, analyst = {}, [], []

    try:
        r = requests.get(
            f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}",
            timeout=10
        )
        if r.status_code == 200:
            d = r.json()
            metrics = d[0] if isinstance(d, list) and d else {}
    except:
        pass

    return metrics, peers, analyst


# ==================== REST DEINER APP BLEIBT IDENTISCH ====================
# (alles andere bleibt 100% gleich)
