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
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');
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
.stApp {
    background: var(--bg) !important;
}
/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1600px; }
/* ---- HEADER ---- */
.eq-header {
    display: flex;
    align-items: flex-end;
    gap: 1.5rem;
    margin-bottom: 0.25rem;
}
.eq-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-transform: uppercase;
}
.eq-company {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    line-height: 1.1;
    color: var(--text);
    margin: 0;
}
.eq-ticker-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.6rem;
    border: 1px solid var(--accent);
    border-radius: 4px;
    color: var(--accent);
    vertical-align: middle;
    margin-left: 0.5rem;
    position: relative;
    top: -0.3rem;
}
.eq-price-block {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin: 0.5rem 0 1.5rem;
}
.eq-price {
    font-family: 'DM Mono', monospace;
    font-size: 3rem;
    font-weight: 500;
    color: var(--text);
    letter-spacing: -0.02em;
}
.eq-change-pos { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--green); }
.eq-change-neg { font-family: 'DM Mono', monospace; font-size: 1.1rem; color: var(--red); }
.eq-sector { font-size: 0.85rem; color: var(--muted); }
/* ---- CARDS ---- */
.eq-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    height: 100%;
}
.eq-card-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.eq-card-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1;
}
.eq-card-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 0.35rem;
}
/* ---- METRIC ROW ---- */
.eq-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.875rem;
}
.eq-metric:last-child { border-bottom: none; }
.eq-metric-label { color: var(--muted); }
.eq-metric-value { font-family: 'DM Mono', monospace; color: var(--text); font-size: 0.85rem; }
/* ---- GAUGE BAR ---- */
.gauge-wrap { margin: 0.3rem 0 0.1rem; }
.gauge-track {
    height: 4px;
    background: var(--border2);
    border-radius: 2px;
    overflow: hidden;
}
.gauge-fill {
    height: 100%;
    border-radius: 2px;
}
/* ---- SECTION LABELS ---- */
.eq-section {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--text);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}
/* ---- NEWS ---- */
.news-item {
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--border);
}
.news-item:last-child { border-bottom: none; }
.news-headline { font-size: 0.9rem; color: var(--text); line-height: 1.4; margin-bottom: 0.25rem; }
.news-meta { font-size: 0.75rem; color: var(--muted); font-family: 'DM Mono', monospace; }
.news-sentiment-pos { color: var(--green); font-weight: 600; }
.news-sentiment-neg { color: var(--red); font-weight: 600; }
.news-sentiment-neu { color: var(--muted); font-weight: 600; }
/* ---- FAIR VALUE ---- */
.fv-positive { color: var(--green); }
.fv-negative { color: var(--red); }
.fv-label {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.2rem;
}
.fv-value {
    font-family: 'DM Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
}
.fv-range {
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: var(--muted);
}
/* ---- TABS ---- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.04em;
    color: var(--muted) !important;
    padding: 0.45rem 1.1rem;
    border-radius: 7px;
    background: transparent !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem;
}
/* ---- INPUTS ---- */
.stTextInput > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
}
.stTextInput label { color: var(--muted) !important; font-size: 0.75rem !important; }
/* ---- SELECTBOX ---- */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
}
/* ---- SIDEBAR ---- */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1rem 1.2rem; }
/* ---- DIVIDER ---- */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }
/* ---- SCROLLBAR ---- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
/* ---- PLOTLY OVERRIDE ---- */
.js-plotly-plot .plotly { background: transparent !important; }
/* ---- SIGNAL BADGE ---- */
.signal {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
}
.signal-buy { background: rgba(34,197,94,0.15); color: var(--green); border: 1px solid rgba(34,197,94,0.3); }
.signal-sell { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }
.signal-hold { background: rgba(245,158,11,0.15); color: var(--amber); border: 1px solid rgba(245,158,11,0.3); }
/* ---- SCORE RING ---- */
.score-ring-wrap { text-align: center; }
.score-number {
    font-family: 'DM Serif Display', serif;
    font-size: 3.5rem;
    line-height: 1;
}
.score-label { font-size: 0.75rem; color: var(--muted); letter-spacing: 0.1em; text-transform: uppercase; }
/* ---- WATCHLIST ---- */
.wl-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    background: var(--surface2);
    border: 1px solid var(--border);
    cursor: pointer;
    font-size: 0.85rem;
}
.wl-ticker { font-family: 'DM Mono', monospace; font-weight: 500; color: var(--accent); }
.wl-change-pos { font-family: 'DM Mono', monospace; color: var(--green); font-size: 0.8rem; }
.wl-change-neg { font-family: 'DM Mono', monospace; color: var(--red); font-size: 0.8rem; }
/* ---- STMETRIC OVERRIDE ---- */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 1.5rem !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INITIALISIERUNG (WICHTIG!) ====================
if "ticker" not in st.session_state:
    st.session_state.ticker = "AAPL"
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]

