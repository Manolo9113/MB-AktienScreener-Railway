import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import requests
import os
import json
import io
import base64
from datetime import datetime, timedelta
import math
from pathlib import Path

# ==================== CONFIG ====================

st.set_page_config(
page_title=“Equitas – Stock Intelligence”,
page_icon=“⬡”,
layout=“wide”,
initial_sidebar_state=“expanded”,
)

# ==================== CUSTOM CSS ====================

st.markdown(”””

<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg: #0a0d14;
    --surface: #111520;
    --surface2: #161b2e;
    --border: #1e2540;
    --border2: #252d4a;
    --accent: #4f8ef7;
    --accent2: #7c5cfc;
    --green: #22c55e;
    --red: #ef4444;
    --amber: #f59e0b;
    --text: #e8ecf4;
    --muted: #6b7599;
    --muted2: #4a5270;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg) !important;
    color: var(--text) !important;
}

.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1600px; }

/* ---- MOBILE SEARCH BAR ---- */
.mobile-search-hint {
    display: none;
    background: var(--surface);
    border: 1px solid var(--border2);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 1.2rem;
    font-size: 0.82rem;
    color: var(--muted);
}
@media (max-width: 768px) {
    .mobile-search-hint { display: block; }
    .block-container { padding: 1rem 0.8rem 2rem; }
}

/* ---- HEADER ---- */
.eq-header { display: flex; align-items: center; gap: 1.5rem; margin-bottom: 0.25rem; }
.eq-logo-img {
    width: 64px;
    height: 64px;
    border-radius: 14px;
    background: var(--surface);
    border: 1px solid var(--border2);
    object-fit: contain;
    padding: 6px;
    flex-shrink: 0;
}
.eq-logo-placeholder {
    width: 64px;
    height: 64px;
    border-radius: 14px;
    background: linear-gradient(135deg, var(--surface2), var(--border2));
    border: 1px solid var(--border2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--accent);
    flex-shrink: 0;
    letter-spacing: 0.02em;
}

.eq-logo { font-family: 'DM Serif Display', serif; font-size: 1.1rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--accent); }
.eq-company { font-family: 'DM Serif Display', serif; font-size: 2.4rem; line-height: 1.1; color: var(--text); }
.eq-ticker-badge { display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.75rem; background: var(--surface2); border: 1px solid var(--border2); padding: 0.2rem 0.6rem; border-radius: 6px; margin-left: 0.6rem; color: var(--accent); vertical-align: middle; }
.eq-price-block { display: flex; align-items: baseline; gap: 1rem; margin: 0.5rem 0 1.5rem; }
.eq-price { font-family: 'DM Mono', monospace; font-size: 3rem; font-weight: 500; color: var(--text); }
.eq-change-pos { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--green); }
.eq-change-neg { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--red); }
.eq-sector { font-size: 0.85rem; color: var(--muted); }

/* ---- CARDS ---- */
.eq-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.2rem; margin-bottom: 0.8rem; }
.eq-card-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.5rem; }
.eq-card-value { font-family: 'DM Mono', monospace; font-size: 1.6rem; font-weight: 500; color: var(--text); }
.eq-card-sub { font-size: 0.78rem; color: var(--muted); margin-top: 0.35rem; }

/* ---- METRIC ROW ---- */
.eq-metric { display: flex; justify-content: space-between; align-items: center; padding: 0.55rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
.eq-metric:last-child { border-bottom: none; }
.eq-metric-label { color: var(--muted); }
.eq-metric-value { font-family: 'DM Mono', monospace; color: var(--text); font-size: 0.85rem; font-weight: 500; }

/* ---- GAUGE BAR ---- */
.gauge-wrap { margin: 0.3rem 0 0.1rem; }
.gauge-track { height: 4px; background: var(--border2); border-radius: 2px; overflow: hidden; }
.gauge-fill { height: 100%; border-radius: 2px; }

/* ---- SECTION LABELS ---- */
.eq-section { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--text); margin: 1.5rem 0 0.8rem; }

/* ---- NEWS ---- */
.news-item { padding: 0.8rem 0; border-bottom: 1px solid var(--border); }
.news-item:last-child { border-bottom: none; }
.news-headline { font-size: 0.9rem; color: var(--text); line-height: 1.4; margin-bottom: 0.25rem; }
.news-meta { font-size: 0.75rem; color: var(--muted); font-family: 'DM Mono', monospace; }
.news-sentiment-pos { color: var(--green); font-weight: 600; }
.news-sentiment-neg { color: var(--red); font-weight: 600; }
.news-sentiment-neu { color: var(--muted); font-weight: 600; }

/* ---- FAIR VALUE ---- */
.fv-positive { color: var(--green); }
.fv-negative { color: var(--red); }
.fv-label { font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); margin-bottom: 0.3rem; }
.fv-value { font-family: 'DM Mono', monospace; font-size: 2rem; font-weight: 500; }
.fv-range { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: var(--muted); }

/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] { gap: 0; background: var(--surface); border-radius: 10px; padding: 4px; border: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; font-weight: 500; color: var(--muted); padding: 0.5rem 1rem; border-radius: 8px; }
.stTabs [aria-selected="true"] { background: var(--surface2) !important; color: var(--text) !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }

/* ---- INPUTS ---- */
.stTextInput > div > div { background: var(--surface) !important; border: 1px solid var(--border2) !important; border-radius: 8px !important; color: var(--text) !important; }
.stTextInput label { color: var(--muted) !important; font-size: 0.75rem !important; }
.stSelectbox > div > div { background: var(--surface) !important; border: 1px solid var(--border2) !important; border-radius: 8px !important; }

/* ---- SIDEBAR ---- */
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] .block-container { padding: 1rem 1.2rem; }

/* ---- SEARCH RESULTS DROPDOWN ---- */
.search-result-item { padding: 0.5rem 0.8rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; }
.search-result-ticker { font-family: 'DM Mono', monospace; color: var(--accent); font-weight: 500; }
.search-result-name { color: var(--muted); font-size: 0.75rem; margin-top: 0.1rem; }

/* ---- STAR SCORE ---- */
.star-score { font-size: 2rem; line-height: 1; color: var(--amber); letter-spacing: 0.1em; }
.star-empty { color: var(--border2); }
.score-category { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.6rem; }
.score-cat-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }
.score-cat-stars { font-size: 1.1rem; }
.score-bar-track { height: 6px; background: var(--border2); border-radius: 3px; margin-top: 0.4rem; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }

/* ---- DILUTION CARDS ---- */
.dilution-highlight { background: linear-gradient(135deg, rgba(79,142,247,0.1), rgba(124,92,252,0.08)); border: 1px solid var(--border2); border-radius: 12px; padding: 1.2rem; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

.js-plotly-plot .plotly { background: transparent !important; }

/* ---- SIGNAL BADGE ---- */
.signal { display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; padding: 0.3rem 0.8rem; border-radius: 6px; }
.signal-buy { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(34,197,94,0.3); }
.signal-sell { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }
.signal-hold { background: rgba(245,158,11,0.15); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }

/* ---- WATCHLIST ---- */
.wl-item { display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0; border-bottom: 1px solid var(--border); font-size: 0.85rem; }
.wl-ticker { font-family: 'DM Mono', monospace; font-weight: 500; color: var(--accent); }
.wl-change-pos { font-family: 'DM Mono', monospace; color: var(--green); font-size: 0.8rem; }
.wl-change-neg { font-family: 'DM Mono', monospace; color: var(--red); font-size: 0.8rem; }

/* ---- STMETRIC OVERRIDE ---- */
[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; }
[data-testid="stMetricLabel"] p { font-size: 0.7rem !important; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted) !important; }
[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; font-size: 1.5rem !important; }
[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }

/* ---- PEER COMPARISON TABLE ---- */
.peer-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.peer-table th { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); padding: 0.6rem 0.5rem; border-bottom: 1px solid var(--border2); text-align: left; }
.peer-table td { font-family: 'DM Mono', monospace; padding: 0.55rem 0.5rem; border-bottom: 1px solid var(--border); color: var(--text); font-size: 0.8rem; }
.peer-table tr:last-child td { border-bottom: none; }
.peer-table .peer-highlight { background: rgba(79,142,247,0.08); }

/* ---- EXPORT BUTTON ---- */
.export-btn { display: inline-block; background: var(--surface2); border: 1px solid var(--border2); border-radius: 8px; padding: 0.5rem 1rem; color: var(--accent); font-size: 0.78rem; font-family: 'DM Mono', monospace; text-decoration: none; margin-right: 0.5rem; margin-bottom: 0.5rem; }
.export-btn:hover { background: var(--border); color: var(--text); }

/* ---- MOBILE RESPONSIVE ---- */
@media (max-width: 768px) {
    .eq-price { font-size: 2rem; }
    .eq-company { font-size: 1.6rem; }
    .stTabs [data-baseweb="tab"] { padding: 0.4rem 0.6rem; font-size: 0.72rem; }
    .eq-logo-img, .eq-logo-placeholder { width: 48px; height: 48px; }
}
</style>

“””, unsafe_allow_html=True)

# ==================== [6] PERSISTENT WATCHLIST ====================

WATCHLIST_FILE = Path(os.getenv(“WATCHLIST_DIR”, “/tmp”)) / “equitas_watchlists.json”

def load_persistent_watchlist(user_key: str = “default”) -> list:
“”“Lade gespeicherte Watchlist von Disk (Railway-persistent volume oder /tmp).”””
try:
if WATCHLIST_FILE.exists():
data = json.loads(WATCHLIST_FILE.read_text())
return data.get(user_key, [])
except Exception:
pass
return []

def save_persistent_watchlist(watchlist: list, user_key: str = “default”):
“”“Speichere Watchlist persistent auf Disk.”””
try:
data = {}
if WATCHLIST_FILE.exists():
data = json.loads(WATCHLIST_FILE.read_text())
data[user_key] = watchlist
WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
WATCHLIST_FILE.write_text(json.dumps(data))
except Exception:
pass

# ==================== SESSION STATE ====================

if “ticker” not in st.session_state:
st.session_state.ticker = “AAPL”
if “watchlist” not in st.session_state:
saved = load_persistent_watchlist()
st.session_state.watchlist = saved if saved else [“AAPL”, “MSFT”, “NVDA”, “GOOGL”, “AMZN”]
if “search_results” not in st.session_state:
st.session_state.search_results = []

# ==================== API KEYS ====================

FMP_API_KEY = os.getenv(“FMP_API_KEY”, “”)
NEWS_API_KEY = os.getenv(“NEWS_API_KEY”, “”)

# ==================== [1] IMPROVED CACHING — st.cache_resource for Ticker objects ====================

@st.cache_resource(ttl=3600)
def get_ticker_object(ticker: str):
“”“Cache the yfinance Ticker object itself (shared across sessions).”””
return yf.Ticker(ticker)

# ==================== LOGO HELPER ====================

@st.cache_data(ttl=86400)
def get_company_logo_url(ticker: str, domain: str = “”) -> str:
if FMP_API_KEY:
try:
url = f”https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}”
r = requests.get(url, timeout=6)
if r.status_code == 200:
data = r.json()
if data and isinstance(data, list) and data[0].get(“image”):
return data[0][“image”]
except Exception:
pass

