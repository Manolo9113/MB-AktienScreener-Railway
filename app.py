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
from datetime import datetime, timedelta
import math
# ==================== CONFIG ====================
st.set_page_config(
page_title="Equitas – Stock Intelligence",
page_icon="⬡",
layout="wide",
initial_sidebar_state="expanded",
)
# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+San
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
.eq-logo { font-family: 'DM Serif Display', serif; font-size: 1.1rem; letter-spacing: 0.15em;
.eq-company { font-family: 'DM Serif Display', serif; font-size: 2.4rem; line-height: 1.1; co
.eq-ticker-badge { display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.75r
.eq-price-block { display: flex; align-items: baseline; gap: 1rem; margin: 0.5rem 0 1.5rem; }
.eq-price { font-family: 'DM Mono', monospace; font-size: 3rem; font-weight: 500; color: var(
.eq-change-pos { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--green); }
.eq-change-neg { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--red); }
.eq-sector { font-size: 0.85rem; color: var(--muted); }
/* ---- CARDS ---- */
.eq-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
.eq-card-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em; text-transform:
.eq-card-value { font-family: 'DM Mono', monospace; font-size: 1.6rem; font-weight: 500; colo
.eq-card-sub { font-size: 0.78rem; color: var(--muted); margin-top: 0.35rem; }
/* ---- METRIC ROW ---- */
.eq-metric { display: flex; justify-content: space-between; align-items: center; padding: 0.5
.eq-metric:last-child { border-bottom: none; }
.eq-metric-label { color: var(--muted); }
.eq-metric-value { font-family: 'DM Mono', monospace; color: var(--text); font-size: 0.85rem;
/* ---- GAUGE BAR ---- */
.gauge-wrap { margin: 0.3rem 0 0.1rem; }
.gauge-track { height: 4px; background: var(--border2); border-radius: 2px; overflow: hidden;
.gauge-fill { height: 100%; border-radius: 2px; }
/* ---- SECTION LABELS ---- */
.eq-section { font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--text);
/* ---- NEWS ---- */
.news-item { padding: 0.8rem 0; border-bottom: 1px solid var(--border); }
.news-item:last-child { border-bottom: none; }
.news-headline { font-size: 0.9rem; color: var(--text); line-height: 1.4; margin-bottom: 0.25
.news-meta { font-size: 0.75rem; color: var(--muted); font-family: 'DM Mono', monospace; }
.news-sentiment-pos { color: var(--green); font-weight: 600; }
.news-sentiment-neg { color: var(--red); font-weight: 600; }
.news-sentiment-neu { color: var(--muted); font-weight: 600; }
/* ---- FAIR VALUE ---- */
.fv-positive { color: var(--green); }
.fv-negative { color: var(--red); }
.fv-label { font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(
.fv-value { font-family: 'DM Mono', monospace; font-size: 2rem; font-weight: 500; }
.fv-range { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: var(--muted); }
/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] { gap: 0; background: var(--surface); border-radius: 10px;
.stTabs [data-baseweb="tab"] { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; font-w
.stTabs [aria-selected="true"] { background: var(--surface2) !important; color: var(--text) !
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }
/* ---- INPUTS ---- */
.stTextInput > div > div { background: var(--surface) !important; border: 1px solid var(--bor
.stTextInput label { color: var(--muted) !important; font-size: 0.75rem !important; }
.stSelectbox > div > div { background: var(--surface) !important; border: 1px solid var(--bor
/* ---- SIDEBAR ---- */
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px s
section[data-testid="stSidebar"] .block-container { padding: 1rem 1.2rem; }
/* ---- SEARCH RESULTS DROPDOWN ---- */
.search-result-item { padding: 0.5rem 0.8rem; border-radius: 6px; cursor: pointer; font-size:
.search-result-ticker { font-family: 'DM Mono', monospace; color: var(--accent); font-weight:
.search-result-name { color: var(--muted); font-size: 0.75rem; margin-top: 0.1rem; }
/* ---- STAR SCORE ---- */
.star-score { font-size: 2rem; line-height: 1; color: var(--amber); letter-spacing: 0.1em; }
.star-empty { color: var(--border2); }
.score-category { background: var(--surface2); border: 1px solid var(--border); border-radius
.score-cat-title { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform
.score-cat-stars { font-size: 1.1rem; }
.score-bar-track { height: 6px; background: var(--border2); border-radius: 3px; margin-top: 0
.score-bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease; }
/* ---- DILUTION CARDS ---- */
.dilution-highlight { background: linear-gradient(135deg, rgba(79,142,247,0.1), rgba(124,92,2
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
.js-plotly-plot .plotly { background: transparent !important; }
/* ---- SIGNAL BADGE ---- */
.signal { display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
.signal-buy { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(3
.signal-sell { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(23
.signal-hold { background: rgba(245,158,11,0.15); color: var(--amber); border: 1px solid rgba
/* ---- WATCHLIST ---- */
.wl-item { display: flex; justify-content: space-between; align-items: center; padding: 0.6re
.wl-ticker { font-family: 'DM Mono', monospace; font-weight: 500; color: var(--accent); }
.wl-change-pos { font-family: 'DM Mono', monospace; color: var(--green); font-size: 0.8rem; }
.wl-change-neg { font-family: 'DM Mono', monospace; color: var(--red); font-size: 0.8rem; }
/* ---- STMETRIC OVERRIDE ---- */
[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--border); borde
[data-testid="stMetricLabel"] p { font-size: 0.7rem !important; letter-spacing: 0.1em; text-t
[data-testid="stMetricValue"] { font-family: 'DM Mono', monospace !important; font-size: 1.5r
[data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; font-size: 0.8r
/* ---- MOBILE RESPONSIVE ---- */
@media (max-width: 768px) {
.eq-price { font-size: 2rem; }
.eq-company { font-size: 1.6rem; }
.stTabs [data-baseweb="tab"] { padding: 0.4rem 0.6rem; font-size: 0.72rem; }
.eq-logo-img, .eq-logo-placeholder { width: 48px; height: 48px; }
}
</style>
""", unsafe_allow_html=True)
# ==================== SESSION STATE ====================
if "ticker" not in st.session_state:
st.session_state.ticker = "AAPL"
if "watchlist" not in st.session_state:
st.session_state.watchlist = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]
if "search_results" not in st.session_state:
st.session_state.search_results = []
# ==================== API KEYS ====================
FMP_API_KEY = os.getenv("FMP_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
# ==================== LOGO HELPER ====================
@st.cache_data(ttl=86400)
def get_company_logo_url(ticker: str, domain: str = "") -> str:
"""
Returns a working logo URL for the ticker.
Priority:
1. FMP (if key available)
2. Clearbit Logo API via company domain
3. Logo.dev (free tier)
4. Empty string (triggers placeholder)
"""
# 1) FMP company profile has logo URL
if FMP_API_KEY:
try:
url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API
r = requests.get(url, timeout=6)
if r.status_code == 200:
data = r.json()
if data and isinstance(data, list) and data[0].get("image"):
return data[0]["image"]
except:
pass
# 2) Try Clearbit with domain if available
if domain:
clearbit_url = f"https://logo.clearbit.com/{domain}"
try:
r = requests.head(clearbit_url, timeout=5)
if r.status_code == 200:
return clearbit_url
except:
pass
# 3) Logo.dev free tier (no key needed for basic use)
# We'll just return the Clearbit URL pattern and let the browser handle it
# Map common tickers to domains as fallback
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
def logo_html(ticker: str, domain: str = "", size: int = 64) -> str:
"""Returns HTML for the company logo with fallback to initials placeholder."""
logo_url = get_company_logo_url(ticker, domain)
initials = ticker[:2].upper()
border_radius = "14px"
if logo_url:
return f"""
<img
src="{logo_url}"
class="eq-logo-img"
width="{size}" height="{size}"
onerror="this.style.display='none';document.getElementById('logo-fallback-{ticker}'
style="width:{size}px;height:{size}px;border-radius:{border_radius};background:var(
/>
<div id="logo-fallback-{ticker}"
style="display:none;width:{size}px;height:{size}px;border-radius:{border_radius};ba
{initials}
</div>
"""
else:
return f"""
<div style="width:{size}px;height:{size}px;border-radius:{border_radius};background:l
{initials}
</div>
"""
# ==================== ISIN/WKN LOOKUP ====================
ISIN_WKN_MAP = {}
@st.cache_data(ttl=3600)
def search_ticker(query: str):
"""Search by name, ticker, ISIN or WKN"""
results = []
q = query.strip()
if not q or len(q) < 2:
return results
# 1) Try FMP search (name + ticker)
if FMP_API_KEY:
try:
url = f"https://financialmodelingprep.com/api/v3/search?query={q}&limit=8&apikey=
r = requests.get(url, timeout=8)
if r.status_code == 200:
for item in r.json():
results.append({
"ticker": item.get("symbol", ""),
"name": item.get("name", ""),
"exchange": item.get("exchangeShortName", ""),
"type": "FMP"
})
except:
pass
# 2) ISIN search via FMP
if len(q) == 12 and q[:2].isalpha():
try:
url2 = f"https://financialmodelingprep.com/api/v3/search?query={q}&limit=5&apikey
r2 = requests.get(url2, timeout=8)
if r2.status_code == 200:
for item in r2.json():
results.append({
"ticker": item.get("symbol", ""),
"name": item.get("name", "") + " (ISIN)",
"exchange": item.get("exchangeShortName", ""),
"type": "ISIN"
})
except:
pass
# 3) Fallback: yfinance search
if not results:
try:
test = yf.Ticker(q)
info = test.get_info() if hasattr(test, "get_info") else test.info
if info and info.get("longName"):
results.append({
"ticker": q.upper(),
"name": info.get("longName", q),
"exchange": info.get("exchange", ""),
"type": "Direct"
})
except:
pass
# Deduplicate
seen = set()
unique = []
for r in results:
if r["ticker"] and r["ticker"] not in seen:
seen.add(r["ticker"])
unique.append(r)
return unique[:8]
# ==================== CACHE / DATA LOADERS ====================
@st.cache_data(ttl=3600)
def load_yfinance(ticker: str):
stock = yf.Ticker(ticker)
try:
info = stock.get_info() if hasattr(stock, "get_info") else stock.info
except:
info = {}
try:
hist = stock.history(period="5y", auto_adjust=True)
except:
hist = pd.DataFrame()
try:
fins = stock.financials
except:
fins = pd.DataFrame()
try:
balance = stock.balance_sheet
except:
balance = pd.DataFrame()
try:
cashflow = stock.cashflow
except:
cashflow = pd.DataFrame()
try:
dividends = stock.dividends
except:
dividends = pd.Series()
return info, hist, fins, balance, cashflow, dividends
@st.cache_data(ttl=3600)
def load_shares_history(ticker: str):
"""Load historical shares outstanding data"""
stock = yf.Ticker(ticker)
shares_data = {}
try:
quarterly_bs = stock.quarterly_balance_sheet
if quarterly_bs is not None and not quarterly_bs.empty:
share_rows = [r for r in quarterly_bs.index if "Share" in str(r) or "Common Stock
if share_rows:
shares_data["quarterly"] = quarterly_bs.loc[share_rows[0]].dropna()
except:
pass
try:
annual_bs = stock.balance_sheet
if annual_bs is not None and not annual_bs.empty:
share_rows = [r for r in annual_bs.index if "Share" in str(r) or "Common Stock" i
if share_rows:
shares_data["annual"] = annual_bs.loc[share_rows[0]].dropna()
except:
pass
try:
cf = stock.cashflow
if cf is not None and not cf.empty:
sbc_rows = [r for r in cf.index if "Stock" in str(r) and ("Based" in str(r) or "C
if sbc_rows:
shares_data["sbc"] = cf.loc[sbc_rows[0]].dropna()
repurchase_rows = [r for r in cf.index if "Repurchase" in str(r) or "Buyback" in
if repurchase_rows:
shares_data["buybacks"] = cf.loc[repurchase_rows[0]].dropna()
except:
pass
return shares_data
@st.cache_data(ttl=86400)
def load_fmp_metrics(ticker: str):
if not FMP_API_KEY:
return {}, {}, []
try:
url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP
r = requests.get(url, timeout=10)
metrics = r.json()[0] if r.status_code == 200 and isinstance(r.json(), list) else {}
except:
metrics = {}
try:
url2 = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={FMP_API
r2 = requests.get(url2, timeout=10)
ratios = r2.json()[0] if r2.status_code == 200 and isinstance(r2.json(), list) else {
except:
ratios = {}
try:
url3 = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?limit=4&
r3 = requests.get(url3, timeout=10)
estimates = r3.json() if r3.status_code == 200 else []
except:
estimates = []
return metrics, ratios, estimates
@st.cache_data(ttl=3600)
def load_news(ticker: str, company: str):
articles = []
if NEWS_API_KEY:
try:
query = f"{company} stock" if company else ticker
url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=e
r = requests.get(url, timeout=8)
if r.status_code == 200:
articles = r.json().get("articles", [])
except:
pass
if not articles:
try:
stock = yf.Ticker(ticker)
raw = stock.news or []
for n in raw[:8]:
articles.append({
"title": n.get("title", ""),
"url": n.get("link", "#"),
"publishedAt": datetime.fromtimestamp(n.get("providerPublishTime", 0)).is
"source": {"name": n.get("publisher", "")},
"sentiment": None
})
except:
pass
return articles
# ==================== HELPERS ====================
def safe(v, digits=2, suffix=""):
try:
return f"{float(v):.{digits}f}{suffix}"
except:
return "N/A"
def fmt(value):
try:
value = float(value)
except:
return "N/A"
if abs(value) >= 1e12: return f"{value/1e12:.2f}T"
if abs(value) >= 1e9: return f"{value/1e9:.2f}B"
if abs(value) >= 1e6: return f"{value/1e6:.2f}M"
return f"{value:.2f}"
def safe_pct(a, b):
try:
return (float(a) - float(b)) / abs(float(b)) * 100
except:
return 0.0
def color_val(v, good_positive=True):
try:
f = float(v)
if f > 0:
return "var(--green)" if good_positive else "var(--red)"
elif f < 0:
return "var(--red)" if good_positive else "var(--green)"
else:
return "var(--muted)"
except:
return "var(--muted)"
def metric_row(label, value, color=None):
c = f'color:{color};' if color else ''
st.markdown(f"""
<div class="eq-metric">
<span class="eq-metric-label">{label}</span>
<span class="eq-metric-value" style="{c}">{value}</span>
</div>""", unsafe_allow_html=True)
def section(title):
st.markdown(f'<div class="eq-section">{title}</div>', unsafe_allow_html=True)
def card(title, value, sub=""):
st.markdown(f"""
<div class="eq-card">
<div class="eq-card-title">{title}</div>
<div class="eq-card-value">{value}</div>
<div class="eq-card-sub">{sub}</div>
</div>""", unsafe_allow_html=True)
def stars_html(score_0_to_5):
"""Render star rating HTML"""
full = int(round(score_0_to_5))
full = max(0, min(5, full))
stars = ""
for i in range(5):
if i < full:
stars += "★"
else:
stars += '<span class="star-empty">★</span>'
return f'<span class="star-score">{stars}</span>'
def score_bar_html(pct, color):
return f"""<div class="score-bar-track">
<div class="score-bar-fill" style="width:{pct:.0f}%;background:{color}"></div>
</div>"""
# ==================== COMPANY QUALITY SCORE ====================
def compute_quality_score(info, df_tech, hist, fmp_metrics):
scores = {}
details = {}
# --- VALUATION ---
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
except: pass
try:
pb_f = float(pb)
if 0 < pb_f < 1.5: pts += 5
elif 0 < pb_f < 3: pts += 4
elif 0 < pb_f < 5: pts += 3
elif 0 < pb_f < 10: pts += 2
elif pb_f > 0: pts += 1
count += 1
except: pass
try:
peg_f = float(peg)
if 0 < peg_f < 1: pts += 5
elif 0 < peg_f < 1.5: pts += 4
elif 0 < peg_f < 2: pts += 3
elif 0 < peg_f < 3: pts += 2
count += 1
except: pass
if count > 0:
val_score = pts / count
scores["Bewertung"] = min(5, val_score)
details["Bewertung"] = f"P/E: {safe(pe)} · P/B: {safe(pb)} · PEG: {safe(peg)}"
# --- PROFITABILITY ---
prof_pts = 0
prof_count = 0
margin = info.get("profitMargins")
roe = info.get("returnOnEquity")
roa = info.get("returnOnAssets")
gross = info.get("grossMargins")
try:
m = float(margin)
if m > 0.20: prof_pts += 5
elif m > 0.10: prof_pts += 4
elif m > 0.05: prof_pts += 3
elif m > 0: prof_pts += 2
else: prof_pts += 0
prof_count += 1
except: pass
try:
r = float(roe)
if r > 0.25: prof_pts += 5
elif r > 0.15: prof_pts += 4
elif r > 0.08: prof_pts += 3
elif r > 0: prof_pts += 2
prof_count += 1
except: pass
try:
ra = float(roa)
if ra > 0.15: prof_pts += 5
elif ra > 0.08: prof_pts += 4
elif ra > 0.03: prof_pts += 3
elif ra > 0: prof_pts += 2
prof_count += 1
except: pass
try:
gm = float(gross)
if gm > 0.50: prof_pts += 5
elif gm > 0.30: prof_pts += 4
elif gm > 0.15: prof_pts += 3
elif gm > 0: prof_pts += 2
prof_count += 1
except: pass
prof_score = (prof_pts / prof_count) if prof_count > 0 else 2.5
scores["Profitabilität"] = min(5, prof_score)
details["Profitabilität"] = f"Nettomarge: {safe(margin,'%')} · ROE: {safe(roe,'%')} · Bru
# --- GROWTH ---
grow_pts = 0
grow_count = 0
rev_growth = info.get("revenueGrowth")
earn_growth = info.get("earningsGrowth")
try:
rg = float(rev_growth)
if rg > 0.25: grow_pts += 5
elif rg > 0.15: grow_pts += 4
elif rg > 0.08: grow_pts += 3
elif rg > 0: grow_pts += 2
else: grow_pts += 1
grow_count += 1
except: pass
try:
eg = float(earn_growth)
if eg > 0.25: grow_pts += 5
elif eg > 0.15: grow_pts += 4
elif eg > 0.08: grow_pts += 3
elif eg > 0: grow_pts += 2
else: grow_pts += 1
grow_count += 1
except: pass
grow_score = (grow_pts / grow_count) if grow_count > 0 else 2.5
scores["Wachstum"] = min(5, grow_score)
details["Wachstum"] = f"Umsatz: {safe(rev_growth,'%')} · Gewinn: {safe(earn_growth,'%')}"
# --- BALANCE SHEET ---
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
except: pass
try:
c = float(cr)
if c > 2.5: bal_pts += 5
elif c > 1.5: bal_pts += 4
elif c > 1.0: bal_pts += 3
elif c > 0.7: bal_pts += 2
else: bal_pts += 1
bal_count += 1
except: pass
try:
f = float(fcf)
if f > 0: bal_pts += 4
else: bal_pts += 1
bal_count += 1
except: pass
bal_score = (bal_pts / bal_count) if bal_count > 0 else 2.5
scores["Bilanzqualität"] = min(5, bal_score)
details["Bilanzqualität"] = f"D/E: {safe(de)} · Current Ratio: {safe(cr)} · FCF: {fmt(fcf
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
except: pass
try:
if float(price_now) > float(ma50): tech_pts += 4
else: tech_pts += 2
tech_count += 1
except: pass
try:
if float(ma50) > float(ma200): tech_pts += 5
else: tech_pts += 2
tech_count += 1
except: pass
try:
if float(macd) > float(signal): tech_pts += 4
else: tech_pts += 2
tech_count += 1
except: pass
tech_score = (tech_pts / tech_count) if tech_count > 0 else 2.5
scores["Technicals"] = min(5, tech_score)
details["Technicals"] = f"RSI: {safe(rsi)} · {'Above MA50 ✓' if (price_now and ma50 and p
# --- OVERALL (weighted) ---
weights = {"Bewertung": 0.25, "Profitabilität": 0.25, "Wachstum": 0.20, "Bilanzqualität":
overall = sum(scores.get(k, 2.5) * w for k, w in weights.items())
return overall, scores, details
# ==================== DCF / FAIR VALUE ====================
def compute_fair_value(info, hist):
try:
eps = info.get("trailingEps") or info.get("epsTrailingTwelveMonths")
growth = info.get("earningsGrowth") or info.get("revenueGrowth") or 0.08
pe = info.get("trailingPE") or 20
shares = info.get("sharesOutstanding", 1)
bvps = info.get("bookValue", 0)
graham = None
if eps and bvps and float(eps) > 0 and float(bvps) > 0:
graham = (22.5 * float(eps) * float(bvps)) ** 0.5
dcf = None
fcf = info.get("freeCashflow")
if fcf and shares:
fcf_ps = float(fcf) / float(shares)
g = min(max(float(growth), 0.0), 0.25)
discount = 0.10
terminal_pe = 15
pv = 0
for yr in range(1, 11):
pv += fcf_ps * (1 + g) ** yr / (1 + discount) ** yr
terminal = fcf_ps * (1 + g) ** 10 * terminal_pe / (1 + discount) ** 10
dcf = pv + terminal
pe_target = None
if eps and pe:
pe_target = float(eps) * min(float(pe) * 1.0, 30)
values = [v for v in [graham, dcf, pe_target] if v and v > 0]
if not values:
return None, None, None
fair = np.mean(values)
lo = fair * 0.80
hi = fair * 1.20
return fair, lo, hi
except:
return None, None, None
# ==================== TECHNICALS ====================
def compute_technicals(hist):
df = hist.copy()
df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()
df["MA200"] = df["Close"].rolling(200).mean()
delta = df["Close"].diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = (-delta.clip(upper=0)).rolling(14).mean()
rs = gain / loss.replace(0, np.nan)
df["RSI"] = 100 - 100 / (1 + rs)
ema12 = df["Close"].ewm(span=12).mean()
ema26 = df["Close"].ewm(span=26).mean()
df["MACD"] = ema12 - ema26
df["Signal"] = df["MACD"].ewm(span=9).mean()
df["Hist"] = df["MACD"] - df["Signal"]
df["BB_mid"] = df["Close"].rolling(20).mean()
std = df["Close"].rolling(20).std()
df["BB_up"] = df["BB_mid"] + 2 * std
df["BB_dn"] = df["BB_mid"] - 2 * std
df["Vol_MA20"] = df["Volume"].rolling(20).mean()
return df
# ==================== PLOTLY THEME ====================
PLOTLY_LAYOUT = dict(
template="plotly_dark",
paper_bgcolor="rgba(0,0,0,0)",
plot_bgcolor="rgba(0,0,0,0)",
font=dict(family="DM Mono, monospace", color="#6b7599", size=11),
xaxis=dict(gridcolor="#1e2540", zeroline=False, showline=False),
yaxis=dict(gridcolor="#1e2540", zeroline=False, showline=False),
margin=dict(l=0, r=0, t=30, b=0),
hoverlabel=dict(bgcolor="#111520", bordercolor="#252d4a", font_family="DM Mono, monospace
legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
)
# ==================== SIDEBAR ====================
with st.sidebar:
st.markdown('<div class="eq-logo">⬡ Equitas</div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown('<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;c
search_input = st.text_input(
"Suche",
value="",
placeholder="z. B. Apple, AAPL, US0378331005…",
label_visibility="collapsed",
key="search_box"
)
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
st.markdown('<div style="font-size:0.78rem;color:var(--muted);padding:0.4rem 0">K
else:
ticker_input = st.text_input(
"Oder direkter Ticker",
value=st.session_state.ticker,
placeholder="z. B. AAPL",
label_visibility="collapsed",
key="ticker_direct"
)
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
st.markdown('<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;c
wl_cols = st.columns([4, 1])
new_wl = wl_cols[0].text_input(
"Neues Symbol",
placeholder="Hinzufügen…",
label_visibility="collapsed",
key="wl_input"
)
if wl_cols[1].button("＋", use_container_width=True) and new_wl:
t = new_wl.upper().strip()
if t and t not in st.session_state.watchlist:
st.session_state.watchlist.append(t)
for wt in st.session_state.watchlist[:]:
try:
_info, _hist, *_ = load_yfinance(wt)
if not _hist.empty:
_p = float(_hist["Close"].iloc[-1])
_pp = float(_hist["Close"].iloc[-2]) if len(_hist) > 1 else _p
_chg = safe_pct(_p, _pp)
chg_cls = "wl-change-pos" if _chg >= 0 else "wl-change-neg"
arrow = "▲" if _chg >= 0 else "▼"
st.markdown(f"""
<div class="wl-item">
<span class="wl-ticker">{wt}</span>
<span class="{chg_cls}">{arrow} {abs(_chg):.2f}%</span>
</div>""", unsafe_allow_html=True)
except:
pass
st.markdown("---")
st.markdown(
f'<div style="font-size:0.7rem;color:var(--muted2)">API Status<br>'
f'FMP: {" " if FMP_API_KEY else " "} &nbsp; News: {" " if NEWS_API_KEY else " "}
unsafe_allow_html=True
)
# ==================== MOBILE SEARCH FALLBACK ====================
st.markdown(f"""
<div class="mobile-search-hint">
Aktuell: <strong style="color:var(--accent)">{ticker}</strong> — Tippe in der Sidebar um zu
</div>
""", unsafe_allow_html=True)
if not ticker:
st.stop()
# ==================== LOAD DATA ====================
with st.spinner(""):
info, hist, fins, balance, cashflow, dividends = load_yfinance(ticker)
fmp_metrics, fmp_ratios, fmp_estimates = load_fmp_metrics(ticker)
shares_history = load_shares_history(ticker)
if hist is None or hist.empty:
st.error(" Keine Kursdaten gefunden. Bitte prüfe den Ticker.")
st.stop()
# ==================== DERIVED ====================
price = float(hist["Close"].iloc[-1])
prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
change = price - prev
chg_pct = safe_pct(price, prev)
high52 = float(hist["High"].rolling(252).max().iloc[-1]) if len(hist) > 252 else float(hist["
low52 = float(hist["Low"].rolling(252).min().iloc[-1]) if len(hist) > 252 else float(hist["Lo
fair_val, fv_lo, fv_hi = compute_fair_value(info, hist)
df_tech = compute_technicals(hist)
company = info.get("longName", ticker)
sector = info.get("sector", "")
industry = info.get("industry", "")
currency = info.get("currency", "USD")
website = info.get("website", "")
rsi_now = float(df_tech["RSI"].iloc[-1]) if not df_tech["RSI"].isna().all() else None
overall_score, cat_scores, cat_details = compute_quality_score(info, df_tech, hist, fmp_metri
# Extract domain from website for logo lookup
company_domain = ""
if website:
try:
from urllib.parse import urlparse
parsed = urlparse(website)
company_domain = parsed.netloc.replace("www.", "")
except:
pass
# ==================== HEADER ====================
arrow = "▲" if change >= 0 else "▼"
chg_color = "var(--green)" if change >= 0 else "var(--red)"
logo_tag = logo_html(ticker, company_domain, size=64)
st.markdown(f"""
<div class="eq-header">
{logo_tag}
<div>
<div style="font-size:0.7rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--m
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
# ==================== KPI STRIP ====================
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
with kpi1:
card("Market Cap", fmt(info.get("marketCap")), "Gesamtbewertung")
with kpi2:
card("P/E (TTM)", safe(info.get("trailingPE")), "Kurs / Gewinn")
with kpi3:
card("EPS (TTM)", safe(info.get("trailingEps"), suffix=" " + currency), "Earnings per Sha
with kpi4:
card("52W Hoch", f"{currency} {high52:,.2f}", f"Tief: {currency} {low52:,.2f}")
with kpi5:
card("Beta", safe(info.get("beta")), "Marktsensitivität")
with kpi6:
fv_disp = f"{currency} {fair_val:,.2f}" if fair_val else "N/A"
fv_diff = safe_pct(fair_val, price) if fair_val else None
fv_sub = f"{fv_diff:+.1f}% vs. Kurs" if fv_diff is not None else "Keine Schätzung"
card("Fair Value (Est.)", fv_disp, fv_sub)
st.markdown("<br>", unsafe_allow_html=True)
# ==================== TABS ====================
tabs = st.tabs([" Chart & Technicals", " Fundamentals", " Fair Value & DCF", " News"
# ================================================================
# TAB 1 — CHART & TECHNICALS
# ================================================================
with tabs[0]:
try:
cutoff = {
"1mo": hist.index[-1] - timedelta(days=30),
"3mo": hist.index[-1] - timedelta(days=90),
"6mo": hist.index[-1] - timedelta(days=180),
"1y": hist.index[-1] - timedelta(days=365),
"2y": hist.index[-1] - timedelta(days=730),
"5y": hist.index[-1] - timedelta(days=1825),
}[chart_period]
df_view = df_tech[df_tech.index >= cutoff]
except:
df_view = df_tech
overlay_opts = st.multiselect(
"Overlays", ["MA20", "MA50", "MA200", "Bollinger Bands"], default=["MA50", "MA200"],
label_visibility="collapsed"
)
fig = make_subplots(
rows=3, cols=1,
shared_xaxes=True,
row_heights=[0.6, 0.2, 0.2],
vertical_spacing=0.04,
subplot_titles=("", "Volumen", "RSI (14)")
)
fig.add_trace(go.Candlestick(
x=df_view.index,
open=df_view["Open"], high=df_view["High"],
low=df_view["Low"], close=df_view["Close"],
increasing_line_color="#22c55e", decreasing_line_color="#ef4444",
increasing_fillcolor="#22c55e", decreasing_fillcolor="#ef4444",
name="OHLC", showlegend=False, line_width=1
), row=1, col=1)
colors = {"MA20": "#f59e0b", "MA50": "#4f8ef7", "MA200": "#7c5cfc"}
for ma in ["MA20", "MA50", "MA200"]:
if ma in overlay_opts:
fig.add_trace(go.Scatter(
x=df_view.index, y=df_view[ma], name=ma,
line=dict(color=colors[ma], width=1.2, dash="dot"),
opacity=0.85
), row=1, col=1)
if "Bollinger Bands" in overlay_opts:
fig.add_trace(go.Scatter(
x=df_view.index, y=df_view["BB_up"], name="BB Upper",
line=dict(color="#6b7599", width=1, dash="dash"), showlegend=True
), row=1, col=1)
fig.add_trace(go.Scatter(
x=df_view.index, y=df_view["BB_dn"], name="BB Lower",
line=dict(color="#6b7599", width=1, dash="dash"),
fill="tonexty", fillcolor="rgba(107,117,153,0.06)", showlegend=False
), row=1, col=1)
if fair_val and fv_lo and fv_hi:
fig.add_hrect(y0=fv_lo, y1=fv_hi, fillcolor="rgba(79,142,247,0.08)",
line_width=0, row=1, col=1,
annotation_text=f"Fair Value ~{currency}{fair_val:,.0f}",
annotation_position="top left",
annotation_font=dict(color="#4f8ef7", size=10))
fig.add_hline(y=fair_val, line_color="#4f8ef7", line_dash="dash",
line_width=1, opacity=0.6, row=1, col=1)
vol_colors = ["#22c55e" if c >= o else "#ef4444"
for c, o in zip(df_view["Close"], df_view["Open"])]
fig.add_trace(go.Bar(
x=df_view.index, y=df_view["Volume"],
marker_color=vol_colors, opacity=0.7, name="Volumen", showlegend=False
), row=2, col=1)
fig.add_trace(go.Scatter(
x=df_view.index, y=df_view["Vol_MA20"],
line=dict(color="#f59e0b", width=1), name="Vol MA20", showlegend=False
), row=2, col=1)
fig.add_trace(go.Scatter(
x=df_view.index, y=df_view["RSI"],
line=dict(color="#7c5cfc", width=1.5), name="RSI", showlegend=False
), row=3, col=1)
fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.08)", line_width=0, row=3, col=1
fig.add_hrect(y0=0, y1=30, fillcolor="rgba(34,197,94,0.08)", line_width=0, row=3, col=1)
fig.add_hline(y=70, line_color="#ef4444", line_dash="dot", line_width=1, opacity=0.4, row
fig.add_hline(y=30, line_color="#22c55e", line_dash="dot", line_width=1, opacity=0.4, row
layout = PLOTLY_LAYOUT.copy()
layout["legend"] = dict(orientation="h", y=1.02, x=0)
fig.update_layout(**layout, height=640, showlegend=True)
fig.update_xaxes(rangeslider_visible=False)
fig.update_yaxes(tickprefix=f"{currency} ", row=1, col=1)
st.plotly_chart(fig, use_container_width=True)
section("Technische Signale")
t1, t2, t3, t4 = st.columns(4)
with t1:
rsi_color = "var(--red)" if (rsi_now and rsi_now > 70) else "var(--green)" if (rsi_no
rsi_label = "Überkauft" if (rsi_now and rsi_now > 70) else "Überverkauft" if (rsi_now
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
<div class="eq-card-value" style="color:{'var(--green)' if macd_bull else 'var(--re
<div class="eq-card-sub">Signal: {safe(sig_now)} — {'Bullish' if macd_bull else 'Be
</div>""", unsafe_allow_html=True)
with t3:
ma50 = df_tech["MA50"].iloc[-1]
ma200 = df_tech["MA200"].iloc[-1]
above = price > ma50 and price > ma200
golden = ma50 > ma200
st.markdown(f"""<div class="eq-card">
<div class="eq-card-title">Trend (MA)</div>
<div class="eq-card-value" style="color:{'var(--green)' if above else 'var(--red)'}
<div class="eq-card-sub">{'Golden Cross ✓' if golden else 'Death Cross ✗'} · MA50:
</div>""", unsafe_allow_html=True)
with t4:
pos52 = (price - low52) / (high52 - low52) * 100 if (high52 - low52) != 0 else 50
st.markdown(f"""<div class="eq-card">
<div class="eq-card-title">52W Position</div>
<div class="eq-card-value">{pos52:.0f}%</div>
<div class="eq-card-sub">Tief {currency}{low52:,.2f} · Hoch {currency}{high52:,.2f}
<div class="gauge-wrap">
<div class="gauge-track">
<div class="gauge-fill" style="width:{pos52:.0f}%;background:{'var(--green)' if
</div>
</div>
</div>""", unsafe_allow_html=True)
section("Performance")
periods = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1J": 252, "3J": 756, "5J": 1260}
perf_data = {}
for label, days in periods.items():
if len(hist) > days:
p0 = float(hist["Close"].iloc[-days-1])
perf_data[label] = safe_pct(price, p0)
if perf_data:
fig_perf = go.Figure(go.Bar(
x=list(perf_data.keys()),
y=list(perf_data.values()),
marker_color=["#22c55e" if v >= 0 else "#ef4444" for v in perf_data.values()],
text=[f"{v:+.1f}%" for v in perf_data.values()],
textposition="outside",
textfont=dict(family="DM Mono, monospace", size=11)
))
fig_perf.update_layout(**PLOTLY_LAYOUT, height=280, yaxis_ticksuffix="%", showlegend=
st.plotly_chart(fig_perf, use_container_width=True)
# ================================================================
# TAB 2 — FUNDAMENTALS
# ================================================================
with tabs[1]:
col_l, col_r = st.columns([1, 1])
with col_l:
section("Bewertung")
metric_row("P/E (TTM)", safe(info.get("trailingPE")))
metric_row("P/E (Forward)", safe(info.get("forwardPE")))
metric_row("P/B", safe(info.get("priceToBook")))
metric_row("P/S (TTM)", safe(info.get("priceToSalesTrailing12Months")))
metric_row("EV/EBITDA", safe(fmp_metrics.get("enterpriseValueOverEBITDATTM") or info.
metric_row("PEG Ratio", safe(info.get("pegRatio")))
section("Profitabilität")
metric_row("Bruttomarge", safe(info.get("grossMargins"), suffix="%") if info.get("gro
metric_row("EBITDA Marge", safe(info.get("ebitdaMargins"), suffix="%"))
metric_row("Nettomarge", safe(info.get("profitMargins"), suffix="%"))
metric_row("ROE", safe(info.get("returnOnEquity"), suffix="%"))
metric_row("ROA", safe(info.get("returnOnAssets"), suffix="%"))
metric_row("ROIC (TTM)", safe(fmp_metrics.get("returnOnInvestedCapitalTTM"), suffix="
with col_r:
section("Wachstum")
metric_row("Umsatzwachstum (YoY)", safe(info.get("revenueGrowth"), suffix="%"))
metric_row("Gewinnwachstum (YoY)", safe(info.get("earningsGrowth"), suffix="%"))
metric_row("EPS Wachstum (5J)", safe(info.get("earningsQuarterlyGrowth"), suffix="%")
section("Finanzkraft")
metric_row("Total Debt", fmt(info.get("totalDebt")))
metric_row("Cash & Equivalents", fmt(info.get("totalCash")))
metric_row("Debt/Equity", safe(info.get("debtToEquity")))
metric_row("Current Ratio", safe(info.get("currentRatio")))
metric_row("Quick Ratio", safe(info.get("quickRatio")))
metric_row("Free Cash Flow", fmt(info.get("freeCashflow")))
section("Dividende")
metric_row("Dividendenrendite", safe(info.get("dividendYield"), suffix="%"))
metric_row("Dividende (annual)", safe(info.get("dividendRate"), suffix=f" {currency}"
metric_row("Payout Ratio", safe(info.get("payoutRatio"), suffix="%"))
metric_row("5J Div. Wachstum", safe(info.get("fiveYearAvgDividendYield"), suffix="%")
if not fins.empty:
section("Umsatz & Gewinn Verlauf")
rev_row = [r for r in fins.index if "Revenue" in str(r) or "Total Revenue" in str(r)]
net_row = [r for r in fins.index if "Net Income" in str(r)]
if rev_row or net_row:
fig_fin = go.Figure()
if rev_row:
rev_vals = fins.loc[rev_row[0]].dropna()
fig_fin.add_trace(go.Bar(
x=rev_vals.index.astype(str), y=rev_vals.values,
name="Umsatz", marker_color="#4f8ef7", opacity=0.7
))
if net_row:
net_vals = fins.loc[net_row[0]].dropna()
fig_fin.add_trace(go.Bar(
x=net_vals.index.astype(str), y=net_vals.values,
name="Nettogewinn", marker_color="#22c55e", opacity=0.8
))
fig_fin.update_layout(**PLOTLY_LAYOUT, height=300, barmode="group",
yaxis_tickprefix=f"{currency} ")
st.plotly_chart(fig_fin, use_container_width=True)
# ================================================================
# TAB 3 — FAIR VALUE & DCF
# ================================================================
with tabs[2]:
fv_col, dcf_col = st.columns([1, 1])
with fv_col:
section("Fair Value Schätzung")
if fair_val:
upside = safe_pct(fair_val, price)
fv_color = "var(--green)" if upside > 0 else "var(--red)"
label = "Unterbewertet" if upside > 10 else "Überbewertet" if upside < -10 else "
st.markdown(f"""
<div class="eq-card">
<div class="fv-label">Intrinsic Value Estimate</div>
<div class="fv-value" style="color:{fv_color}">{currency} {fair_val:,.2f}</div>
<div class="fv-range">Range: {currency} {fv_lo:,.2f} — {currency} {fv_hi:,.2f}<
<br>
<div style="display:flex;gap:1rem;align-items:center">
<div>
<div class="fv-label">Kurspreis</div>
<div style="font-family:'DM Mono',monospace;font-size:1.2rem">{currency} {p
</div>
<div>
<div class="fv-label">Upside/Downside</div>
<div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{fv_colo
</div>
<div>
<div class="fv-label">Einschätzung</div>
<div style="font-size:0.85rem;margin-top:0.2rem">
<span class="signal {'signal-buy' if upside>10 else 'signal-sell' if upsi
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
fig_fv = go.Figure()
fig_fv.add_trace(go.Indicator(
mode="gauge+number+delta",
value=price,
delta={"reference": fair_val, "valueformat": ".2f",
"increasing": {"color": "#22c55e"}, "decreasing": {"color": "#ef4444"}
title={"text": f"Kurs vs. Fair Value ({currency})", "font": {"size": 13, "col
gauge={
"axis": {"range": [fv_lo * 0.7, fv_hi * 1.3],
"tickcolor": "#6b7599", "tickfont": {"size": 9}},
"bar": {"color": "#4f8ef7"},
"bgcolor": "#111520",
"bordercolor": "#1e2540",
"steps": [
{"range": [fv_lo * 0.7, fv_lo], "color": "rgba(239,68,68,0.2)"},
{"range": [fv_lo, fv_hi], "color": "rgba(34,197,94,0.15)"},
{"range": [fv_hi, fv_hi * 1.3], "color": "rgba(239,68,68,0.2)"},
],
"threshold": {"line": {"color": "#4f8ef7", "width": 2}, "value": fair_val
},
number={"prefix": f"{currency} ", "font": {"family": "DM Mono", "size": 26}}
))
fig_fv.update_layout(**PLOTLY_LAYOUT, height=280)
st.plotly_chart(fig_fv, use_container_width=True)
else:
st.info("Nicht genug Daten für eine Fair Value Schätzung.")
with dcf_col:
section("DCF Sensitivitäts-Analyse")
st.markdown('<div style="font-size:0.8rem;color:var(--muted);margin-bottom:1rem">Pass
fcf = info.get("freeCashflow")
shares_out = info.get("sharesOutstanding")
if fcf and shares_out:
g_min = st.slider("Wachstumsrate Min (%)", 0, 20, 5)
g_max = st.slider("Wachstumsrate Max (%)", 5, 40, 20)
disc = st.slider("Diskontierungsrate (%)", 6, 15, 10)
term_pe = st.slider("Terminal PE", 10, 30, 15)
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
x=[f"{g*100:.0f}%" for g in growth_rates],
y=dcf_vals,
marker_color=bar_colors,
text=[f"{currency} {v:,.0f}" for v in dcf_vals],
textposition="outside",
textfont=dict(family="DM Mono", size=10)
))
fig_dcf.add_hline(y=price, line_color="#4f8ef7", line_dash="dash",
annotation_text=f"Kurs: {currency}{price:,.2f}",
annotation_position="right", line_width=1.5)
fig_dcf.update_layout(**PLOTLY_LAYOUT, height=320,
xaxis_title="Wachstumsrate",
yaxis_tickprefix=f"{currency} ", showlegend=False)
st.plotly_chart(fig_dcf, use_container_width=True)
else:
st.info("Free Cash Flow und Aktienanzahl werden für DCF benötigt.")
# ================================================================
# TAB 4 — NEWS
# ================================================================
with tabs[3]:
news = load_news(ticker, company)
section("Aktuelle Nachrichten")
if news:
for art in news:
title = art.get("title", "")
url = art.get("url", "#")
src = art.get("source", {}).get("name", "") if isinstance(art.get("source"), dict
pub = art.get("publishedAt", "")[:10] if art.get("publishedAt") else ""
title_l = title.lower()
neg_words = ["fall", "drop", "crash", "loss", "decline", "down", "cut", "miss", "
pos_words = ["rise", "gain", "beat", "growth", "profit", "surge", "record", "buy"
if any(w in title_l for w in pos_words):
sent_label, sent_cls = "Positiv", "news-sentiment-pos"
elif any(w in title_l for w in neg_words):
sent_label, sent_cls = "Negativ", "news-sentiment-neg"
else:
sent_label, sent_cls = "Neutral", "news-sentiment-neu"
st.markdown(f"""
<div class="news-item">
<div class="news-headline"><a href="{url}" target="_blank" style="color:var(--t
<div class="news-meta">
{src} &nbsp;·&nbsp; {pub} &nbsp;·&nbsp;
<span class="{sent_cls}">{sent_label}</span>
</div>
</div>""", unsafe_allow_html=True)
else:
st.info("Keine Nachrichten gefunden.")
# ================================================================
# TAB 5 — ANALYST ESTIMATES
# ================================================================
with tabs[4]:
section("Analyst-Konsensus & Schätzungen")
est_col1, est_col2, est_col3 = st.columns(3)
target = info.get("targetMeanPrice")
target_lo = info.get("targetLowPrice")
target_hi = info.get("targetHighPrice")
rec = info.get("recommendationKey", "").upper().replace("_", " ")
num_analysts = info.get("numberOfAnalystOpinions", "N/A")
with est_col1:
t_upside = safe_pct(target, price) if target else None
card("Analyst Kursziel", f"{currency} {target:,.2f}" if target else "N/A",
f"Upside: {t_upside:+.1f}%" if t_upside else "")
with est_col2:
sig_cls = "signal-buy" if "BUY" in rec or "OVERWEIGHT" in rec else "signal-sell" if "
st.markdown(f"""<div class="eq-card">
<div class="eq-card-title">Empfehlung</div>
<div style="margin-top:0.4rem"><span class="signal {sig_cls}" style="font-size:0.9r
<div class="eq-card-sub">{num_analysts} Analysten</div>
</div>""", unsafe_allow_html=True)
with est_col3:
card("Kursziel-Range",
f"{currency} {target_lo:,.0f} – {currency} {target_hi:,.0f}" if target_lo and ta
"Niedrig – Hoch")
if target and target_lo and target_hi:
fig_est = go.Figure()
fig_est.add_trace(go.Scatter(
x=[target_lo, target, target_hi],
y=["Kursziel", "Kursziel", "Kursziel"],
mode="markers+lines",
marker=dict(size=[10, 16, 10], color=["#6b7599", "#4f8ef7", "#6b7599"]),
line=dict(color="#252d4a", width=2),
name="Analyst Range"
))
fig_est.add_vline(x=price, line_color="#22c55e", line_dash="dash",
annotation_text=f"Kurs {currency}{price:,.2f}",
annotation_position="top right")
fig_est.update_layout(**PLOTLY_LAYOUT, height=150, showlegend=False,
xaxis_tickprefix=f"{currency} ", yaxis_visible=False)
st.plotly_chart(fig_est, use_container_width=True)
if fmp_estimates:
section("Umsatz & EPS Prognosen")
est_rows = []
for e in fmp_estimates:
est_rows.append({
"Jahr": str(e.get("date", ""))[:4],
"Umsatz (Est.)": fmt(e.get("estimatedRevenueAvg")),
"EPS (Est.)": safe(e.get("estimatedEpsAvg")),
"EPS High": safe(e.get("estimatedEpsHigh")),
"EPS Low": safe(e.get("estimatedEpsLow")),
})
if est_rows:
st.dataframe(pd.DataFrame(est_rows), use_container_width=True, hide_index=True)
section("Weitere Signale")
s1, s2, s3 = st.columns(3)
with s1:
card("Short Float", safe(info.get("shortPercentOfFloat"), suffix="%"), "Leerverkaufsq
with s2:
card("Insider Halten", safe(info.get("heldPercentInsiders"), suffix="%"), "Insiderant
with s3:
card("Inst. Halten", safe(info.get("heldPercentInstitutions"), suffix="%"), "Institut
# ================================================================
# TAB 6 — DILUTION / SHARE COUNT HISTORY
# ================================================================
with tabs[5]:
section("Aktienanzahl & Verwässerungsanalyse")
shares_now = info.get("sharesOutstanding")
float_shares = info.get("floatShares")
d1, d2, d3, d4 = st.columns(4)
with d1:
card("Aktien ausstehend", fmt(shares_now), "Aktuell")
with d2:
card("Float", fmt(float_shares), "Handelbar")
with d3:
sbc = None
if "sbc" in shares_history and len(shares_history["sbc"]) > 0:
sbc = float(shares_history["sbc"].iloc[0])
card("SBC (letztes Jahr)", fmt(sbc) if sbc else "N/A", "Stock-Based Compensation")
with d4:
bb = None
if "buybacks" in shares_history and len(shares_history["buybacks"]) > 0:
bb_val = float(shares_history["buybacks"].iloc[0])
bb = abs(bb_val)
card("Rückkäufe (letztes Jahr)", fmt(bb) if bb else "N/A", "Share Repurchases")
st.markdown("<br>", unsafe_allow_html=True)
annual_shares = shares_history.get("annual")
quarterly_shares = shares_history.get("quarterly")
has_share_data = (annual_shares is not None and len(annual_shares) > 1) or \
(quarterly_shares is not None and len(quarterly_shares) > 1)
if has_share_data:
fig_shares = go.Figure()
if annual_shares is not None and len(annual_shares) > 1:
sorted_ann = annual_shares.sort_index()
fig_shares.add_trace(go.Bar(
x=sorted_ann.index.astype(str),
y=sorted_ann.values / 1e9,
name="Aktien ausst. (Mrd.)",
marker_color="#4f8ef7",
opacity=0.75,
))
if quarterly_shares is not None and len(quarterly_shares) > 1:
sorted_q = quarterly_shares.sort_index()
fig_shares.add_trace(go.Scatter(
x=sorted_q.index.astype(str),
y=sorted_q.values / 1e9,
name="Quarterly",
line=dict(color="#7c5cfc", width=2),
mode="lines+markers",
marker=dict(size=5)
))
fig_shares.update_layout(
**PLOTLY_LAYOUT,
height=300,
yaxis_title="Mrd. Aktien",
title_text="Historische Aktienanzahl",
)
st.plotly_chart(fig_shares, use_container_width=True)
else:
st.info("Historische Aktienzahlen nicht verfügbar (yfinance-Limitation).")
sbc_data = shares_history.get("sbc")
bb_data = shares_history.get("buybacks")
if (sbc_data is not None and len(sbc_data) > 0) or (bb_data is not None and len(bb_data)
section("SBC vs. Aktienrückkäufe")
fig_sbc = go.Figure()
if sbc_data is not None and len(sbc_data) > 0:
sorted_sbc = sbc_data.sort_index()
fig_sbc.add_trace(go.Bar(
x=sorted_sbc.index.astype(str),
y=sorted_sbc.values / 1e9,
name="SBC (Vergütung)",
marker_color="#ef4444",
opacity=0.8,
))
if bb_data is not None and len(bb_data) > 0:
sorted_bb = bb_data.sort_index()
fig_sbc.add_trace(go.Bar(
x=sorted_bb.index.astype(str),
y=[-abs(v) / 1e9 for v in sorted_bb.values],
name="Rückkäufe",
marker_color="#22c55e",
opacity=0.8,
))
fig_sbc.add_hline(y=0, line_color="#6b7599", line_width=1)
fig_sbc.update_layout(
**PLOTLY_LAYOUT,
height=300,
barmode="overlay",
yaxis_title="Mrd. USD",
title_text="SBC (rot) vs. Rückkäufe (grün, negativ = Kapitalrückführung)",
)
st.plotly_chart(fig_sbc, use_container_width=True)
section("Verwässerungskontext")
dil_l, dil_r = st.columns(2)
with dil_l:
st.markdown("""
<div class="dilution-highlight">
<div class="eq-card-title">Was bedeutet Verwässerung?</div>
<div style="font-size:0.85rem;color:var(--muted);line-height:1.7">
Wenn ein Unternehmen neue Aktien ausgibt – z. B. durch SBC (Mitarbeitervergütung)
Kapitalerhöhungen – sinkt der Anteil bestehender Aktionäre. Netto-Rückkäufe &gt;
<span style="color:var(--green)">✓ Buybacks &gt; SBC → Netto-Reduktion</span><br>
<span style="color:var(--red)">✗ SBC &gt; Buybacks → Netto-Verwässerung</span>
</div>
</div>
""", unsafe_allow_html=True)
with dil_r:
net_effect = None
sbc_last = None
bb_last = None
if sbc_data is not None and len(sbc_data) > 0:
sbc_last = float(sbc_data.iloc[0])
if bb_data is not None and len(bb_data) > 0:
bb_last = abs(float(bb_data.iloc[0]))
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
<span class="eq-metric-label">SBC (Vergütung)</span>
<span class="eq-metric-value" style="color:var(--red)">{fmt(sbc_last)}</span>
</div>
<div class="eq-metric">
<span class="eq-metric-label">Rückkäufe</span>
<span class="eq-metric-value" style="color:var(--green)">{fmt(bb_last)}</span
</div>
</div>
""", unsafe_allow_html=True)
else:
st.info("Nicht genug Daten für Netto-Effekt Berechnung.")
# ================================================================
# TAB 7 — QUALITY SCORE
# ================================================================
with tabs[6]:
section("Unternehmensqualität")
score_l, score_r = st.columns([1, 2])
with score_l:
score_rounded = round(overall_score * 2) / 2
score_stars = stars_html(score_rounded)
score_pct = (overall_score / 5) * 100
if overall_score >= 4.0:
score_verdict = "Ausgezeichnet"
score_color = "var(--green)"
score_desc = "Starkes Unternehmen mit solider Qualität in den meisten Kategorien.
elif overall_score >= 3.0:
score_verdict = "Gut"
score_color = "#4f8ef7"
score_desc = "Solides Unternehmen mit einigen Stärken und moderaten Schwächen."
elif overall_score >= 2.0:
score_verdict = "Durchschnittlich"
score_color = "var(--amber)"
score_desc = "Gemischtes Bild – einzelne starke Kategorien, aber auch Schwachstel
else:
score_verdict = "Schwach"
score_color = "var(--red)"
score_desc = "Erhebliche Schwächen in mehreren Kategorien."
st.markdown(f"""
<div class="eq-card" style="text-align:center;padding:2rem 1.4rem">
<div class="eq-card-title" style="text-align:center">Gesamtqualität</div>
<div style="font-family:'DM Serif Display',serif;font-size:4.5rem;line-height:1;col
{overall_score:.1f}
</div>
<div style="font-size:0.7rem;color:var(--muted);letter-spacing:0.1em;text-transform
<div style="font-size:1.8rem;letter-spacing:0.08em;margin-bottom:0.6rem">{score_sta
<div style="font-size:1rem;font-weight:600;color:{score_color};margin-bottom:0.5rem
<div style="font-size:0.78rem;color:var(--muted);line-height:1.5">{score_desc}</div
<div class="gauge-wrap" style="margin-top:1rem">
<div class="gauge-track" style="height:6px">
<div class="gauge-fill" style="width:{score_pct:.0f}%;background:{score_color}"
</div>
</div>
</div>
""", unsafe_allow_html=True)
with score_r:
section("Kategorie-Breakdown")
cat_colors = {
"Bewertung": "#f59e0b",
"Profitabilität": "#22c55e",
"Wachstum": "#4f8ef7",
"Bilanzqualität": "#7c5cfc",
"Technicals": "#ef4444"
}
cat_weights = {
"Bewertung": "25%",
"Profitabilität": "25%",
"Wachstum": "20%",
"Bilanzqualität": "20%",
"Technicals": "10%"
}
for cat, score in cat_scores.items():
cat_pct = (score / 5) * 100
c_color = cat_colors.get(cat, "#4f8ef7")
c_stars = stars_html(round(score))
detail = cat_details.get(cat, "")
weight = cat_weights.get(cat, "")
st.markdown(f"""
<div class="score-category">
<div style="display:flex;justify-content:space-between;align-items:center;margi
<div>
<span class="score-cat-title">{cat}</span>
<span style="font-size:0.65rem;color:var(--muted2);margin-left:0.5rem">({we
</div>
<div style="display:flex;align-items:center;gap:0.8rem">
<span style="font-family:'DM Mono',monospace;font-size:0.9rem;color:{c_colo
<span style="font-size:1rem;color:{c_color};letter-spacing:0.05em">{c_stars
</div>
</div>
<div style="font-size:0.75rem;color:var(--muted);margin-bottom:0.4rem">{detail}
<div class="score-bar-track">
<div class="score-bar-fill" style="width:{cat_pct:.0f}%;background:{c_color}"
</div>
</div>
""", unsafe_allow_html=True)
section("Qualitäts-Radar")
cats = list(cat_scores.keys())
vals = [cat_scores[c] for c in cats]
vals_closed = vals + [vals[0]]
cats_closed = cats + [cats[0]]
fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
r=vals_closed,
theta=cats_closed,
fill="toself",
fillcolor="rgba(79,142,247,0.15)",
line=dict(color="#4f8ef7", width=2),
name=ticker
))
fig_radar.update_layout(
**PLOTLY_LAYOUT,
polar=dict(
bgcolor="rgba(0,0,0,0)",
radialaxis=dict(
visible=True,
range=[0, 5],
tickfont=dict(size=9, color="#6b7599"),
gridcolor="#1e2540",
linecolor="#1e2540",
),
angularaxis=dict(
tickfont=dict(size=11, color="#e8ecf4"),
gridcolor="#1e2540",
linecolor="#1e2540",
)
),
height=400,
showlegend=False
)
st.plotly_chart(fig_radar, use_container_width=True)
st.markdown("""
<div style="font-size:0.72rem;color:var(--muted2);margin-top:1rem;padding:0.8rem 1rem;bac
<strong>Hinweis:</strong> Der Qualitätsscore basiert auf automatisch berechneten Kennza
und stellt <em>keine Anlageberatung</em> dar. Er dient als Orientierungshilfe für eine
Gewichtung: Bewertung 25% · Profitabilität 25% · Wachstum 20% · Bilanz 20% · Technicals
</div>
""", unsafe_allow_html=True)
# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
'<div style="text-align:center;font-size:0.7rem;color:var(--muted2);font-family:DM Mono,m
'Equitas · Keine Anlageberatung · Daten: Yahoo Finance, FMP · '
+ datetime.now().strftime("%d.%m.%Y %H:%M") +
'</div>', unsafe_allow_html=True
)