# ==================== API KEYS ====================
FMP_API_KEY = nDMiO8SB2a3sBH6mqxr0jhk75qpnZiYJ
NEWS_API_KEY = os.getenv 2882d428504e477aafcd883273084a73

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

@st.cache_data(ttl=86400)
def load_fmp_metrics(ticker: str):
    if not FMP_API_KEY:
        return {}, {}, []
    try:
        url = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}"
        r = requests.get(url, timeout=10)
        metrics = r.json()[0] if r.status_code == 200 and isinstance(r.json(), list) else {}
    except:
        metrics = {}
    try:
        url2 = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{ticker}?apikey={FMP_API_KEY}"
        r2 = requests.get(url2, timeout=10)
        ratios = r2.json()[0] if r2.status_code == 200 and isinstance(r2.json(), list) else {}
    except:
        ratios = {}
    try:
        url3 = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}?limit=4&apikey={FMP_API_KEY}"
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
            url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=8&apiKey={NEWS_API_KEY}"
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
                    "publishedAt": datetime.fromtimestamp(n.get("providerPublishTime", 0)).isoformat(),
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
    hoverlabel=dict(bgcolor="#111520", bordercolor="#252d4a", font_family="DM Mono, monospace"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
)

# ==================== SIDEBAR (KORRIGIERT) ====================
with st.sidebar:
    st.markdown('<div class="eq-logo">⬡ Equitas</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Ticker Input – jetzt mit Label + Key (kein KeyError mehr!)
    ticker_input = st.text_input(
        "Ticker Symbol",
        value=st.session_state.ticker,
        placeholder="z. B. AAPL",
        label_visibility="collapsed",
        key="ticker_input"
    )
    ticker = ticker_input.upper().strip()
    
    # Ticker in Session State speichern
    if ticker and ticker != st.session_state.ticker:
        st.session_state.ticker = ticker
    
    period_map = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1J": "1y", "2J": "2y", "5J": "5y"}
    period_label = st.radio("Zeitraum", list(period_map.keys()), horizontal=True, index=3)
    chart_period = period_map[period_label]
    
    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin-bottom:0.5rem">Watchlist</div>', unsafe_allow_html=True)
    
    wl_cols = st.columns([4, 1])
    new_wl = wl_cols[0].text_input(
        "Neues Symbol hinzufügen",
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
    st.markdown(f'<div style="font-size:0.7rem;color:var(--muted2)">API Status<br>'
                f'FMP: {"🟢" if FMP_API_KEY else "🔴"} &nbsp; News: {"🟢" if NEWS_API_KEY else "🔴"}</div>',
                unsafe_allow_html=True)

if not ticker:
    st.stop()

# ==================== LOAD DATA ====================
with st.spinner(""):
    info, hist, fins, balance, cashflow, dividends = load_yfinance(ticker)
    fmp_metrics, fmp_ratios, fmp_estimates = load_fmp_metrics(ticker)

if hist is None or hist.empty:
    st.error("❌ Keine Kursdaten gefunden. Bitte prüfe den Ticker.")
    st.stop()

# ==================== DERIVED ====================
price = float(hist["Close"].iloc[-1])
prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
change = price - prev
chg_pct = safe_pct(price, prev)
high52 = float(hist["High"].rolling(252).max().iloc[-1]) if len(hist) > 252 else float(hist["High"].max())
low52 = float(hist["Low"].rolling(252).min().iloc[-1]) if len(hist) > 252 else float(hist["Low"].min())
fair_val, fv_lo, fv_hi = compute_fair_value(info, hist)
df_tech = compute_technicals(hist)
company = info.get("longName", ticker)
sector = info.get("sector", "")
industry = info.get("industry", "")
currency = info.get("currency", "USD")
rsi_now = float(df_tech["RSI"].iloc[-1]) if not df_tech["RSI"].isna().all() else None

# ==================== HEADER ====================
arrow = "▲" if change >= 0 else "▼"
chg_color = "var(--green)" if change >= 0 else "var(--red)"
st.markdown(f"""
<div class="eq-header">
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

# ==================== KPI STRIP ====================
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
with kpi1:
    card("Market Cap", fmt(info.get("marketCap")), "Gesamtbewertung")
with kpi2:
    card("P/E (TTM)", safe(info.get("trailingPE")), "Kurs / Gewinn")
with kpi3:
    card("EPS (TTM)", safe(info.get("trailingEps"), suffix=" " + currency), "Earnings per Share")
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
tabs = st.tabs(["📈 Chart & Technicals", "📊 Fundamentals", "⚖️ Fair Value & DCF", "📰 News", "🔭 Schätzungen"])

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
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.08)", line_width=0, row=3, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(34,197,94,0.08)", line_width=0, row=3, col=1)
    fig.add_hline(y=70, line_color="#ef4444", line_dash="dot", line_width=1, opacity=0.4, row=3, col=1)
    fig.add_hline(y=30, line_color="#22c55e", line_dash="dot", line_width=1, opacity=0.4, row=3, col=1)
    # KORRIGIERT – verhindert den "multiple values for keyword argument 'legend'" Fehler
    layout = PLOTLY_LAYOUT.copy()
    layout["legend"] = dict(orientation="h", y=1.02, x=0)
    
    fig.update_layout(
        **layout,
        height=640,
        showlegend=True
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(tickprefix=f"{currency} ", row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

    section("Technische Signale")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        rsi_color = "var(--red)" if (rsi_now and rsi_now > 70) else "var(--green)" if (rsi_now and rsi_now < 30) else "var(--amber)"
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
            <div class="eq-card-sub">Signal: {safe(sig_now)} — {'Bullish' if macd_bull else 'Bearish'}</div>
        </div>""", unsafe_allow_html=True)
    with t3:
        ma50 = df_tech["MA50"].iloc[-1]
        ma200 = df_tech["MA200"].iloc[-1]
        above = price > ma50 and price > ma200
        golden = ma50 > ma200
        st.markdown(f"""<div class="eq-card">
            <div class="eq-card-title">Trend (MA)</div>
            <div class="eq-card-value" style="color:{'var(--green)' if above else 'var(--red)'}">{safe(ma50)}</div>
            <div class="eq-card-sub">{'Golden Cross ✓' if golden else 'Death Cross ✗'} · MA50/MA200</div>
        </div>""", unsafe_allow_html=True)
    with t4:
        pos52 = (price - low52) / (high52 - low52) * 100 if (high52 - low52) != 0 else 50
        st.markdown(f"""<div class="eq-card">
            <div class="eq-card-title">52W Position</div>
            <div class="eq-card-value">{pos52:.0f}%</div>
            <div class="eq-card-sub">Tief {currency}{low52:,.2f} · Hoch {currency}{high52:,.2f}</div>
            <div class="gauge-wrap">
                <div class="gauge-track">
                    <div class="gauge-fill" style="width:{pos52:.0f}%;background:{'var(--green)' if pos52>60 else 'var(--amber)' if pos52>30 else 'var(--red)'}"></div>
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
        fig_perf.update_layout(**PLOTLY_LAYOUT, height=280,
                               yaxis_ticksuffix="%", showlegend=False)
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
        metric_row("EV/EBITDA", safe(fmp_metrics.get("enterpriseValueOverEBITDATTM") or info.get("enterpriseToEbitda")))
        metric_row("PEG Ratio", safe(info.get("pegRatio")))
        section("Profitabilität")
        metric_row("Bruttomarge", safe(info.get("grossMargins"), suffix="%") if info.get("grossMargins") else
                   safe(fmp_metrics.get("grossProfitMarginTTM"), suffix="%"))
        metric_row("EBITDA Marge", safe(info.get("ebitdaMargins"), suffix="%"))
        metric_row("Nettomarge", safe(info.get("profitMargins"), suffix="%"))
        metric_row("ROE", safe(info.get("returnOnEquity"), suffix="%"))
        metric_row("ROA", safe(info.get("returnOnAssets"), suffix="%"))
        metric_row("ROIC (TTM)", safe(fmp_metrics.get("returnOnInvestedCapitalTTM"), suffix="%"))
    with col_r:
        section("Wachstum")
        metric_row("Umsatzwachstum (YoY)", safe(info.get("revenueGrowth"), suffix="%"))
        metric_row("Gewinnwachstum (YoY)", safe(info.get("earningsGrowth"), suffix="%"))
        metric_row("EPS Wachstum (5J)", safe(info.get("earningsQuarterlyGrowth"), suffix="%"))
        section("Finanzkraft")
        metric_row("Total Debt", fmt(info.get("totalDebt")))
        metric_row("Cash & Equivalents", fmt(info.get("totalCash")))
        metric_row("Debt/Equity", safe(info.get("debtToEquity")))
        metric_row("Current Ratio", safe(info.get("currentRatio")))
        metric_row("Quick Ratio", safe(info.get("quickRatio")))
        metric_row("Free Cash Flow", fmt(info.get("freeCashflow")))
        section("Dividende")
        metric_row("Dividendenrendite", safe(info.get("dividendYield"), suffix="%"))
        metric_row("Dividende (annual)", safe(info.get("dividendRate"), suffix=f" {currency}"))
        metric_row("Payout Ratio", safe(info.get("payoutRatio"), suffix="%"))
        metric_row("5J Div. Wachstum", safe(info.get("fiveYearAvgDividendYield"), suffix="%"))

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
            label = "Unterbewertet" if upside > 10 else "Überbewertet" if upside < -10 else "Fair bewertet"
            st.markdown(f"""
            <div class="eq-card">
                <div class="fv-label">Intrinsic Value Estimate</div>
                <div class="fv-value" style="color:{fv_color}">{currency} {fair_val:,.2f}</div>
                <div class="fv-range">Range: {currency} {fv_lo:,.2f} — {currency} {fv_hi:,.2f}</div>
                <br>
                <div style="display:flex;gap:1rem;align-items:center">
                    <div>
                        <div class="fv-label">Kurspreis</div>
                        <div style="font-family:'DM Mono',monospace;font-size:1.2rem">{currency} {price:,.2f}</div>
                    </div>
                    <div>
                        <div class="fv-label">Upside/Downside</div>
                        <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{fv_color}">{upside:+.1f}%</div>
                    </div>
                    <div>
                        <div class="fv-label">Einschätzung</div>
                        <div style="font-size:0.85rem;margin-top:0.2rem">
                            <span class="signal {'signal-buy' if upside>10 else 'signal-sell' if upside<-10 else 'signal-hold'}">{label}</span>
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
                       "increasing": {"color": "#22c55e"}, "decreasing": {"color": "#ef4444"}},
                title={"text": f"Kurs vs. Fair Value ({currency})", "font": {"size": 13, "color": "#6b7599"}},
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
                    "threshold": {"line": {"color": "#4f8ef7", "width": 2}, "value": fair_val}
                },
                number={"prefix": f"{currency} ", "font": {"family": "DM Mono", "size": 26}}
            ))
            fig_fv.update_layout(**PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig_fv, use_container_width=True)
        else:
            st.info("Nicht genug Daten für eine Fair Value Schätzung.")

    with dcf_col:
        section("DCF Sensitivitäts-Analyse")
        st.markdown('<div style="font-size:0.8rem;color:var(--muted);margin-bottom:1rem">Passe Wachstums- und Diskontierungsannahmen an, um den inneren Wert zu simulieren.</div>', unsafe_allow_html=True)
        fcf = info.get("freeCashflow")
        shares = info.get("sharesOutstanding")
        if fcf and shares:
            g_min = st.slider("Wachstumsrate Min (%)", 0, 20, 5)
            g_max = st.slider("Wachstumsrate Max (%)", 5, 40, 20)
            disc = st.slider("Diskontierungsrate (%)", 6, 15, 10)
            term_pe = st.slider("Terminal PE", 10, 30, 15)
            growth_rates = np.linspace(g_min/100, g_max/100, 6)
            dcf_vals = []
            for g in growth_rates:
                fcf_ps = float(fcf) / float(shares)
                pv = sum(fcf_ps * (1+g)**yr / (1+disc/100)**yr for yr in range(1,11))
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
            src = art.get("source", {}).get("name", "") if isinstance(art.get("source"), dict) else ""
            pub = art.get("publishedAt", "")[:10] if art.get("publishedAt") else ""
            title_l = title.lower()
            neg_words = ["fall", "drop", "crash", "loss", "decline", "down", "cut", "miss", "risk", "fail", "warn"]
            pos_words = ["rise", "gain", "beat", "growth", "profit", "surge", "record", "buy", "upgrade", "strong"]
            if any(w in title_l for w in pos_words):
                sent_label, sent_cls = "Positiv", "news-sentiment-pos"
            elif any(w in title_l for w in neg_words):
                sent_label, sent_cls = "Negativ", "news-sentiment-neg"
            else:
                sent_label, sent_cls = "Neutral", "news-sentiment-neu"
            st.markdown(f"""
            <div class="news-item">
                <div class="news-headline"><a href="{url}" target="_blank" style="color:var(--text);text-decoration:none">{title}</a></div>
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
        sig_cls = "signal-buy" if "BUY" in rec or "OVERWEIGHT" in rec else "signal-sell" if "SELL" in rec or "UNDER" in rec else "signal-hold"
        st.markdown(f"""<div class="eq-card">
            <div class="eq-card-title">Empfehlung</div>
            <div style="margin-top:0.4rem"><span class="signal {sig_cls}" style="font-size:0.95rem">{rec or 'N/A'}</span></div>
            <div class="eq-card-sub">{num_analysts} Analysten</div>
        </div>""", unsafe_allow_html=True)
    with est_col3:
        card("Kursziel-Range",
             f"{currency} {target_lo:,.0f} – {currency} {target_hi:,.0f}" if target_lo and target_hi else "N/A",
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
                "Jahr": str(e.get("date",""))[:4],
                "Umsatz (Est.)": fmt(e.get("estimatedRevenueAvg")),
                "EPS (Est.)": safe(e.get("estimatedEpsAvg")),
                "EPS High": safe(e.get("estimatedEpsHigh")),
                "EPS Low": safe(e.get("estimatedEpsLow")),
            })
        if est_rows:
            st.dataframe(
                pd.DataFrame(est_rows),
                use_container_width=True,
                hide_index=True
            )

    section("Weitere Signale")
    s1, s2, s3 = st.columns(3)
    with s1:
        card("Short Float", safe(info.get("shortPercentOfFloat"), suffix="%"), "Leerverkaufsquote")
    with s2:
        card("Insider Halten", safe(info.get("heldPercentInsiders"), suffix="%"), "Insideranteil")
    with s3:
        card("Inst. Halten", safe(info.get("heldPercentInstitutions"), suffix="%"), "Institutionell")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    '<div style="text-align:center;font-size:0.7rem;color:var(--muted2);font-family:DM Mono,monospace">'
    'Equitas · Keine Anlageberatung · Daten: Yahoo Finance, FMP · '
    + datetime.now().strftime("%d.%m.%Y %H:%M") +
    '</div>', unsafe_allow_html=True
)