```
if domain:
    clearbit_url = f"https://logo.clearbit.com/{domain}"
    try:
        r = requests.head(clearbit_url, timeout=5)
        if r.status_code == 200:
            return clearbit_url
    except Exception:
        pass

TICKER_DOMAIN_MAP = {
    "AAPL": "apple.com", "MSFT": "microsoft.com", "GOOGL": "google.com",
    "GOOG": "google.com", "AMZN": "amazon.com", "NVDA": "nvidia.com",
    "META": "meta.com", "TSLA": "tesla.com", "BRK.B": "berkshirehathaway.com",
    "BRK-B": "berkshirehathaway.com", "JPM": "jpmorganchase.com",
    "V": "visa.com", "MA": "mastercard.com", "UNH": "unitedhealthgroup.com",
    "JNJ": "jnj.com", "WMT": "walmart.com", "XOM": "exxonmobil.com",
    "PG": "pg.com", "ORCL": "oracle.com", "NFLX": "netflix.com",
    "ADBE": "adobe.com", "CRM": "salesforce.com", "AMD": "amd.com",
    "INTC": "intel.com", "QCOM": "qualcomm.com", "IBM": "ibm.com",
    "SAP": "sap.com", "ASML": "asml.com", "TSM": "tsmc.com",
    "BABA": "alibaba.com", "TCEHY": "tencent.com", "SHOP": "shopify.com",
    "SQ": "squareup.com", "PYPL": "paypal.com", "UBER": "uber.com",
    "LYFT": "lyft.com", "ABNB": "airbnb.com", "COIN": "coinbase.com",
    "DIS": "disney.com", "NKE": "nike.com", "MCD": "mcdonalds.com",
    "SBUX": "starbucks.com", "KO": "coca-cola.com", "PEP": "pepsico.com",
    "BAC": "bankofamerica.com", "WFC": "wellsfargo.com", "GS": "goldmansachs.com",
    "MS": "morganstanley.com", "C": "citi.com", "HSBC": "hsbc.com",
    "BA": "boeing.com", "CAT": "caterpillar.com", "GE": "ge.com",
    "MMM": "3m.com", "HON": "honeywell.com", "LMT": "lockheedmartin.com",
    "RTX": "rtx.com", "CVX": "chevron.com", "COP": "conocophillips.com",
    "SPGI": "spglobal.com", "MCO": "moodys.com",
}
fallback_domain = TICKER_DOMAIN_MAP.get(ticker.upper(), "")
if fallback_domain:
    return f"https://logo.clearbit.com/{fallback_domain}"
return ""
```

def logo_html(ticker: str, domain: str = “”, size: int = 64) -> str:
logo_url = get_company_logo_url(ticker, domain)
initials = ticker[:2].upper()
border_radius = “14px”
if logo_url:
return f”””
<img src="{logo_url}" class="eq-logo-img" width="{size}" height="{size}"
onerror="this.style.display='none';document.getElementById('logo-fallback-{ticker}').style.display='flex'"
style="width:{size}px;height:{size}px;border-radius:{border_radius};background:var(--surface);border:1px solid var(--border2);object-fit:contain;padding:6px;flex-shrink:0;"
/>
<div id="logo-fallback-{ticker}"
style="display:none;width:{size}px;height:{size}px;border-radius:{border_radius};background:linear-gradient(135deg,var(--surface2),var(--border2));border:1px solid var(--border2);align-items:center;justify-content:center;font-family:'DM Serif Display',serif;font-size:1.4rem;color:var(--accent);flex-shrink:0;">
{initials}
</div>”””
else:
return f”””
<div style="width:{size}px;height:{size}px;border-radius:{border_radius};background:linear-gradient(135deg,var(--surface2),var(--border2));border:1px solid var(--border2);display:flex;align-items:center;justify-content:center;font-family:'DM Serif Display',serif;font-size:1.4rem;color:var(--accent);flex-shrink:0;">
{initials}
</div>”””

# ==================== TICKER SEARCH ====================

ISIN_WKN_MAP = {}

@st.cache_data(ttl=3600)
def search_ticker(query: str):
results = []
q = query.strip()
if not q or len(q) < 2:
return results

```
if FMP_API_KEY:
    try:
        url = f"https://financialmodelingprep.com/api/v3/search?query={q}&limit=8&apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            for item in r.json():
                results.append({
                    "ticker": item.get("symbol", ""),
                    "name": item.get("name", ""),
                    "exchange": item.get("exchangeShortName", ""),
                    "type": "FMP"
                })
    except Exception:
        pass

if len(q) == 12 and q[:2].isalpha():
    try:
        url2 = f"https://financialmodelingprep.com/api/v3/search?query={q}&limit=5&apikey={FMP_API_KEY}"
        r2 = requests.get(url2, timeout=8)
        if r2.status_code == 200:
            for item in r2.json():
                results.append({
                    "ticker": item.get("symbol", ""),
                    "name": item.get("name", "") + " (ISIN)",
                    "exchange": item.get("exchangeShortName", ""),
                    "type": "ISIN"
                })
    except Exception:
        pass

if not results:
    try:
        test = yf.Ticker(q)
        _info = test.get_info() if hasattr(test, "get_info") else test.info
        if _info and _info.get("longName"):
            results.append({
                "ticker": q.upper(),
                "name": _info.get("longName", q),
                "exchange": _info.get("exchange", ""),
                "type": "Direkt"
            })
    except Exception:
        pass

seen = set()
unique = []
for r in results:
    if r["ticker"] and r["ticker"] not in seen:
        seen.add(r["ticker"])
        unique.append(r)
return unique[:8]
```

# ==================== [1] DATA LOADERS — with cache_resource for Ticker ====================

@st.cache_data(ttl=3600)
def load_yfinance(ticker: str):
stock = get_ticker_object(ticker)
try:
info = stock.get_info() if hasattr(stock, “get_info”) else stock.info
except Exception:
info = {}
try:
hist = stock.history(period=“5y”, auto_adjust=True)
except Exception:
hist = pd.DataFrame()
try:
fins = stock.financials
except Exception:
fins = pd.DataFrame()
try:
balance = stock.balance_sheet
except Exception:
balance = pd.DataFrame()
try:
cashflow = stock.cashflow
except Exception:
cashflow = pd.DataFrame()
try:
dividends = stock.dividends
except Exception:
dividends = pd.Series(dtype=float)
return info, hist, fins, balance, cashflow, dividends

@st.cache_data(ttl=3600)
def load_shares_history(ticker: str):
stock = get_ticker_object(ticker)
shares_data = {}
try:
quarterly_bs = stock.quarterly_balance_sheet
if quarterly_bs is not None and not quarterly_bs.empty:
share_rows = [r for r in quarterly_bs.index if “Share” in str(r) or “Common Stock” in str(r)]
if share_rows:
shares_data[“quarterly”] = quarterly_bs.loc[share_rows[0]].dropna()
except Exception:
pass
try:
annual_bs = stock.balance_sheet
if annual_bs is not None and not annual_bs.empty:
share_rows = [r for r in annual_bs.index if “Share” in str(r) or “Common Stock” in str(r)]
if share_rows:
shares_data[“annual”] = annual_bs.loc[share_rows[0]].dropna()
except Exception:
pass
try:
cf = stock.cashflow
if cf is not None and not cf.empty:
sbc_rows = [r for r in cf.index if “Stock” in str(r) and (“Based” in str(r) or “Comp” in str(r))]
if sbc_rows:
shares_data[“sbc”] = cf.loc[sbc_rows[0]].dropna()
repurchase_rows = [r for r in cf.index if “Repurchase” in str(r) or “Buyback” in str(r)]
if repurchase_rows:
shares_data[“buybacks”] = cf.loc[repurchase_rows[0]].dropna()
except Exception:
pass
return shares_data

# ==================== [2] LOAD FCF HISTORY for enhanced DCF ====================

@st.cache_data(ttl=3600)
def load_fcf_history(ticker: str):
“”“Lade historische Free-Cash-Flow-Daten für erweiterte DCF-Berechnung.”””
stock = get_ticker_object(ticker)
fcf_data = {}
try:
cf = stock.cashflow
if cf is not None and not cf.empty:
# Operativer Cashflow
op_rows = [r for r in cf.index if “Operating” in str(r) and “Cash” in str(r)]
if op_rows:
fcf_data[“operating_cf”] = cf.loc[op_rows[0]].dropna()
# CapEx
capex_rows = [r for r in cf.index if “Capital” in str(r) and “Expend” in str(r)]
if capex_rows:
fcf_data[“capex”] = cf.loc[capex_rows[0]].dropna()
# FCF = OpCF + CapEx (CapEx ist negativ)
if “operating_cf” in fcf_data and “capex” in fcf_data:
common_idx = fcf_data[“operating_cf”].index.intersection(fcf_data[“capex”].index)
if len(common_idx) > 0:
fcf_data[“fcf_history”] = (fcf_data[“operating_cf”][common_idx] + fcf_data[“capex”][common_idx])
except Exception:
pass
return fcf_data

@st.cache_data(ttl=86400)
def load_fmp_metrics(ticker: str):
if not FMP_API_KEY:
return {}, {}, []
try:
url = f”https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}”
r = requests.get(url, timeout=10)
metrics = r.json()[0] if r.status_code == 200 and isinstance(r.json(), list) else {}
except Exception:
metrics = {}
try:
url2 = f”https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={FMP_API_KEY}”
r2 = requests.get(url2, timeout=10)
ratios = r2.json()[0] if r2.status_code == 200 and isinstance(r2.json(), list) else {}
except Exception:
ratios = {}
try:
url3 = f”https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?limit=4&apikey={FMP_API_KEY}”
r3 = requests.get(url3, timeout=10)
estimates = r3.json() if r3.status_code == 200 else []
except Exception:
estimates = []
return metrics, ratios, estimates

@st.cache_data(ttl=3600)
def load_news(ticker: str, company: str):
articles = []
if NEWS_API_KEY:
try:
query = f”{company} stock” if company else ticker
url = f”https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=10&apiKey={NEWS_API_KEY}”
r = requests.get(url, timeout=8)
if r.status_code == 200:
articles = r.json().get(“articles”, [])
except Exception:
pass
if not articles:
try:
stock = get_ticker_object(ticker)
raw = stock.news or []
for n in raw[:8]:
articles.append({
“title”: n.get(“title”, “”),
“url”: n.get(“link”, “#”),
“publishedAt”: datetime.fromtimestamp(n.get(“providerPublishTime”, 0)).isoformat() if n.get(“providerPublishTime”) else “”,
“source”: {“name”: n.get(“publisher”, “”)},
“sentiment”: None
})
except Exception:
pass
return articles

@st.cache_data(ttl=3600)
def load_peer_data(ticker: str, sector: str):
peers = []
if FMP_API_KEY:
try:
url = f”https://financialmodelingprep.com/api/v3/stock_peers?symbol={ticker}&apikey={FMP_API_KEY}”
r = requests.get(url, timeout=8)
if r.status_code == 200:
data = r.json()
if data and isinstance(data, list) and data[0].get(“peersList”):
peer_tickers = data[0][“peersList”][:5]
for pt in peer_tickers:
try:
pinfo = get_ticker_object(pt)
pi = pinfo.get_info() if hasattr(pinfo, “get_info”) else pinfo.info
if pi and pi.get(“longName”):
peers.append(_extract_peer_info(pt, pi))
except Exception:
pass
except Exception:
pass

```
if not peers:
    SECTOR_PEERS = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "CRM", "ADBE", "ORCL"],
        "Financial Services": ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SPGI"],
        "Healthcare": ["UNH", "JNJ", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT"],
        "Consumer Cyclical": ["AMZN", "TSLA", "HD", "NKE", "MCD", "SBUX", "TGT", "LOW"],
        "Communication Services": ["GOOGL", "META", "DIS", "NFLX", "CMCSA", "T", "VZ"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "PXD", "MPC"],
        "Industrials": ["CAT", "HON", "BA", "GE", "RTX", "LMT", "UPS", "DE"],
        "Consumer Defensive": ["PG", "KO", "PEP", "WMT", "COST", "PM", "CL"],
    }
    sector_key = sector if sector in SECTOR_PEERS else None
    if sector_key:
        candidate_tickers = [t for t in SECTOR_PEERS[sector_key] if t != ticker][:4]
        for pt in candidate_tickers:
            try:
                pinfo = get_ticker_object(pt)
                pi = pinfo.get_info() if hasattr(pinfo, "get_info") else pinfo.info
                if pi and pi.get("longName"):
                    peers.append(_extract_peer_info(pt, pi))
            except Exception:
                pass
return peers
```

def _extract_peer_info(pt, pi):
return {
“ticker”: pt,
“name”: pi.get(“shortName”, pi.get(“longName”, pt)),
“marketCap”: pi.get(“marketCap”),
“trailingPE”: pi.get(“trailingPE”),
“forwardPE”: pi.get(“forwardPE”),
“profitMargins”: pi.get(“profitMargins”),
“revenueGrowth”: pi.get(“revenueGrowth”),
“returnOnEquity”: pi.get(“returnOnEquity”),
“debtToEquity”: pi.get(“debtToEquity”),
“dividendYield”: pi.get(“dividendYield”),
“beta”: pi.get(“beta”),
“priceToBook”: pi.get(“priceToBook”),
}

# ==================== HELPERS ====================

def safe(v, digits=2, suffix=””):
try:
return f”{float(v):.{digits}f}{suffix}”
except (TypeError, ValueError):
return “N/A”

def fmt(value):
try:
value = float(value)
except (TypeError, ValueError):
return “N/A”
if abs(value) >= 1e12: return f”{value/1e12:.2f}T”
if abs(value) >= 1e9: return f”{value/1e9:.2f}B”
if abs(value) >= 1e6: return f”{value/1e6:.2f}M”
return f”{value:.2f}”

def safe_pct(a, b):
try:
return (float(a) - float(b)) / abs(float(b)) * 100
except (TypeError, ValueError, ZeroDivisionError):
return 0.0

def color_val(v, good_positive=True):
try:
f = float(v)
if f > 0: return “var(–green)” if good_positive else “var(–red)”
elif f < 0: return “var(–red)” if good_positive else “var(–green)”
else: return “var(–muted)”
except (TypeError, ValueError):
return “var(–muted)”

def metric_row(label, value, color=None):
c = f’color:{color};’ if color else ‘’
st.markdown(f”””
<div class="eq-metric">
<span class="eq-metric-label">{label}</span>
<span class="eq-metric-value" style="{c}">{value}</span>
</div>”””, unsafe_allow_html=True)

def section(title):
st.markdown(f’<div class="eq-section">{title}</div>’, unsafe_allow_html=True)

def card(title, value, sub=””):
st.markdown(f”””
<div class="eq-card">
<div class="eq-card-title">{title}</div>
<div class="eq-card-value">{value}</div>
<div class="eq-card-sub">{sub}</div>
</div>”””, unsafe_allow_html=True)

def stars_html(score_0_to_5):
full = int(round(score_0_to_5))
full = max(0, min(5, full))
stars = “”
for i in range(5):
if i < full: stars += “★”
else: stars += ‘<span class="star-empty">★</span>’
return f’<span class="star-score">{stars}</span>’

def score_bar_html(pct, color):
return f”””<div class="score-bar-track">
<div class="score-bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
</div>”””

# ==================== [3] DILUTION SCORE — integrated into Quality ====================

def compute_dilution_score(shares_history, info):
“”“Berechne Verwässerungs-Score (0–5). Hoher Score = aktionärsfreundlich.”””
dil_pts = 0
dil_count = 0
dil_details = []

```
# 1) Aktienanzahl-Trend (steigend = schlecht, sinkend = gut)
annual = shares_history.get("annual")
if annual is not None and len(annual) >= 2:
    sorted_ann = annual.sort_index()
    oldest = float(sorted_ann.iloc[0])
    newest = float(sorted_ann.iloc[-1])
    if oldest > 0:
        change_pct = (newest - oldest) / oldest * 100
        if change_pct < -5:
            dil_pts += 5  # Starke Reduktion
        elif change_pct < -1:
            dil_pts += 4
        elif change_pct < 1:
            dil_pts += 3  # Stabil
        elif change_pct < 5:
            dil_pts += 2
        else:
            dil_pts += 1  # Starke Verwässerung
        dil_count += 1
        dil_details.append(f"Aktien Δ: {change_pct:+.1f}%")

# 2) SBC vs. Rückkäufe
sbc_data = shares_history.get("sbc")
bb_data = shares_history.get("buybacks")
sbc_last = float(sbc_data.iloc[0]) if sbc_data is not None and len(sbc_data) > 0 else None
bb_last = abs(float(bb_data.iloc[0])) if bb_data is not None and len(bb_data) > 0 else None

if sbc_last is not None and bb_last is not None:
    if bb_last > sbc_last * 2:
        dil_pts += 5  # Rückkäufe dominieren stark
    elif bb_last > sbc_last:
        dil_pts += 4
    elif bb_last > sbc_last * 0.5:
        dil_pts += 3
    elif bb_last > 0:
        dil_pts += 2
    else:
        dil_pts += 1
    dil_count += 1
    dil_details.append(f"SBC: {fmt(sbc_last)} vs. Rückkauf: {fmt(bb_last)}")
elif bb_last is not None and bb_last > 0:
    dil_pts += 4
    dil_count += 1
    dil_details.append(f"Rückkäufe: {fmt(bb_last)} (kein SBC-Daten)")
elif sbc_last is not None and sbc_last > 0:
    # SBC ohne Rückkäufe = Verwässerung
    mcap = info.get("marketCap", 0)
    if mcap and mcap > 0:
        sbc_pct = sbc_last / mcap * 100
        if sbc_pct < 1:
            dil_pts += 3
        elif sbc_pct < 3:
            dil_pts += 2
        else:
            dil_pts += 1
        dil_count += 1
        dil_details.append(f"SBC/MarketCap: {sbc_pct:.1f}%")

if dil_count == 0:
    return 2.5, "Keine Verwässerungsdaten verfügbar"

score = min(5, dil_pts / dil_count)
return score, " · ".join(dil_details)
```

# ==================== COMPANY QUALITY SCORE ====================

def compute_quality_score(info, df_tech, hist, fmp_metrics, shares_history=None):
scores = {}
details = {}

```
# --- BEWERTUNG ---
val_score = 2.5
pe = info.get("trailingPE")
pb = info.get("priceToBook")
peg = info.get("pegRatio")
pts = 0
count = 0
try:
    pe_f = float(pe)
    if 0 < pe_f < 15: pts += 5
    elif 0 < pe_f < 20: pts += 4
    elif 0 < pe_f < 25: pts += 3
    elif 0 < pe_f < 35: pts += 2
    elif pe_f > 0: pts += 1
    count += 1
except (TypeError, ValueError): pass
try:
    pb_f = float(pb)
    if 0 < pb_f < 1.5: pts += 5
    elif 0 < pb_f < 3: pts += 4
    elif 0 < pb_f < 5: pts += 3
    elif 0 < pb_f < 10: pts += 2
    elif pb_f > 0: pts += 1
    count += 1
except (TypeError, ValueError): pass
try:
    peg_f = float(peg)
    if 0 < peg_f < 1: pts += 5
    elif 0 < peg_f < 1.5: pts += 4
    elif 0 < peg_f < 2: pts += 3
    elif 0 < peg_f < 3: pts += 2
    count += 1
except (TypeError, ValueError): pass
if count > 0: val_score = pts / count
scores["Bewertung"] = min(5, val_score)
details["Bewertung"] = f"KGV: {safe(pe)} · KBV: {safe(pb)} · PEG: {safe(peg)}"

# --- PROFITABILITÄT ---
prof_pts = 0
prof_count = 0
margin = info.get("profitMargins")
roe = info.get("returnOnEquity")
roa = info.get("returnOnAssets")
gross = info.get("grossMargins")
for val, thresholds in [(margin, [0.20, 0.10, 0.05, 0]), (roe, [0.25, 0.15, 0.08, 0]),
                         (roa, [0.15, 0.08, 0.03, 0]), (gross, [0.50, 0.30, 0.15, 0])]:
    try:
        v = float(val)
        if v > thresholds[0]: prof_pts += 5
        elif v > thresholds[1]: prof_pts += 4
        elif v > thresholds[2]: prof_pts += 3
        elif v > thresholds[3]: prof_pts += 2
        prof_count += 1
    except (TypeError, ValueError): pass
prof_score = (prof_pts / prof_count) if prof_count > 0 else 2.5
scores["Profitabilität"] = min(5, prof_score)
details["Profitabilität"] = f"Nettomarge: {safe(margin, suffix='%')} · EKR: {safe(roe, suffix='%')} · Brutto: {safe(gross, suffix='%')}"

# --- WACHSTUM ---
grow_pts = 0
grow_count = 0
rev_growth = info.get("revenueGrowth")
earn_growth = info.get("earningsGrowth")
for val in [rev_growth, earn_growth]:
    try:
        g = float(val)
        if g > 0.25: grow_pts += 5
        elif g > 0.15: grow_pts += 4
        elif g > 0.08: grow_pts += 3
        elif g > 0: grow_pts += 2
        else: grow_pts += 1
        grow_count += 1
    except (TypeError, ValueError): pass
grow_score = (grow_pts / grow_count) if grow_count > 0 else 2.5
scores["Wachstum"] = min(5, grow_score)
details["Wachstum"] = f"Umsatz: {safe(rev_growth, suffix='%')} · Gewinn: {safe(earn_growth, suffix='%')}"

# --- BILANZQUALITÄT ---
bal_pts = 0
bal_count = 0
de = info.get("debtToEquity")
cr = info.get("currentRatio")
fcf = info.get("freeCashflow")
try:
    d = float(de)
    if d < 30: bal_pts += 5
    elif d < 60: bal_pts += 4
    elif d < 100: bal_pts += 3
    elif d < 200: bal_pts += 2
    else: bal_pts += 1
    bal_count += 1
except (TypeError, ValueError): pass
try:
    c = float(cr)
    if c > 2.5: bal_pts += 5
    elif c > 1.5: bal_pts += 4
    elif c > 1.0: bal_pts += 3
    elif c > 0.7: bal_pts += 2
    else: bal_pts += 1
    bal_count += 1
except (TypeError, ValueError): pass
try:
    f = float(fcf)
    if f > 0: bal_pts += 4
    else: bal_pts += 1
    bal_count += 1
except (TypeError, ValueError): pass
bal_score = (bal_pts / bal_count) if bal_count > 0 else 2.5
scores["Bilanzqualität"] = min(5, bal_score)
details["Bilanzqualität"] = f"FK/EK: {safe(de)} · Liquidität: {safe(cr)} · FCF: {fmt(fcf)}"

# --- TECHNICALS ---
tech_pts = 0
tech_count = 0
price_now = float(hist["Close"].iloc[-1]) if not hist.empty else None
rsi = df_tech["RSI"].iloc[-1] if not df_tech["RSI"].isna().all() else None
ma50 = df_tech["MA50"].iloc[-1] if not df_tech["MA50"].isna().all() else None
ma200 = df_tech["MA200"].iloc[-1] if not df_tech["MA200"].isna().all() else None
macd = df_tech["MACD"].iloc[-1] if not df_tech["MACD"].isna().all() else None
signal = df_tech["Signal"].iloc[-1] if not df_tech["Signal"].isna().all() else None
try:
    r = float(rsi)
    if 40 <= r <= 60: tech_pts += 5
    elif 30 <= r <= 70: tech_pts += 4
    elif r < 30: tech_pts += 3
    else: tech_pts += 1
    tech_count += 1
except (TypeError, ValueError): pass
try:
    if float(price_now) > float(ma50): tech_pts += 4
    else: tech_pts += 2
    tech_count += 1
except (TypeError, ValueError): pass
try:
    if float(ma50) > float(ma200): tech_pts += 5
    else: tech_pts += 2
    tech_count += 1
except (TypeError, ValueError): pass
try:
    if float(macd) > float(signal): tech_pts += 4
    else: tech_pts += 2
    tech_count += 1
except (TypeError, ValueError): pass
tech_score = (tech_pts / tech_count) if tech_count > 0 else 2.5
scores["Technicals"] = min(5, tech_score)
ma50_above = price_now and ma50 and price_now > ma50
details["Technicals"] = f"RSI: {safe(rsi)} · {'Über MA50 ✓' if ma50_above else 'Unter MA50 ✗'}"

# --- [3] VERWÄSSERUNG (NEU) ---
if shares_history:
    dil_score, dil_detail = compute_dilution_score(shares_history, info)
    scores["Kapitalstruktur"] = dil_score
    details["Kapitalstruktur"] = dil_detail

# --- GESAMTSCORE (gewichtet) ---
if "Kapitalstruktur" in scores:
    weights = {"Bewertung": 0.20, "Profitabilität": 0.22, "Wachstum": 0.18,
               "Bilanzqualität": 0.15, "Technicals": 0.10, "Kapitalstruktur": 0.15}
else:
    weights = {"Bewertung": 0.25, "Profitabilität": 0.25, "Wachstum": 0.20,
               "Bilanzqualität": 0.20, "Technicals": 0.10}
overall = sum(scores.get(k, 2.5) * w for k, w in weights.items())

return overall, scores, details
```

# ==================== [2] ENHANCED DCF / FAIR VALUE ====================

def compute_fair_value(info, hist, fcf_history_data=None):
“”“Erweiterte Fair-Value-Berechnung mit Mehrphasen-DCF.”””
try:
eps = info.get(“trailingEps”) or info.get(“epsTrailingTwelveMonths”)
growth = info.get(“earningsGrowth”) or info.get(“revenueGrowth”) or 0.08
pe = info.get(“trailingPE”) or 20
shares = info.get(“sharesOutstanding”, 1)
bvps = info.get(“bookValue”, 0)

```
    # Graham-Zahl
    graham = None
    if eps and bvps and float(eps) > 0 and float(bvps) > 0:
        graham = (22.5 * float(eps) * float(bvps)) ** 0.5

    # [2] ENHANCED: Mehrphasen-DCF mit historischem FCF-Wachstum
    dcf = None
    fcf = info.get("freeCashflow")
    if fcf and shares:
        fcf_ps = float(fcf) / float(shares)

        # Historische FCF-Wachstumsrate berechnen falls vorhanden
        hist_fcf_growth = None
        if fcf_history_data and "fcf_history" in fcf_history_data:
            fcf_hist = fcf_history_data["fcf_history"].sort_index()
            if len(fcf_hist) >= 2:
                positive_fcf = fcf_hist[fcf_hist > 0]
                if len(positive_fcf) >= 2:
                    cagr = (float(positive_fcf.iloc[-1]) / float(positive_fcf.iloc[0])) ** (1 / max(1, len(positive_fcf) - 1)) - 1
                    hist_fcf_growth = max(-0.05, min(cagr, 0.30))  # Begrenzung auf -5% bis 30%

        # Wachstumsrate: historisch wenn vorhanden, sonst Earnings-Growth
        g_phase1 = hist_fcf_growth if hist_fcf_growth is not None else min(max(float(growth), 0.0), 0.25)
        g_phase2 = g_phase1 * 0.5   # Phase 2: halbes Wachstum (Normalisierung)
        g_terminal = 0.025           # Terminal: 2.5% (BIP-Wachstum)
        discount = 0.10

        pv = 0
        # Phase 1: Jahre 1–5 (hohes Wachstum)
        for yr in range(1, 6):
            pv += fcf_ps * (1 + g_phase1) ** yr / (1 + discount) ** yr
        # Phase 2: Jahre 6–10 (Normalisierung)
        fcf_y5 = fcf_ps * (1 + g_phase1) ** 5
        for yr in range(1, 6):
            pv += fcf_y5 * (1 + g_phase2) ** yr / (1 + discount) ** (yr + 5)
        # Terminal Value (Gordon Growth)
        fcf_y10 = fcf_y5 * (1 + g_phase2) ** 5
        terminal_value = fcf_y10 * (1 + g_terminal) / (discount - g_terminal)
        pv_terminal = terminal_value / (1 + discount) ** 10
        dcf = pv + pv_terminal

    # KGV-basiertes Kursziel
    pe_target = None
    if eps and pe:
        pe_target = float(eps) * min(float(pe) * 1.0, 30)

    values = [v for v in [graham, dcf, pe_target] if v and v > 0]
    if not values:
        return None, None, None, {}

    fair = np.mean(values)
    lo = fair * 0.80
    hi = fair * 1.20

    # Methodendetails für Transparenz
    method_details = {
        "graham": graham,
        "dcf": dcf,
        "pe_target": pe_target,
        "dcf_growth_phase1": g_phase1 if dcf else None,
        "dcf_growth_phase2": g_phase2 if dcf else None,
        "hist_fcf_growth": hist_fcf_growth,
    }

    return fair, lo, hi, method_details

except Exception:
    return None, None, None, {}
```

# ==================== TECHNICALS ====================

def compute_technicals(hist):
df = hist.copy()
df[“MA20”] = df[“Close”].rolling(20).mean()
df[“MA50”] = df[“Close”].rolling(50).mean()
df[“MA200”] = df[“Close”].rolling(200).mean()
delta = df[“Close”].diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = (-delta.clip(upper=0)).rolling(14).mean()
rs = gain / loss.replace(0, np.nan)
df[“RSI”] = 100 - 100 / (1 + rs)
ema12 = df[“Close”].ewm(span=12).mean()
ema26 = df[“Close”].ewm(span=26).mean()
df[“MACD”] = ema12 - ema26
df[“Signal”] = df[“MACD”].ewm(span=9).mean()
df[“Hist”] = df[“MACD”] - df[“Signal”]
df[“BB_mid”] = df[“Close”].rolling(20).mean()
std = df[“Close”].rolling(20).std()
df[“BB_up”] = df[“BB_mid”] + 2 * std
df[“BB_dn”] = df[“BB_mid”] - 2 * std
df[“Vol_MA20”] = df[“Volume”].rolling(20).mean()
return df

# ==================== [4] EXPORT HELPERS ====================

def build_analysis_csv(ticker, info, hist, cat_scores, fair_val, price, currency):
“”“Erstelle CSV-Export der kompletten Analyse.”””
rows = [
[“Equitas Analyse”, ticker, datetime.now().strftime(”%d.%m.%Y %H:%M”)],
[],
[“Kennzahl”, “Wert”],
[“Unternehmen”, info.get(“longName”, ticker)],
[“Sektor”, info.get(“sector”, “”)],
[“Branche”, info.get(“industry”, “”)],
[“Kurs”, f”{currency} {price:.2f}”],
[“Marktkapitalisierung”, fmt(info.get(“marketCap”))],
[“KGV (TTM)”, safe(info.get(“trailingPE”))],
[“KGV (Forward)”, safe(info.get(“forwardPE”))],
[“KBV”, safe(info.get(“priceToBook”))],
[“KUV”, safe(info.get(“priceToSalesTrailing12Months”))],
[“PEG”, safe(info.get(“pegRatio”))],
[“EPS (TTM)”, safe(info.get(“trailingEps”))],
[“Dividendenrendite”, safe(info.get(“dividendYield”), suffix=”%”)],
[“Beta”, safe(info.get(“beta”))],
[“Bruttomarge”, safe(info.get(“grossMargins”), suffix=”%”)],
[“Nettomarge”, safe(info.get(“profitMargins”), suffix=”%”)],
[“Eigenkapitalrendite”, safe(info.get(“returnOnEquity”), suffix=”%”)],
[“Gesamtkapitalrendite”, safe(info.get(“returnOnAssets”), suffix=”%”)],
[“Verschuldungsgrad”, safe(info.get(“debtToEquity”))],
[“Liquiditätsgrad”, safe(info.get(“currentRatio”))],
[“Freier Cashflow”, fmt(info.get(“freeCashflow”))],
[“Fair Value (Schätzung)”, f”{currency} {fair_val:.2f}” if fair_val else “N/A”],
[],
[“Qualitätskategorie”, “Score (0-5)”],
]
for cat, score in cat_scores.items():
rows.append([cat, f”{score:.1f}”])

```
df_export = pd.DataFrame(rows)
return df_export.to_csv(index=False, header=False)
```

def build_watchlist_csv(watchlist):
“”“Erstelle CSV-Export der Watchlist.”””
rows = [[“Ticker”, “Unternehmen”, “Kurs”, “Veränderung %”]]
for wt in watchlist:
try:
_info, *hist, ** = load_yfinance(wt)
if not _hist.empty:
_p = float(_hist[“Close”].iloc[-1])
_pp = float(_hist[“Close”].iloc[-2]) if len(_hist) > 1 else _p
_chg = safe_pct(_p, _pp)
rows.append([wt, _info.get(“longName”, wt), f”{_p:.2f}”, f”{_chg:.2f}%”])
except Exception:
rows.append([wt, “”, “”, “”])
df = pd.DataFrame(rows[1:], columns=rows[0])
return df.to_csv(index=False)

# ==================== PLOTLY THEME ====================

PLOTLY_LAYOUT = dict(
template=“plotly_dark”,
paper_bgcolor=“rgba(0,0,0,0)”,
plot_bgcolor=“rgba(0,0,0,0)”,
font=dict(family=“DM Mono, monospace”, color=”#6b7599”, size=11),
xaxis=dict(gridcolor=”#1e2540”, zeroline=False, showline=False),
yaxis=dict(gridcolor=”#1e2540”, zeroline=False, showline=False),
margin=dict(l=0, r=0, t=30, b=0),
hoverlabel=dict(bgcolor=”#111520”, bordercolor=”#252d4a”, font_family=“DM Mono, monospace”),
legend=dict(bgcolor=“rgba(0,0,0,0)”, bordercolor=“rgba(0,0,0,0)”),
)

# ==================== SIDEBAR ====================

with st.sidebar:
st.markdown(’<div class="eq-logo">⬡ Equitas</div>’, unsafe_allow_html=True)
st.markdown(”—”)

```
st.markdown('<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:0.5rem">Suche</div>', unsafe_allow_html=True)
search_input = st.text_input("Suche", value="", placeholder="z. B. Apple, AAPL, US0378331005…",
                              label_visibility="collapsed", key="search_box")

if search_input and len(search_input) >= 2:
    with st.spinner("Suche…"):
        results = search_ticker(search_input)
    if results:
        for res in results[:5]:
            ticker_sym = res["ticker"]
            name = res["name"][:30] if res["name"] else ticker_sym
            label = f"{ticker_sym} · {name}"
            if st.button(label, key=f"res_{ticker_sym}", use_container_width=True):
                st.session_state.ticker = ticker_sym
                st.rerun()
    else:
        st.markdown('<div style="font-size:0.78rem;color:var(--muted);padding:0.4rem 0">Keine Ergebnisse</div>', unsafe_allow_html=True)
else:
    ticker_input = st.text_input("Oder direkter Ticker", value=st.session_state.ticker,
                                  placeholder="z. B. AAPL", label_visibility="collapsed", key="ticker_direct")
    if ticker_input:
        t = ticker_input.upper().strip()
        if t and t != st.session_state.ticker:
            st.session_state.ticker = t
            st.rerun()

ticker = st.session_state.ticker

period_map = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1J": "1y", "2J": "2y", "5J": "5y"}
period_label = st.radio("Zeitraum", list(period_map.keys()), horizontal=True, index=3)
chart_period = period_map[period_label]

st.markdown("---")
st.markdown('<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:0.5rem">Watchlist</div>', unsafe_allow_html=True)
wl_cols = st.columns([4, 1])
new_wl = wl_cols[0].text_input("Neues Symbol", placeholder="Hinzufügen…",
                                label_visibility="collapsed", key="wl_input")
if wl_cols[1].button("＋", use_container_width=True) and new_wl:
    t = new_wl.upper().strip()
    if t and t not in st.session_state.watchlist:
        st.session_state.watchlist.append(t)
        save_persistent_watchlist(st.session_state.watchlist)  # [6] persist

for wt in st.session_state.watchlist[:]:
    try:
        _info, _hist, *_ = load_yfinance(wt)
        if not _hist.empty:
            _p = float(_hist["Close"].iloc[-1])
            _pp = float(_hist["Close"].iloc[-2]) if len(_hist) > 1 else _p
            _chg = safe_pct(_p, _pp)
            chg_cls = "wl-change-pos" if _chg >= 0 else "wl-change-neg"
            arrow_wl = "▲" if _chg >= 0 else "▼"
            st.markdown(f"""
            <div class="wl-item">
                <span class="wl-ticker">{wt}</span>
                <span class="{chg_cls}">{arrow_wl} {abs(_chg):.2f}%</span>
            </div>""", unsafe_allow_html=True)
    except Exception:
        pass

# [6] Watchlist-Entfernen-Button
if st.session_state.watchlist:
    remove_ticker = st.selectbox("Entfernen", [""] + st.session_state.watchlist,
                                  label_visibility="collapsed", key="wl_remove",
                                  format_func=lambda x: "Ticker entfernen…" if x == "" else f"✕ {x}")
    if remove_ticker:
        st.session_state.watchlist.remove(remove_ticker)
        save_persistent_watchlist(st.session_state.watchlist)
        st.rerun()

st.markdown("---")

# [4] Watchlist-Export
if st.session_state.watchlist:
    wl_csv = build_watchlist_csv(st.session_state.watchlist)
    st.download_button("📥 Watchlist als CSV", wl_csv, file_name="equitas_watchlist.csv",
                       mime="text/csv", use_container_width=True)

st.markdown(
    f'<div style="font-size:0.7rem;color:var(--muted2)">API-Status<br>'
    f'FMP: {"🟢" if FMP_API_KEY else "🔴"} &nbsp; News: {"🟢" if NEWS_API_KEY else "🔴"}'
    f'</div>', unsafe_allow_html=True)
```

# ==================== MOBILE ====================

st.markdown(f”””

<div class="mobile-search-hint">
    Aktuell: <strong style="color:var(--accent)">{ticker}</strong> — Tippe in der Seitenleiste um zu wechseln
</div>
""", unsafe_allow_html=True)

if not ticker:
st.stop()

# ==================== DATEN LADEN ====================

with st.spinner(””):
info, hist, fins, balance, cashflow, dividends = load_yfinance(ticker)
fmp_metrics, fmp_ratios, fmp_estimates = load_fmp_metrics(ticker)
shares_history = load_shares_history(ticker)
fcf_history_data = load_fcf_history(ticker)  # [2] NEU

if hist is None or hist.empty:
st.error(“❌ Keine Kursdaten gefunden. Bitte prüfe den Ticker.”)
st.stop()

# ==================== ABGELEITETE WERTE ====================

price = float(hist[“Close”].iloc[-1])
prev = float(hist[“Close”].iloc[-2]) if len(hist) > 1 else price
change = price - prev
chg_pct = safe_pct(price, prev)
high52 = float(hist[“High”].rolling(252).max().iloc[-1]) if len(hist) > 252 else float(hist[“High”].max())
low52 = float(hist[“Low”].rolling(252).min().iloc[-1]) if len(hist) > 252 else float(hist[“Low”].min())
fair_val, fv_lo, fv_hi, fv_methods = compute_fair_value(info, hist, fcf_history_data)  # [2] enhanced
df_tech = compute_technicals(hist)

company = info.get(“longName”, ticker)
sector = info.get(“sector”, “”)
industry = info.get(“industry”, “”)
currency = info.get(“currency”, “USD”)
website = info.get(“website”, “”)

rsi_now = float(df_tech[“RSI”].iloc[-1]) if not df_tech[“RSI”].isna().all() else None
overall_score, cat_scores, cat_details = compute_quality_score(info, df_tech, hist, fmp_metrics, shares_history)  # [3] mit Verwässerung

company_domain = “”
if website:
try:
from urllib.parse import urlparse
parsed = urlparse(website)
company_domain = parsed.netloc.replace(“www.”, “”)
except Exception:
pass

# ==================== HEADER ====================

arrow = “▲” if change >= 0 else “▼”
chg_color = “var(–green)” if change >= 0 else “var(–red)”
logo_tag = logo_html(ticker, company_domain, size=64)

st.markdown(f”””

<div class="eq-header">
    {logo_tag}
    <div>
        <div style="font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:0.3rem">
            {sector} · {industry}
        </div>
        <div class="eq-company">{company}
            <span class="eq-ticker-badge">{ticker}</span>
        </div>
    </div>
</div>
<div class="eq-price-block">
    <span class="eq-price">{currency} {price:,.2f}</span>
    <span style="color:{chg_color};font-family:'DM Mono',monospace;font-size:1.1rem">
        {arrow} {abs(change):.2f} ({abs(chg_pct):.2f}%)
    </span>
</div>
""", unsafe_allow_html=True)

# ==================== KPI-LEISTE ====================

kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
with kpi1: card(“Marktkapit.”, fmt(info.get(“marketCap”)), “Gesamtbewertung”)
with kpi2: card(“KGV (TTM)”, safe(info.get(“trailingPE”)), “Kurs / Gewinn”)
with kpi3: card(“Gewinn/Aktie”, safe(info.get(“trailingEps”), suffix=” “ + currency), “EPS (TTM)”)
with kpi4: card(“52W Hoch”, f”{currency} {high52:,.2f}”, f”Tief: {currency} {low52:,.2f}”)
with kpi5: card(“Beta”, safe(info.get(“beta”)), “Marktsensitivität”)
with kpi6:
fv_disp = f”{currency} {fair_val:,.2f}” if fair_val else “N/A”
fv_diff = safe_pct(fair_val, price) if fair_val else None
fv_sub = f”{fv_diff:+.1f}% vs. Kurs” if fv_diff is not None else “Keine Schätzung”
card(“Innerer Wert”, fv_disp, fv_sub)

st.markdown(”<br>”, unsafe_allow_html=True)

# [4] Export-Buttons im Header

exp_c1, exp_c2, exp_c3 = st.columns([1, 1, 4])
with exp_c1:
csv_data = build_analysis_csv(ticker, info, hist, cat_scores, fair_val, price, currency)
st.download_button(“📥 Analyse als CSV”, csv_data, file_name=f”equitas_{ticker}*analyse.csv”,
mime=“text/csv”, use_container_width=True)
with exp_c2:
# Kursdaten-Export
hist_csv = hist.tail(252).to_csv()
st.download_button(“📥 Kursdaten (1J)”, hist_csv, file_name=f”equitas*{ticker}_kurse.csv”,
mime=“text/csv”, use_container_width=True)

# ==================== TABS ====================

tabs = st.tabs([“📈 Chart & Technik”, “📊 Fundamentaldaten”, “⚖️ Innerer Wert & DCF”,
“📰 Nachrichten”, “🎯 Analysten”, “🔬 Verwässerung”, “⭐ Qualität”, “🏢 Peer-Vergleich”])

# ================================================================

# TAB 1 — CHART & TECHNICALS

# ================================================================

with tabs[0]:
try:
cutoff = {
“1mo”: hist.index[-1] - timedelta(days=30),
“3mo”: hist.index[-1] - timedelta(days=90),
“6mo”: hist.index[-1] - timedelta(days=180),
“1y”: hist.index[-1] - timedelta(days=365),
“2y”: hist.index[-1] - timedelta(days=730),
“5y”: hist.index[-1] - timedelta(days=1825),
}[chart_period]
df_view = df_tech[df_tech.index >= cutoff]
except Exception:
df_view = df_tech

```
overlay_opts = st.multiselect(
    "Overlays", ["MA20", "MA50", "MA200", "Bollinger Bänder"], default=["MA50", "MA200"],
    label_visibility="collapsed"
)

fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2],
                    vertical_spacing=0.04, subplot_titles=("", "Volumen", "RSI (14)"))

fig.add_trace(go.Candlestick(
    x=df_view.index, open=df_view["Open"], high=df_view["High"],
    low=df_view["Low"], close=df_view["Close"],
    increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
    increasing_fillcolor="#22c55e", decreasing_fillcolor="#ef4444",
    name="OHLC", showlegend=False, line_width=1
), row=1, col=1)

colors = {"MA20": "#f59e0b", "MA50": "#4f8ef7", "MA200": "#7c5cfc"}
for ma in ["MA20", "MA50", "MA200"]:
    if ma in overlay_opts:
        fig.add_trace(go.Scatter(x=df_view.index, y=df_view[ma], name=ma,
            line=dict(color=colors[ma], width=1.2, dash="dot"), opacity=0.85), row=1, col=1)

if "Bollinger Bänder" in overlay_opts:
    fig.add_trace(go.Scatter(x=df_view.index, y=df_view["BB_up"], name="BB Oben",
        line=dict(color="#6b7599", width=1, dash="dash"), showlegend=True), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_view.index, y=df_view["BB_dn"], name="BB Unten",
        line=dict(color="#6b7599", width=1, dash="dash"),
        fill="tonexty", fillcolor="rgba(107,117,153,0.06)", showlegend=False), row=1, col=1)

if fair_val and fv_lo and fv_hi:
    fig.add_hrect(y0=fv_lo, y1=fv_hi, fillcolor="rgba(79,142,247,0.08)",
                  line_width=0, row=1, col=1,
                  annotation_text=f"Innerer Wert ~{currency}{fair_val:,.0f}",
                  annotation_position="top left",
                  annotation_font=dict(color="#4f8ef7", size=10))
    fig.add_hline(y=fair_val, line_color="#4f8ef7", line_dash="dash",
                  line_width=1, opacity=0.6, row=1, col=1)

vol_colors = ["#22c55e" if c >= o else "#ef4444" for c, o in zip(df_view["Close"], df_view["Open"])]
fig.add_trace(go.Bar(x=df_view.index, y=df_view["Volume"],
    marker_color=vol_colors, opacity=0.7, name="Volumen", showlegend=False), row=2, col=1)
fig.add_trace(go.Scatter(x=df_view.index, y=df_view["Vol_MA20"],
    line=dict(color="#f59e0b", width=1), name="Vol MA20", showlegend=False), row=2, col=1)

fig.add_trace(go.Scatter(x=df_view.index, y=df_view["RSI"],
    line=dict(color="#7c5cfc", width=1.5), name="RSI", showlegend=False), row=3, col=1)
fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.08)", line_width=0, row=3, col=1)
fig.add_hrect(y0=0, y1=30, fillcolor="rgba(34,197,94,0.08)", line_width=0, row=3, col=1)
fig.add_hline(y=70, line_color="#ef4444", line_dash="dot", line_width=1, opacity=0.4, row=3, col=1)
fig.add_hline(y=30, line_color="#22c55e", line_dash="dot", line_width=1, opacity=0.4, row=3, col=1)

layout = PLOTLY_LAYOUT.copy()
layout["legend"] = dict(orientation="h", y=1.02, x=0)
fig.update_layout(**layout, height=640, showlegend=True)
fig.update_xaxes(rangeslider_visible=False)
fig.update_yaxes(tickprefix=f"{currency} ", row=1, col=1)
st.plotly_chart(fig, use_container_width=True)

section("Technische Signale")
t1, t2, t3, t4 = st.columns(4)
with t1:
    rsi_color = "var(--red)" if (rsi_now and rsi_now > 70) else "var(--green)" if (rsi_now and rsi_now < 30) else "var(--muted)"
    rsi_label = "Überkauft" if (rsi_now and rsi_now > 70) else "Überverkauft" if (rsi_now and rsi_now < 30) else "Neutral"
    st.markdown(f"""<div class="eq-card">
        <div class="eq-card-title">RSI (14)</div>
        <div class="eq-card-value" style="color:{rsi_color}">{safe(rsi_now)}</div>
        <div class="eq-card-sub">{rsi_label}</div>
    </div>""", unsafe_allow_html=True)
with t2:
    macd_now = df_tech["MACD"].iloc[-1]
    sig_now = df_tech["Signal"].iloc[-1]
    macd_bull = macd_now > sig_now
    st.markdown(f"""<div class="eq-card">
        <div class="eq-card-title">MACD</div>
        <div class="eq-card-value" style="color:{'var(--green)' if macd_bull else 'var(--red)'}">{safe(macd_now)}</div>
        <div class="eq-card-sub">Signal: {safe(sig_now)} — {'Bullisch' if macd_bull else 'Bärisch'}</div>
    </div>""", unsafe_allow_html=True)
with t3:
    ma50_val = df_tech["MA50"].iloc[-1]
    ma200_val = df_tech["MA200"].iloc[-1]
    above = price > ma50_val and price > ma200_val
    golden = ma50_val > ma200_val
    st.markdown(f"""<div class="eq-card">
        <div class="eq-card-title">Trend (GD)</div>
        <div class="eq-card-value" style="color:{'var(--green)' if above else 'var(--red)'}">{'Aufwärts' if above else 'Abwärts'}</div>
        <div class="eq-card-sub">{'Goldenes Kreuz ✓' if golden else 'Todeskreuz ✗'} · GD50: {safe(ma50_val)}</div>
    </div>""", unsafe_allow_html=True)
with t4:
    pos52 = (price - low52) / (high52 - low52) * 100 if (high52 - low52) != 0 else 50
    st.markdown(f"""<div class="eq-card">
        <div class="eq-card-title">52W Position</div>
        <div class="eq-card-value">{pos52:.0f}%</div>
        <div class="eq-card-sub">Tief {currency}{low52:,.2f} · Hoch {currency}{high52:,.2f}</div>
        <div class="gauge-wrap"><div class="gauge-track">
            <div class="gauge-fill" style="width:{pos52:.0f}%;background:{'var(--green)' if pos52 > 50 else 'var(--red)'}"></div>
        </div></div>
    </div>""", unsafe_allow_html=True)

section("Kursperformance")
periods = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1J": 252, "3J": 756, "5J": 1260}
perf_data = {}
for lbl, days in periods.items():
    if len(hist) > days:
        p0 = float(hist["Close"].iloc[-days-1])
        perf_data[lbl] = safe_pct(price, p0)
if perf_data:
    fig_perf = go.Figure(go.Bar(
        x=list(perf_data.keys()), y=list(perf_data.values()),
        marker_color=["#22c55e" if v >= 0 else "#ef4444" for v in perf_data.values()],
        text=[f"{v:+.1f}%" for v in perf_data.values()],
        textposition="outside", textfont=dict(family="DM Mono, monospace", size=11)
    ))
    fig_perf.update_layout(**PLOTLY_LAYOUT, height=280, yaxis_ticksuffix="%", showlegend=False)
    st.plotly_chart(fig_perf, use_container_width=True)
```

# ================================================================

# TAB 2 — FUNDAMENTALDATEN [5] konsequent Deutsch

# ================================================================

with tabs[1]:
col_l, col_r = st.columns([1, 1])
with col_l:
section(“Bewertungskennzahlen”)
metric_row(“KGV (TTM)”, safe(info.get(“trailingPE”)))
metric_row(“KGV (Forward)”, safe(info.get(“forwardPE”)))
metric_row(“KBV”, safe(info.get(“priceToBook”)))
metric_row(“KUV (TTM)”, safe(info.get(“priceToSalesTrailing12Months”)))
metric_row(“EV/EBITDA”, safe(fmp_metrics.get(“enterpriseValueOverEBITDATTM”) or info.get(“enterpriseToEbitda”)))
metric_row(“PEG-Verhältnis”, safe(info.get(“pegRatio”)))

```
    section("Profitabilität")
    metric_row("Bruttomarge", safe(info.get("grossMargins"), suffix="%") if info.get("grossMargins") else "N/A")
    metric_row("EBITDA-Marge", safe(info.get("ebitdaMargins"), suffix="%"))
    metric_row("Nettomarge", safe(info.get("profitMargins"), suffix="%"))
    metric_row("Eigenkapitalrendite", safe(info.get("returnOnEquity"), suffix="%"))
    metric_row("Gesamtkapitalrendite", safe(info.get("returnOnAssets"), suffix="%"))
    metric_row("ROIC (TTM)", safe(fmp_metrics.get("returnOnInvestedCapitalTTM"), suffix="%"))

with col_r:
    section("Wachstum")
    metric_row("Umsatzwachstum (JüJ)", safe(info.get("revenueGrowth"), suffix="%"))
    metric_row("Gewinnwachstum (JüJ)", safe(info.get("earningsGrowth"), suffix="%"))
    metric_row("EPS-Wachstum (Quartal)", safe(info.get("earningsQuarterlyGrowth"), suffix="%"))

    section("Finanzkraft")
    metric_row("Gesamtverschuldung", fmt(info.get("totalDebt")))
    metric_row("Barmittel & Äquivalente", fmt(info.get("totalCash")))
    metric_row("Verschuldungsgrad", safe(info.get("debtToEquity")))
    metric_row("Liquiditätsgrad", safe(info.get("currentRatio")))
    metric_row("Schnelle Liquidität", safe(info.get("quickRatio")))
    metric_row("Freier Cashflow", fmt(info.get("freeCashflow")))

    section("Dividende")
    metric_row("Dividendenrendite", safe(info.get("dividendYield"), suffix="%"))
    metric_row("Dividende (jährlich)", safe(info.get("dividendRate"), suffix=f" {currency}"))
    metric_row("Ausschüttungsquote", safe(info.get("payoutRatio"), suffix="%"))
    metric_row("5J Ø Div.-Rendite", safe(info.get("fiveYearAvgDividendYield"), suffix="%"))

if not fins.empty:
    section("Umsatz- & Gewinnverlauf")
    rev_row = [r for r in fins.index if "Revenue" in str(r) or "Total Revenue" in str(r)]
    net_row = [r for r in fins.index if "Net Income" in str(r)]
    if rev_row or net_row:
        fig_fin = go.Figure()
        if rev_row:
            rev_vals = fins.loc[rev_row[0]].dropna()
            fig_fin.add_trace(go.Bar(x=rev_vals.index.astype(str), y=rev_vals.values,
                name="Umsatz", marker_color="#4f8ef7", opacity=0.7))
        if net_row:
            net_vals = fins.loc[net_row[0]].dropna()
            fig_fin.add_trace(go.Bar(x=net_vals.index.astype(str), y=net_vals.values,
                name="Nettogewinn", marker_color="#22c55e", opacity=0.8))
        fig_fin.update_layout(**PLOTLY_LAYOUT, height=300, barmode="group",
                              yaxis_tickprefix=f"{currency} ")
        st.plotly_chart(fig_fin, use_container_width=True)
```

# ================================================================

# TAB 3 — [2] ENHANCED FAIR VALUE & DCF

# ================================================================

with tabs[2]:
fv_col, dcf_col = st.columns([1, 1])

```
with fv_col:
    section("Innerer Wert – Schätzung")
    if fair_val:
        upside = safe_pct(fair_val, price)
        fv_color = "var(--green)" if upside > 0 else "var(--red)"
        label_fv = "Unterbewertet" if upside > 10 else "Überbewertet" if upside < -10 else "Fair bewertet"
        st.markdown(f"""
        <div class="eq-card">
            <div class="fv-label">Geschätzter innerer Wert</div>
            <div class="fv-value" style="color:{fv_color}">{currency} {fair_val:,.2f}</div>
            <div class="fv-range">Bandbreite: {currency} {fv_lo:,.2f} — {currency} {fv_hi:,.2f}</div>
            <br>
            <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap">
                <div>
                    <div class="fv-label">Aktueller Kurs</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.2rem">{currency} {price:,.2f}</div>
                </div>
                <div>
                    <div class="fv-label">Potenzial</div>
                    <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{fv_color}">{upside:+.1f}%</div>
                </div>
                <div>
                    <div class="fv-label">Einschätzung</div>
                    <div style="font-size:0.85rem;margin-top:0.2rem">
                        <span class="signal {'signal-buy' if upside>10 else 'signal-sell' if upside<-10 else 'signal-hold'}">{label_fv}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # [2] Methodentransparenz
        if fv_methods:
            section("Bewertungsmethoden")
            m1, m2, m3 = st.columns(3)
            with m1:
                g_val = fv_methods.get("graham")
                card("Graham-Zahl", f"{currency} {g_val:,.2f}" if g_val else "N/A", "√(22.5 × EPS × Buchwert)")
            with m2:
                d_val = fv_methods.get("dcf")
                g1 = fv_methods.get("dcf_growth_phase1")
                hfcf = fv_methods.get("hist_fcf_growth")
                dcf_sub = "Mehrphasen-DCF"
                if hfcf is not None:
                    dcf_sub += f" · hist. FCF-CAGR: {hfcf*100:.1f}%"
                elif g1 is not None:
                    dcf_sub += f" · Wachstum P1: {g1*100:.1f}%"
                card("DCF-Modell", f"{currency} {d_val:,.2f}" if d_val else "N/A", dcf_sub)
            with m3:
                p_val = fv_methods.get("pe_target")
                card("KGV-Kursziel", f"{currency} {p_val:,.2f}" if p_val else "N/A", "EPS × Ziel-KGV")

        fig_fv = go.Figure()
        fig_fv.add_trace(go.Indicator(
            mode="gauge+number+delta", value=price,
            delta={"reference": fair_val, "valueformat": ".2f",
                   "increasing": {"color": "#22c55e"}, "decreasing": {"color": "#ef4444"}},
            title={"text": f"Kurs vs. Innerer Wert ({currency})", "font": {"size": 13, "color": "#6b7599"}},
            gauge={
                "axis": {"range": [fv_lo * 0.7, fv_hi * 1.3], "tickcolor": "#6b7599", "tickfont": {"size": 9}},
                "bar": {"color": "#4f8ef7"}, "bgcolor": "#111520", "bordercolor": "#1e2540",
                "steps": [
                    {"range": [fv_lo * 0.7, fv_lo], "color": "rgba(239,68,68,0.2)"},
                    {"range": [fv_lo, fv_hi], "color": "rgba(34,197,94,0.15)"},
                    {"range": [fv_hi, fv_hi * 1.3], "color": "rgba(239,68,68,0.2)"},
                ],
                "threshold": {"line": {"color": "#4f8ef7", "width": 2}, "value": fair_val},
            },
            number={"prefix": f"{currency} ", "font": {"family": "DM Mono", "size": 26}}
        ))
        fig_fv.update_layout(**PLOTLY_LAYOUT, height=280)
        st.plotly_chart(fig_fv, use_container_width=True)
    else:
        st.info("Nicht genug Daten für eine Schätzung des inneren Werts.")

with dcf_col:
    section("DCF-Sensitivitätsanalyse")
    st.markdown('<div style="font-size:0.8rem;color:var(--muted);margin-bottom:1rem">Passe die Parameter an, um verschiedene Szenarien zu simulieren.</div>', unsafe_allow_html=True)

    fcf = info.get("freeCashflow")
    shares_out = info.get("sharesOutstanding")
    if fcf and shares_out:
        g_min = st.slider("Wachstumsrate Min (%)", 0, 20, 5)
        g_max = st.slider("Wachstumsrate Max (%)", 5, 40, 20)
        disc = st.slider("Diskontierungsrate (%)", 6, 15, 10)
        term_pe = st.slider("Terminal-KGV", 10, 30, 15)

        growth_rates = np.linspace(g_min/100, g_max/100, 6)
        dcf_vals = []
        for g in growth_rates:
            fcf_ps = float(fcf) / float(shares_out)
            pv = sum(fcf_ps * (1+g)**yr / (1+disc/100)**yr for yr in range(1, 11))
            terminal = fcf_ps * (1+g)**10 * term_pe / (1+disc/100)**10
            dcf_vals.append(pv + terminal)

        fig_dcf = go.Figure()
        bar_colors = ["#22c55e" if v > price else "#ef4444" for v in dcf_vals]
        fig_dcf.add_trace(go.Bar(
            x=[f"{g*100:.0f}%" for g in growth_rates], y=dcf_vals,
            marker_color=bar_colors, text=[f"{currency} {v:,.0f}" for v in dcf_vals],
            textposition="outside", textfont=dict(family="DM Mono", size=10)
        ))
        fig_dcf.add_hline(y=price, line_color="#4f8ef7", line_dash="dash",
                          annotation_text=f"Kurs: {currency}{price:,.2f}",
                          annotation_position="right", line_width=1.5)
        fig_dcf.update_layout(**PLOTLY_LAYOUT, height=320, xaxis_title="Wachstumsrate",
                              yaxis_tickprefix=f"{currency} ", showlegend=False)
        st.plotly_chart(fig_dcf, use_container_width=True)
    else:
        st.info("Freier Cashflow und Aktienanzahl werden für die DCF-Analyse benötigt.")

    # [2] Historischer FCF-Chart
    if fcf_history_data and "fcf_history" in fcf_history_data:
        section("Historischer Free Cash Flow")
        fcf_hist_sorted = fcf_history_data["fcf_history"].sort_index()
        fig_fcf_hist = go.Figure(go.Bar(
            x=fcf_hist_sorted.index.astype(str),
            y=fcf_hist_sorted.values / 1e9,
            marker_color=["#22c55e" if v > 0 else "#ef4444" for v in fcf_hist_sorted.values],
            text=[f"{v/1e9:.1f}B" for v in fcf_hist_sorted.values],
            textposition="outside", textfont=dict(family="DM Mono", size=10)
        ))
        fig_fcf_hist.update_layout(**PLOTLY_LAYOUT, height=260, yaxis_title=f"Mrd. {currency}",
                                   showlegend=False)
        st.plotly_chart(fig_fcf_hist, use_container_width=True)
```

# ================================================================

# TAB 4 — NACHRICHTEN

# ================================================================

with tabs[3]:
news = load_news(ticker, company)
section(“Aktuelle Nachrichten”)
if news:
for art in news:
title = art.get(“title”, “”)
url = art.get(“url”, “#”)
src = art.get(“source”, {}).get(“name”, “”) if isinstance(art.get(“source”), dict) else “”
pub = art.get(“publishedAt”, “”)[:10] if art.get(“publishedAt”) else “”
title_l = title.lower()
neg_words = [“fall”, “drop”, “crash”, “loss”, “decline”, “down”, “cut”, “miss”, “warn”, “fear”, “risk”, “sell”, “bear”, “layoff”, “lawsuit”]
pos_words = [“rise”, “gain”, “beat”, “growth”, “profit”, “surge”, “record”, “buy”, “bull”, “upgrade”, “breakout”, “strong”, “outperform”]
if any(w in title_l for w in pos_words):
sent_label, sent_cls = “Positiv”, “news-sentiment-pos”
elif any(w in title_l for w in neg_words):
sent_label, sent_cls = “Negativ”, “news-sentiment-neg”
else:
sent_label, sent_cls = “Neutral”, “news-sentiment-neu”
st.markdown(f”””
<div class="news-item">
<div class="news-headline"><a href="{url}" target="_blank" style="color:var(--text);text-decoration:none">{title}</a></div>
<div class="news-meta">{src}  ·  {pub}  ·  <span class="{sent_cls}">{sent_label}</span></div>
</div>”””, unsafe_allow_html=True)
else:
st.info(“Keine Nachrichten gefunden.”)

# ================================================================

# TAB 5 — ANALYSTEN

# ================================================================

with tabs[4]:
section(“Analysten-Konsens & Schätzungen”)
est_col1, est_col2, est_col3 = st.columns(3)
target = info.get(“targetMeanPrice”)
target_lo = info.get(“targetLowPrice”)
target_hi = info.get(“targetHighPrice”)
rec = info.get(“recommendationKey”, “”).upper().replace(”_”, “ “)
num_analysts = info.get(“numberOfAnalystOpinions”, “N/A”)

```
# [5] Deutsche Empfehlungsbegriffe
REC_DE = {"BUY": "KAUFEN", "STRONG BUY": "STARKER KAUF", "OVERWEIGHT": "ÜBERGEWICHTEN",
          "HOLD": "HALTEN", "NEUTRAL": "NEUTRAL", "UNDERWEIGHT": "UNTERGEWICHTEN",
          "SELL": "VERKAUFEN", "STRONG SELL": "STARK VERKAUFEN"}
rec_de = REC_DE.get(rec, rec)

with est_col1:
    t_upside = safe_pct(target, price) if target else None
    card("Analysten-Kursziel", f"{currency} {target:,.2f}" if target else "N/A",
         f"Potenzial: {t_upside:+.1f}%" if t_upside else "")
with est_col2:
    sig_cls = "signal-buy" if "BUY" in rec or "OVERWEIGHT" in rec else "signal-sell" if "SELL" in rec or "UNDERWEIGHT" in rec else "signal-hold"
    st.markdown(f"""<div class="eq-card">
        <div class="eq-card-title">Empfehlung</div>
        <div style="margin-top:0.4rem"><span class="signal {sig_cls}" style="font-size:0.9rem">{rec_de if rec_de else 'N/A'}</span></div>
        <div class="eq-card-sub">{num_analysts} Analysten</div>
    </div>""", unsafe_allow_html=True)
with est_col3:
    card("Kursziel-Bandbreite",
         f"{currency} {target_lo:,.0f} – {currency} {target_hi:,.0f}" if target_lo and target_hi else "N/A",
         "Niedrig – Hoch")

if target and target_lo and target_hi:
    fig_est = go.Figure()
    fig_est.add_trace(go.Scatter(
        x=[target_lo, target, target_hi], y=["Kursziel", "Kursziel", "Kursziel"],
        mode="markers+lines", marker=dict(size=[10, 16, 10], color=["#6b7599", "#4f8ef7", "#6b7599"]),
        line=dict(color="#252d4a", width=2), name="Analysten-Bandbreite"
    ))
    fig_est.add_vline(x=price, line_color="#22c55e", line_dash="dash",
                      annotation_text=f"Kurs {currency}{price:,.2f}", annotation_position="top right")
    fig_est.update_layout(**PLOTLY_LAYOUT, height=150, showlegend=False,
                          xaxis_tickprefix=f"{currency} ", yaxis_visible=False)
    st.plotly_chart(fig_est, use_container_width=True)

if fmp_estimates:
    section("Umsatz- & EPS-Prognosen")
    est_rows = []
    for e in fmp_estimates:
        est_rows.append({
            "Jahr": str(e.get("date", ""))[:4],
            "Umsatz (Schätzung)": fmt(e.get("estimatedRevenueAvg")),
            "EPS (Schätzung)": safe(e.get("estimatedEpsAvg")),
            "EPS Hoch": safe(e.get("estimatedEpsHigh")),
            "EPS Tief": safe(e.get("estimatedEpsLow")),
        })
    if est_rows:
        st.dataframe(pd.DataFrame(est_rows), use_container_width=True, hide_index=True)

section("Weitere Signale")
s1, s2, s3 = st.columns(3)
with s1: card("Leerverkaufsquote", safe(info.get("shortPercentOfFloat"), suffix="%"), "Short Float")
with s2: card("Insideranteil", safe(info.get("heldPercentInsiders"), suffix="%"), "Aktien im Besitz des Managements")
with s3: card("Institutioneller Anteil", safe(info.get("heldPercentInstitutions"), suffix="%"), "Aktien bei Großinvestoren")
```

# ================================================================

# TAB 6 — VERWÄSSERUNG

# ================================================================

with tabs[5]:
section(“Aktienanzahl & Verwässerungsanalyse”)
shares_now = info.get(“sharesOutstanding”)
float_shares = info.get(“floatShares”)

```
d1, d2, d3, d4 = st.columns(4)
with d1: card("Ausstehende Aktien", fmt(shares_now), "Aktuell")
with d2: card("Streubesitz", fmt(float_shares), "Frei handelbar")
with d3:
    sbc = None
    if "sbc" in shares_history and len(shares_history["sbc"]) > 0:
        sbc = float(shares_history["sbc"].iloc[0])
    card("Aktienvergütung (SBC)", fmt(sbc) if sbc else "N/A", "Letztes Geschäftsjahr")
with d4:
    bb = None
    if "buybacks" in shares_history and len(shares_history["buybacks"]) > 0:
        bb = abs(float(shares_history["buybacks"].iloc[0]))
    card("Aktienrückkäufe", fmt(bb) if bb else "N/A", "Letztes Geschäftsjahr")

st.markdown("<br>", unsafe_allow_html=True)

annual_shares = shares_history.get("annual")
quarterly_shares = shares_history.get("quarterly")
has_share_data = (annual_shares is not None and len(annual_shares) > 1) or \
                 (quarterly_shares is not None and len(quarterly_shares) > 1)

if has_share_data:
    fig_shares = go.Figure()
    if annual_shares is not None and len(annual_shares) > 1:
        sorted_ann = annual_shares.sort_index()
        fig_shares.add_trace(go.Bar(x=sorted_ann.index.astype(str), y=sorted_ann.values / 1e9,
            name="Aktien ausst. (Mrd.)", marker_color="#4f8ef7", opacity=0.75))
    if quarterly_shares is not None and len(quarterly_shares) > 1:
        sorted_q = quarterly_shares.sort_index()
        fig_shares.add_trace(go.Scatter(x=sorted_q.index.astype(str), y=sorted_q.values / 1e9,
            name="Quartal", line=dict(color="#7c5cfc", width=2), mode="lines+markers", marker=dict(size=5)))
    fig_shares.update_layout(**PLOTLY_LAYOUT, height=300, yaxis_title="Mrd. Aktien",
                             title_text="Historische Aktienanzahl")
    st.plotly_chart(fig_shares, use_container_width=True)
else:
    st.info("Historische Aktienzahlen nicht verfügbar.")

sbc_data = shares_history.get("sbc")
bb_data = shares_history.get("buybacks")
if (sbc_data is not None and len(sbc_data) > 0) or (bb_data is not None and len(bb_data) > 0):
    section("Aktienvergütung vs. Rückkäufe")
    fig_sbc = go.Figure()
    if sbc_data is not None and len(sbc_data) > 0:
        sorted_sbc = sbc_data.sort_index()
        fig_sbc.add_trace(go.Bar(x=sorted_sbc.index.astype(str), y=sorted_sbc.values / 1e9,
            name="SBC (Vergütung)", marker_color="#ef4444", opacity=0.8))
    if bb_data is not None and len(bb_data) > 0:
        sorted_bb = bb_data.sort_index()
        fig_sbc.add_trace(go.Bar(x=sorted_bb.index.astype(str), y=[-abs(v) / 1e9 for v in sorted_bb.values],
            name="Rückkäufe", marker_color="#22c55e", opacity=0.8))
    fig_sbc.add_hline(y=0, line_color="#6b7599", line_width=1)
    fig_sbc.update_layout(**PLOTLY_LAYOUT, height=300, barmode="overlay", yaxis_title=f"Mrd. {currency}",
                          title_text="SBC (rot) vs. Rückkäufe (grün, negativ = Kapitalrückführung)")
    st.plotly_chart(fig_sbc, use_container_width=True)

section("Verwässerungskontext")
dil_l, dil_r = st.columns(2)
with dil_l:
    st.markdown("""
    <div class="dilution-highlight">
        <div class="eq-card-title">Was bedeutet Verwässerung?</div>
        <div style="font-size:0.85rem;color:var(--muted);line-height:1.7">
            Wenn ein Unternehmen neue Aktien ausgibt – z. B. durch aktienbasierte Vergütung (SBC) oder
            Kapitalerhöhungen – sinkt der Anteil bestehender Aktionäre am Gewinn.<br>
            <span style="color:var(--green)">✓ Rückkäufe &gt; SBC → Netto-Reduktion (aktionärsfreundlich)</span><br>
            <span style="color:var(--red)">✗ SBC &gt; Rückkäufe → Netto-Verwässerung (negativ)</span>
        </div>
    </div>""", unsafe_allow_html=True)

with dil_r:
    sbc_last = float(sbc_data.iloc[0]) if sbc_data is not None and len(sbc_data) > 0 else None
    bb_last = abs(float(bb_data.iloc[0])) if bb_data is not None and len(bb_data) > 0 else None
    if sbc_last is not None and bb_last is not None:
        net_effect = bb_last - sbc_last
        net_color = "var(--green)" if net_effect > 0 else "var(--red)"
        net_label = "Netto-Rückführung ✓" if net_effect > 0 else "Netto-Verwässerung ✗"
        st.markdown(f"""
        <div class="eq-card">
            <div class="eq-card-title">Netto-Kapitaleffekt (letztes Jahr)</div>
            <div class="eq-card-value" style="color:{net_color}">{fmt(net_effect)}</div>
            <div class="eq-card-sub">{net_label}</div>
            <br>
            <div class="eq-metric">
                <span class="eq-metric-label">Aktienvergütung (SBC)</span>
                <span class="eq-metric-value" style="color:var(--red)">{fmt(sbc_last)}</span>
            </div>
            <div class="eq-metric">
                <span class="eq-metric-label">Aktienrückkäufe</span>
                <span class="eq-metric-value" style="color:var(--green)">{fmt(bb_last)}</span>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Nicht genug Daten für die Netto-Effekt-Berechnung.")
```

# ================================================================

# TAB 7 — QUALITÄTS-SCORE [3] mit Verwässerungs-Kategorie

# ================================================================

with tabs[6]:
section(“Unternehmensqualität”)
score_l, score_r = st.columns([1, 2])

```
with score_l:
    score_rounded = round(overall_score * 2) / 2
    score_stars = stars_html(score_rounded)
    score_pct = (overall_score / 5) * 100
    if overall_score >= 4.0:
        score_verdict, score_color = "Ausgezeichnet", "var(--green)"
        score_desc = "Starkes Unternehmen mit solider Qualität in den meisten Kategorien."
    elif overall_score >= 3.0:
        score_verdict, score_color = "Gut", "#4f8ef7"
        score_desc = "Solides Unternehmen mit einigen Stärken und moderaten Schwächen."
    elif overall_score >= 2.0:
        score_verdict, score_color = "Durchschnittlich", "var(--amber)"
        score_desc = "Gemischtes Bild – einzelne starke Kategorien, aber auch Schwachstellen."
    else:
        score_verdict, score_color = "Schwach", "var(--red)"
        score_desc = "Erhebliche Schwächen in mehreren Kategorien."

    st.markdown(f"""
    <div class="eq-card" style="text-align:center;padding:2rem 1.4rem">
        <div class="eq-card-title" style="text-align:center">Gesamtqualität</div>
        <div style="font-family:'DM Serif Display',serif;font-size:4.5rem;line-height:1;color:{score_color};margin:0.5rem 0 0.3rem">{overall_score:.1f}</div>
        <div style="font-size:0.7rem;color:var(--muted);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem">von 5.0</div>
        <div style="font-size:1.8rem;letter-spacing:0.08em;margin-bottom:0.6rem">{score_stars}</div>
        <div style="font-size:1rem;font-weight:600;color:{score_color};margin-bottom:0.5rem">{score_verdict}</div>
        <div style="font-size:0.78rem;color:var(--muted);line-height:1.5">{score_desc}</div>
        <div class="gauge-wrap" style="margin-top:1rem"><div class="gauge-track" style="height:6px">
            <div class="gauge-fill" style="width:{score_pct:.0f}%;background:{score_color}"></div>
        </div></div>
    </div>""", unsafe_allow_html=True)

with score_r:
    section("Kategorie-Breakdown")
    cat_colors = {
        "Bewertung": "#f59e0b", "Profitabilität": "#22c55e", "Wachstum": "#4f8ef7",
        "Bilanzqualität": "#7c5cfc", "Technicals": "#ef4444", "Kapitalstruktur": "#4f8ef7"
    }
    # [3] Gewichtungen dynamisch
    if "Kapitalstruktur" in cat_scores:
        cat_weights = {"Bewertung": "20%", "Profitabilität": "22%", "Wachstum": "18%",
                       "Bilanzqualität": "15%", "Technicals": "10%", "Kapitalstruktur": "15%"}
    else:
        cat_weights = {"Bewertung": "25%", "Profitabilität": "25%", "Wachstum": "20%",
                       "Bilanzqualität": "20%", "Technicals": "10%"}

    for cat, score in cat_scores.items():
        cat_pct = (score / 5) * 100
        c_color = cat_colors.get(cat, "#4f8ef7")
        c_stars = stars_html(round(score))
        detail = cat_details.get(cat, "")
        weight = cat_weights.get(cat, "")
        st.markdown(f"""
        <div class="score-category">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem">
                <div>
                    <span class="score-cat-title">{cat}</span>
                    <span style="font-size:0.65rem;color:var(--muted2);margin-left:0.5rem">({weight})</span>
                </div>
                <div style="display:flex;align-items:center;gap:0.8rem">
                    <span style="font-family:'DM Mono',monospace;font-size:0.9rem;color:{c_color}">{score:.1f}</span>
                    <span style="font-size:1rem;color:{c_color};letter-spacing:0.05em">{c_stars}</span>
                </div>
            </div>
            <div style="font-size:0.75rem;color:var(--muted);margin-bottom:0.4rem">{detail}</div>
            <div class="score-bar-track">
                <div class="score-bar-fill" style="width:{cat_pct:.0f}%;background:{c_color}"></div>
            </div>
        </div>""", unsafe_allow_html=True)

section("Qualitäts-Radar")
cats = list(cat_scores.keys())
vals = [cat_scores[c] for c in cats]
vals_closed = vals + [vals[0]]
cats_closed = cats + [cats[0]]
fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(r=vals_closed, theta=cats_closed, fill="toself",
    fillcolor="rgba(79,142,247,0.15)", line=dict(color="#4f8ef7", width=2), name=ticker))
fig_radar.update_layout(**PLOTLY_LAYOUT, polar=dict(
    bgcolor="rgba(0,0,0,0)",
    radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=9, color="#6b7599"),
                    gridcolor="#1e2540", linecolor="#1e2540"),
    angularaxis=dict(tickfont=dict(size=11, color="#e8ecf4"), gridcolor="#1e2540", linecolor="#1e2540")
), height=400, showlegend=False)
st.plotly_chart(fig_radar, use_container_width=True)

# [3] Gewichtungs-Hinweis aktualisiert
weight_text = "Bewertung 20% · Profitabilität 22% · Wachstum 18% · Bilanz 15% · Technicals 10% · Kapitalstruktur 15%" if "Kapitalstruktur" in cat_scores else "Bewertung 25% · Profitabilität 25% · Wachstum 20% · Bilanz 20% · Technicals 10%"
st.markdown(f"""
<div style="font-size:0.72rem;color:var(--muted2);margin-top:1rem;padding:0.8rem 1rem;background:var(--surface);border-radius:8px;border:1px solid var(--border)">
    <strong>Hinweis:</strong> Der Qualitätsscore basiert auf automatisch berechneten Kennzahlen
    und stellt <em>keine Anlageberatung</em> dar. Er dient als Orientierungshilfe für eine schnelle Einschätzung.
    Gewichtung: {weight_text}
</div>""", unsafe_allow_html=True)
```

# ================================================================

# TAB 8 — PEER-VERGLEICH

# ================================================================

with tabs[7]:
section(“Peer-Vergleich”)
st.markdown(f’<div style="font-size:0.8rem;color:var(--muted);margin-bottom:1rem">Vergleich von <strong style="color:var(--accent)">{ticker}</strong> mit Branchenkonkurrenten.</div>’, unsafe_allow_html=True)

```
with st.spinner("Lade Peer-Daten…"):
    peers = load_peer_data(ticker, sector)

if peers:
    all_companies = [_extract_peer_info(ticker, info)] + peers

    metrics_config = [
        ("Marktkapit.", "marketCap", fmt),
        ("KGV (TTM)", "trailingPE", lambda v: safe(v)),
        ("KGV (Fwd)", "forwardPE", lambda v: safe(v)),
        ("KBV", "priceToBook", lambda v: safe(v)),
        ("Nettomarge", "profitMargins", lambda v: f"{float(v)*100:.1f}%" if v else "N/A"),
        ("Umsatzwachstum", "revenueGrowth", lambda v: f"{float(v)*100:.1f}%" if v else "N/A"),
        ("EKR", "returnOnEquity", lambda v: f"{float(v)*100:.1f}%" if v else "N/A"),
        ("FK/EK", "debtToEquity", lambda v: safe(v)),
        ("Div.-Rendite", "dividendYield", lambda v: f"{float(v)*100:.2f}%" if v else "N/A"),
        ("Beta", "beta", lambda v: safe(v)),
    ]

    header_cells = '<th style="min-width:80px">Kennzahl</th>'
    for comp in all_companies:
        highlight = ' class="peer-highlight"' if comp["ticker"] == ticker else ""
        header_cells += f'<th{highlight}><span style="color:var(--accent)">{comp["ticker"]}</span><br><span style="font-size:0.6rem;font-weight:400;text-transform:none;letter-spacing:0">{comp["name"][:18]}</span></th>'

    rows_html = ""
    for metric_name, key, formatter in metrics_config:
        row_cells = f'<td style="color:var(--muted);font-family:\'DM Sans\',sans-serif;font-size:0.78rem">{metric_name}</td>'
        for comp in all_companies:
            highlight = ' class="peer-highlight"' if comp["ticker"] == ticker else ""
            val = comp.get(key)
            try: formatted = formatter(val)
            except Exception: formatted = "N/A"
            row_cells += f'<td{highlight}>{formatted}</td>'
        rows_html += f'<tr>{row_cells}</tr>'

    st.markdown(f"""
    <div style="overflow-x:auto;margin-bottom:1.5rem">
        <table class="peer-table"><thead><tr>{header_cells}</tr></thead>
        <tbody>{rows_html}</tbody></table>
    </div>""", unsafe_allow_html=True)

    section("Vergleichs-Radar")
    radar_metrics = ["trailingPE", "profitMargins", "revenueGrowth", "returnOnEquity", "beta"]
    radar_labels = ["KGV", "Nettomarge", "Wachstum", "EKR", "Beta"]
    fig_peer_radar = go.Figure()
    peer_colors = ["#4f8ef7", "#22c55e", "#f59e0b", "#7c5cfc", "#ef4444", "#6b7599"]

    for idx, comp in enumerate(all_companies[:4]):
        r_vals = []
        for metric_key in radar_metrics:
            try:
                v = float(comp.get(metric_key, 0) or 0)
                if metric_key == "trailingPE": r_vals.append(max(0, min(5, 5 - (v - 10) / 10)))
                elif metric_key == "profitMargins": r_vals.append(max(0, min(5, v * 20)))
                elif metric_key == "revenueGrowth": r_vals.append(max(0, min(5, v * 15 + 2.5)))
                elif metric_key == "returnOnEquity": r_vals.append(max(0, min(5, v * 15)))
                elif metric_key == "beta": r_vals.append(max(0, min(5, 5 - abs(v - 1) * 2)))
                else: r_vals.append(2.5)
            except (TypeError, ValueError): r_vals.append(0)

        r_vals_closed = r_vals + [r_vals[0]]
        labels_closed = radar_labels + [radar_labels[0]]
        lw = 2.5 if comp["ticker"] == ticker else 1.5
        fo = 0.12 if comp["ticker"] == ticker else 0.04
        c = peer_colors[idx]
        fig_peer_radar.add_trace(go.Scatterpolar(
            r=r_vals_closed, theta=labels_closed, fill="toself",
            fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},{fo})",
            line=dict(color=c, width=lw), name=comp["ticker"]))

    fig_peer_radar.update_layout(**PLOTLY_LAYOUT, polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, range=[0, 5], tickfont=dict(size=9, color="#6b7599"),
                        gridcolor="#1e2540", linecolor="#1e2540"),
        angularaxis=dict(tickfont=dict(size=11, color="#e8ecf4"), gridcolor="#1e2540", linecolor="#1e2540")
    ), height=420, showlegend=True, legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
    st.plotly_chart(fig_peer_radar, use_container_width=True)

    section("Marktkapitalisierung im Vergleich")
    mc_data = [(c["ticker"], c.get("marketCap", 0) or 0) for c in all_companies if c.get("marketCap")]
    if mc_data:
        mc_data.sort(key=lambda x: x[1], reverse=True)
        mc_colors = ["#4f8ef7" if t == ticker else "#252d4a" for t, _ in mc_data]
        fig_mc = go.Figure(go.Bar(
            x=[t for t, _ in mc_data], y=[v / 1e9 for _, v in mc_data],
            marker_color=mc_colors, text=[f"{v/1e9:.0f}B" for _, v in mc_data],
            textposition="outside", textfont=dict(family="DM Mono", size=10, color="#6b7599")))
        fig_mc.update_layout(**PLOTLY_LAYOUT, height=280, yaxis_title=f"Mrd. {currency}", showlegend=False)
        st.plotly_chart(fig_mc, use_container_width=True)
else:
    st.info("Keine Peer-Daten verfügbar. Versuche es mit einem Ticker aus einem größeren Sektor.")
```

# ==================== FOOTER ====================

st.markdown(”—”)
st.markdown(
‘<div style="text-align:center;font-size:0.7rem;color:var(--muted2);font-family:DM Mono,monospace">’
’Equitas · Keine Anlageberatung · Daten: Yahoo Finance, FMP · ’
+ datetime.now().strftime(”%d.%m.%Y %H:%M”) +
‘</div>’, unsafe_allow_html=True)