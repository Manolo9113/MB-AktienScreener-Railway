import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import requests

# ==================== CONFIG ====================
st.set_page_config(
    page_title="Aktien-Tool Bäumer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: #080d18;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0d1526 !important;
        border-right: 1px solid #1e2d45;
    }

    /* Header */
    .header-wrap {
        background: linear-gradient(135deg, #0d1f3c 0%, #0a1628 100%);
        border: 1px solid #1e3a5f;
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 32px rgba(0,120,255,0.15);
    }
    .header-title { color: #fff; font-size: 2rem; font-weight: 700; margin: 0; }
    .header-sub { color: #64b5f6; font-size: 1rem; margin-top: 4px; }
    .header-price { font-size: 2.4rem; font-weight: 700; color: #00e5ff; text-align: right; }
    .header-change-pos { color: #00e676; font-size: 1rem; }
    .header-change-neg { color: #ff1744; font-size: 1rem; }

    /* Score Ring */
    .score-section {
        background: linear-gradient(135deg, #0d1f3c, #0a1628);
        border: 1px solid #1e3a5f;
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,120,255,0.1);
        margin-bottom: 20px;
    }
    .score-title { color: #64b5f6; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; }
    .score-num { font-size: 3.5rem; font-weight: 800; }
    .score-label { color: #90a4ae; font-size: 0.9rem; margin-top: 6px; }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #0d1f3c, #0a1628);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .metric-card:hover { border-color: #1565c0; }
    .metric-label { color: #78909c; font-size: 0.78rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .metric-value { color: #eceff1; font-size: 1.5rem; font-weight: 700; }
    .metric-sub { color: #546e7a; font-size: 0.75rem; margin-top: 4px; }
    .metric-badge-green { background: rgba(0,230,118,0.15); color: #00e676; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600; }
    .metric-badge-yellow { background: rgba(255,214,0,0.15); color: #ffd600; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600; }
    .metric-badge-red { background: rgba(255,23,68,0.15); color: #ff1744; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600; }
    .metric-badge-gray { background: rgba(120,144,156,0.15); color: #78909c; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; font-weight: 600; }

    /* Section headers */
    .section-header {
        color: #64b5f6;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 24px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e3a5f;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #0d1526;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid #1e2d45;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #78909c;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.85rem;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #1565c0 !important;
        color: #fff !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #0d1526;
        border-radius: 10px;
        color: #64b5f6;
    }

    /* Input */
    .stTextInput input {
        background: #0d1526;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        color: #eceff1;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        padding: 12px;
    }
    .stTextInput input:focus {
        border-color: #1565c0;
        box-shadow: 0 0 0 2px rgba(21,101,192,0.3);
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] { padding: 0; }

    /* Divider */
    hr { border-color: #1e3a5f; }

    /* Caption */
    .caption-text { color: #37474f; font-size: 0.72rem; text-align: center; margin-top: 30px; }

    /* Insight box */
    .insight-box {
        background: linear-gradient(135deg, #0d2137, #0a1a2e);
        border-left: 3px solid #1565c0;
        border-radius: 0 12px 12px 0;
        padding: 14px 18px;
        margin: 8px 0;
        color: #b0bec5;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .insight-box strong { color: #64b5f6; }

    /* Insider table */
    .insider-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #1e2d45;
        font-size: 0.85rem;
    }
    .insider-buy { color: #00e676; font-weight: 600; }
    .insider-sell { color: #ff5252; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==================== API KEY ====================
import os

FMP_API_KEY = os.getenv("FMP_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

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

@st.cache_data(ttl=3600)
def load_yfinance_extended(ticker: str):
    """Lädt zusätzliche Daten: Wöchentliche + monatliche Kerzen, Share count history, Splits"""
    stock = yf.Ticker(ticker)
    hist_weekly, hist_monthly = pd.DataFrame(), pd.DataFrame()
    share_history = pd.DataFrame()
    splits_data = pd.Series(dtype=float)
    try:
        hist_weekly = stock.history(period="2y", interval="1wk")
    except:
        pass
    try:
        hist_monthly = stock.history(period="5y", interval="1mo")
    except:
        pass
    try:
        share_history = stock.get_shares_full(start="2019-01-01")
    except:
        try:
            share_history = stock.shares
        except:
            pass
    try:
        splits_data = stock.splits
    except:
        pass
    return hist_weekly, hist_monthly, share_history, splits_data

@st.cache_data(ttl=86400)
def load_fmp_metrics(ticker: str):
    if not FMP_API_KEY:
        return {}, [], []
    metrics, peers, analyst = {}, [], []
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{ticker}?apikey={FMP_API_KEY}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            metrics = d[0] if isinstance(d, list) and d else {}
    except:
        pass
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/stock_peers?symbol={ticker}&apikey={FMP_API_KEY}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            peers = d[0].get("peersList", [])[:5] if isinstance(d, list) and d else []
    except:
        pass
    try:
        r = requests.get(f"https://financialmodelingprep.com/api/v3/price-target-consensus/{ticker}?apikey={FMP_API_KEY}", timeout=10)
        if r.status_code == 200:
            analyst = r.json()
    except:
        pass
    return metrics, peers, analyst

# ==================== HELPERS ====================
def badge(v, good, ok, fmt=".1f", inverse=False):
    if v is None:
        return '<span class="metric-badge-gray">N/A</span>'
    if inverse:
        cls = "green" if v <= good else "yellow" if v <= ok else "red"
    else:
        cls = "green" if v >= good else "yellow" if v >= ok else "red"
    return f'<span class="metric-badge-{cls}">{v:{fmt}}</span>'

def safe_float(v, digits=2):
    return f"{v:.{digits}f}" if v is not None else "N/A"

def fmt_large(value):
    if value is None:
        return "N/A"
    if value >= 1e12:
        return f"{value/1e12:.2f}T$"
    elif value >= 1e9:
        return f"{value/1e9:.1f}B$"
    elif value >= 1e6:
        return f"{value/1e6:.1f}M$"
    return f"{value:,.0f}"

def score_color(s):
    if s >= 75:
        return "#00e676"
    elif s >= 50:
        return "#ffd600"
    elif s >= 25:
        return "#ff9100"
    return "#ff1744"

def score_label(s):
    if s >= 75:
        return "Sehr stark 🚀"
    elif s >= 50:
        return "Solide 👍"
    elif s >= 25:
        return "Schwach ⚠️"
    return "Kritisch 🔴"

def is_saas_or_cyber(sector: str, industry: str) -> bool:
    """Rule of 40 gilt nur für Software/SaaS/Cybersecurity — NICHT für Hardware/Consumer Electronics"""
    saas_keywords = [
        "software", "cloud", "saas", "cybersecurity", "security software",
        "internet content", "internet services", "data storage",
        "information technology services",
    ]
    industry_lower = industry.lower()
    for kw in saas_keywords:
        if kw in industry_lower:
            return True
    return False

# ==================== EMA HELPER ====================
def compute_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

# ==================== QUALITY SCORE ====================
def compute_score(rev_growth, fcf_yield, gross_margin, roic_val,
                  profit_margin, rule_of_40, peg_ratio, debt, operating_margin,
                  use_rule_of_40=True):
    score = 0
    max_score = 0

    def add(val, good, ok, weight, inverse=False):
        nonlocal score, max_score
        if val is None:
            return
        max_score += weight
        if inverse:
            score += weight if val <= good else (weight * 0.5 if val <= ok else 0)
        else:
            score += weight if val >= good else (weight * 0.5 if val >= ok else 0)

    if use_rule_of_40:
        add(rule_of_40, 40, 20, 20)
    add(gross_margin, 60, 40, 15)
    add(roic_val, 20, 10, 15)
    add(rev_growth, 15, 5, 12)
    add(fcf_yield, 5, 2, 12)
    add(profit_margin, 15, 5, 10)
    add(operating_margin, 20, 10, 8)
    add(peg_ratio, 1.5, 2.5, 8, inverse=True)

    if max_score == 0:
        return 0
    return round((score / max_score) * 100)

# ==================== DCF ====================
def dcf_valuation(fcf, shares, growth_rate, terminal_growth, discount_rate, years):
    if not fcf or not shares or shares == 0:
        return None
    cashflows = []
    cf = fcf
    for i in range(1, years + 1):
        cf = cf * (1 + growth_rate / 100)           # cf = nominaler FCF in Jahr i
        pv = cf / ((1 + discount_rate / 100) ** i)  # Barwert
        cashflows.append(pv)
    # Terminal Value auf Basis des NOMINALEN CF in Jahr N (nicht des Barwerts!)
    terminal = cf * (1 + terminal_growth / 100) / ((discount_rate - terminal_growth) / 100)
    terminal_pv = terminal / ((1 + discount_rate / 100) ** years)
    total = sum(cashflows) + terminal_pv
    return total / shares

# ==================== SMART SEARCH ====================

def is_isin(q: str) -> bool:
    """ISIN: 2 Buchstaben + 10 Ziffern/Buchstaben, z.B. US0378331005"""
    import re
    return bool(re.match(r'^[A-Z]{2}[A-Z0-9]{10}$', q))


def is_wkn(q: str) -> bool:
    """WKN: genau 6 alphanumerische Zeichen, z.B. 865985"""
    import re
    return bool(re.match(r'^[A-Z0-9]{6}$', q)) and not q.isalpha()

@st.cache_data(ttl=86400)
def resolve_isin_to_ticker(isin: str) -> tuple[str, str]:
    """Löst ISIN via OpenFIGI API in Ticker auf. Gibt (ticker, name) zurück."""
    try:
        resp = requests.post(
            "https://api.openfigi.com/v3/mapping",
            json=[{"idType": "ID_ISIN", "idValue": isin}],
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data and "data" in data[0]:
                results = data[0]["data"]
                # Bevorzuge US-Börsen, dann andere
                for r in results:
                    if r.get("exchCode") in ("US", "UN", "UQ", "UA"):
                        return r.get("ticker", ""), r.get("name", "")
                # Fallback: ersten nehmen
                if results:
                    return results[0].get("ticker", ""), results[0].get("name", "")
    except:
        pass
    return "", ""

@st.cache_data(ttl=86400)
def resolve_wkn_to_ticker(wkn: str) -> tuple[str, str]:
    """Löst WKN via OpenFIGI API in Ticker auf."""
    try:
        resp = requests.post(
            "https://api.openfigi.com/v3/mapping",
            json=[{"idType": "ID_WERTPAPIER", "idValue": wkn}],
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data and "data" in data[0]:
                results = data[0]["data"]
                for r in results:
                    if r.get("exchCode") in ("US", "UN", "UQ", "UA"):
                        return r.get("ticker", ""), r.get("name", "")
                if results:
                    return results[0].get("ticker", ""), results[0].get("name", "")
    except:
        pass
    return "", ""

@st.cache_data(ttl=3600)
def search_by_name(query: str) -> list[dict]:
    """Suche nach Firmenname via yFinance search. Gibt Liste von {ticker, name, exchange} zurück."""
    try:
        results = yf.Search(query, max_results=6)
        quotes = results.quotes if hasattr(results, "quotes") else []
        out = []
        for q in quotes:
            t = q.get("symbol", "")
            n = q.get("longname") or q.get("shortname") or t
            e = q.get("exchange", "")
            qt = q.get("quoteType", "")
            if t and qt in ("EQUITY", "ETF", ""):
                out.append({"ticker": t, "name": n, "exchange": e})
        return out[:6]
    except:
        return []

def resolve_search_input(raw: str) -> tuple[str, str, list]:
    """
    Hauptfunktion: Gibt (ticker, info_msg, suggestions) zurück.
    suggestions = [] wenn eindeutig, sonst Liste von Kandidaten.
    """
    q = raw.strip().upper()
    if not q:
        return "", "", []

    # 1) ISIN erkennen (12 Zeichen, 2 Buchstaben + 10 alphanumerisch)
    if is_isin(q):
        ticker, name = resolve_isin_to_ticker(q)
        if ticker:
            return ticker, f"ISIN {q} → **{ticker}** ({name})", []
        return "", f"❌ ISIN {q} nicht auflösbar.", []

    # 2) WKN erkennen (genau 6 alphanumerisch, nicht rein alphabetisch)
    if is_wkn(q):
        ticker, name = resolve_wkn_to_ticker(q)
        if ticker:
            return ticker, f"WKN {q} → **{ticker}** ({name})", []
        # Fallback: als Ticker versuchen
        pass

    # 3) Direkter Ticker-Versuch (kurz, nur Buchstaben/Punkte)
    if len(q) <= 6 and q.replace(".", "").replace("-", "").isalpha():
        test = yf.Ticker(q)
        try:
            info = test.info
            if info.get("regularMarketPrice") or info.get("currentPrice") or info.get("marketCap"):
                return q, "", []
        except:
            pass

    # 4) Firmenname-Suche
    suggestions = search_by_name(raw.strip())
    if len(suggestions) == 1:
        return suggestions[0]["ticker"], f"Gefunden: **{suggestions[0]['name']}** ({suggestions[0]['ticker']})", []
    elif suggestions:
        return "", "", suggestions

    # 5) Letzter Fallback: Eingabe direkt als Ticker
    return q, "", []


# ==================== SESSION ====================
if "ticker" not in st.session_state:
    st.session_state["ticker"] = "AAPL"
if "search_input" not in st.session_state:
    st.session_state["search_input"] = "AAPL"
if "search_msg" not in st.session_state:
    st.session_state["search_msg"] = ""
if "suggestions" not in st.session_state:
    st.session_state["suggestions"] = []

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <span style='font-size:2rem;'>📈</span>
        <div style='color:#64b5f6; font-size:1.3rem; font-weight:700; margin-top:6px;'>Bäumer</div>
        <div style='color:#37474f; font-size:0.75rem;'>Aktien Analyse Tool</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Smarte Suche
    search_raw = st.text_input(
        "Suche",
        value=st.session_state["search_input"],
        label_visibility="collapsed",
        placeholder="Ticker, Name, ISIN oder WKN…"
    )

    search_btn = st.button("🔍 Suchen", use_container_width=True)

    if search_btn and search_raw.strip():
        with st.spinner("Suche…"):
            resolved, msg, sugg = resolve_search_input(search_raw)
        st.session_state["search_input"] = search_raw
        st.session_state["search_msg"] = msg
        st.session_state["suggestions"] = sugg
        if resolved:
            st.session_state["ticker"] = resolved
            st.session_state["suggestions"] = []
            st.rerun()

    # Auflösungs-Info anzeigen
    if st.session_state["search_msg"]:
        st.markdown(f"<div style='color:#64b5f6; font-size:0.8rem; padding:6px 4px;'>{st.session_state['search_msg']}</div>", unsafe_allow_html=True)

    # Mehrere Treffer → Auswahl anzeigen
    if st.session_state["suggestions"]:
        st.markdown("<div style='color:#ffd600; font-size:0.78rem; padding:4px 0 6px 0;'>Mehrere Treffer — bitte auswählen:</div>", unsafe_allow_html=True)
        for s in st.session_state["suggestions"]:
            label = f"{s['ticker']}  ·  {s['name'][:22]}  [{s['exchange']}]"
            if st.button(label, use_container_width=True, key=f"sugg_{s['ticker']}"):
                st.session_state["ticker"] = s["ticker"]
                st.session_state["search_input"] = s["ticker"]
                st.session_state["suggestions"] = []
                st.session_state["search_msg"] = f"Ausgewählt: **{s['name']}** ({s['ticker']})"
                st.rerun()

    st.markdown("<div class='section-header'>⚡ Schnellauswahl</div>", unsafe_allow_html=True)
    quick = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "SAP"]
    cols = st.columns(2)
    for i, t in enumerate(quick):
        if cols[i % 2].button(t, use_container_width=True, key=f"q_{t}"):
            st.session_state["ticker"] = t
            st.session_state["search_input"] = t
            st.session_state["search_msg"] = ""
            st.session_state["suggestions"] = []
            st.rerun()

    st.markdown("<div class='section-header'>⚙️ Einstellungen</div>", unsafe_allow_html=True)
    show_peers = st.toggle("Peer-Vergleich anzeigen", value=True)
    show_insider = st.toggle("Insider-Transaktionen", value=True)
    show_dcf = st.toggle("DCF Rechner", value=True)

# ==================== MAIN DATA ====================
ticker = st.session_state["ticker"]

with st.spinner(f"Lade Daten für {ticker}..."):
    yf_info, hist, insider_df = load_yfinance(ticker)
    fmp_metrics, peers, analyst_data = load_fmp_metrics(ticker)
    hist_weekly, hist_monthly, share_history, splits_data = load_yfinance_extended(ticker)

if hist.empty:
    st.error(f"❌ Keine Kursdaten für **{ticker}** gefunden. Bitte prüfe das Ticker-Symbol.")
    st.stop()

# ==================== DERIVED METRICS ====================
price = hist["Close"].iloc[-1]
price_prev = hist["Close"].iloc[-2] if len(hist) > 1 else price
price_change = price - price_prev
price_change_pct = (price_change / price_prev * 100) if price_prev != 0 else 0

fcf = yf_info.get("freeCashflow")
market_cap = yf_info.get("marketCap")
revenue = yf_info.get("totalRevenue")
fcf_yield = (fcf / market_cap * 100) if fcf and market_cap else 0
# FCF Margin = FCF / Umsatz (operative Unternehmenskennzahl für Rule of 40)
fcf_margin = (fcf / revenue * 100) if fcf and revenue else None

rev_growth = (yf_info.get("revenueGrowth") or 0) * 100
earnings_growth = (yf_info.get("earningsGrowth") or 0) * 100
profit_margin = (yf_info.get("profitMargins") or 0) * 100
gross_margin = (yf_info.get("grossMargins") or 0) * 100
operating_margin = (yf_info.get("operatingMargins") or 0) * 100
# Rule of 40 = Rev Growth % + FCF Margin % (Branchenstandard für SaaS)
rule_of_40 = (rev_growth + fcf_margin) if fcf_margin is not None else None

trailing_pe = yf_info.get("trailingPE")
forward_pe = yf_info.get("forwardPE")
debt = yf_info.get("debtToEquity") or 0
beta = yf_info.get("beta") or 1
dividend_yield = (yf_info.get("dividendYield") or 0) * 100
shares_outstanding = yf_info.get("sharesOutstanding")
shares_float = yf_info.get("floatShares")
shares_short = yf_info.get("sharesShort")
short_ratio = yf_info.get("shortRatio")
pct_held_insider = yf_info.get("heldPercentInsiders")
pct_held_institutions = yf_info.get("heldPercentInstitutions")
trailing_eps = yf_info.get("trailingEps")
forward_eps = yf_info.get("forwardEps")
enterprise_value = yf_info.get("enterpriseValue")
week52_high = yf_info.get("fiftyTwoWeekHigh")
week52_low = yf_info.get("fiftyTwoWeekLow")
target_mean = yf_info.get("targetMeanPrice")
recommendation = yf_info.get("recommendationKey", "").replace("_", " ").title()
sector = yf_info.get("sector", "")
industry = yf_info.get("industry", "")
# Logo: FMP Image-Endpoint (öffentlich, kein API-Key nötig)
logo_url = f"https://financialmodelingprep.com/image-stock/{ticker}.png"

# Rule of 40 nur für SaaS/Tech/Cyber relevant
show_rule_of_40 = is_saas_or_cyber(sector, industry)

# Verwässerung berechnen — split-bereinigt, 5-Jahres-Fenster
dilution_pct = None
if share_history is not None and not (isinstance(share_history, pd.DataFrame) and share_history.empty):
    try:
        if isinstance(share_history, pd.Series):
            sh = share_history.dropna().sort_index()
        elif isinstance(share_history, pd.DataFrame) and len(share_history.columns) > 0:
            sh = share_history.iloc[:, 0].dropna().sort_index()
        else:
            sh = pd.Series(dtype=float)
        # Split-Bereinigung: timezone-sicher (beide Seiten als naive)
        def _naive(ts):
            t = pd.Timestamp(ts)
            return t.tz_localize(None) if t.tzinfo is None else t.tz_convert(None)
        def _naive_index(idx):
            if hasattr(idx, "tz") and idx.tz is not None:
                return idx.tz_convert(None)
            return idx
        if len(sh) > 0 and splits_data is not None and len(splits_data) > 0:
            sh = sh.copy()
            sh_idx_naive = _naive_index(sh.index)
            for split_date, ratio in splits_data.items():
                if ratio <= 0:
                    continue
                try:
                    sd = _naive(split_date)
                    mask = sh_idx_naive < sd
                    sh.iloc[mask.values] = sh.iloc[mask.values].values * ratio
                except Exception:
                    continue
        # Nur letzte 5 Jahre
        sh_idx_naive = _naive_index(sh.index)
        five_years_ago = pd.Timestamp.now().replace(tzinfo=None) - pd.DateOffset(years=5)
        sh = sh[sh_idx_naive >= five_years_ago]
        if len(sh) >= 2:
            oldest = sh.iloc[0]
            newest = sh.iloc[-1]
            if oldest > 0:
                dilution_pct = (newest - oldest) / oldest * 100
    except:
        pass

# Neue Investor-Kennzahlen
total_cash = yf_info.get("totalCash")
total_debt = yf_info.get("totalDebt") or 0
net_cash = (total_cash - total_debt) if total_cash is not None else None
net_cash_per_share = (net_cash / shares_outstanding) if net_cash is not None and shares_outstanding else None
price_to_fcf = (market_cap / fcf) if fcf and fcf > 0 and market_cap else None
short_pct_float = yf_info.get("shortPercentOfFloat")
total_shareholder_yield = (fcf_yield + dividend_yield) if (fcf and market_cap) else (dividend_yield if dividend_yield else None)
earnings_ts = yf_info.get("earningsTimestamp") or yf_info.get("earningsDate")
earnings_date_str = ""
try:
    from datetime import datetime
    if isinstance(earnings_ts, (int, float)) and earnings_ts > 0:
        earnings_date_str = datetime.fromtimestamp(earnings_ts).strftime("%d.%m.%Y")
    elif isinstance(earnings_ts, list) and earnings_ts:
        earnings_date_str = pd.Timestamp(earnings_ts[0]).strftime("%d.%m.%Y")
except:
    pass

peg_ratio = next(
    (fmp_metrics.get(k) for k in ["priceToEarningsGrowthRatioTTM", "pegRatioTTM", "pegRatio"]
     if fmp_metrics.get(k) is not None),
    yf_info.get("pegRatio")
)

roic_val = fmp_metrics.get("returnOnInvestedCapitalTTM")
if roic_val is not None:
    roic_val *= 100
else:
    roe = fmp_metrics.get("returnOnEquityTTM") or yf_info.get("returnOnEquity")
    roic_val = roe * 100 if roe is not None else None

quality_score = compute_score(rev_growth, fcf_yield, gross_margin, roic_val,
                               profit_margin, rule_of_40, peg_ratio, debt, operating_margin,
                               use_rule_of_40=show_rule_of_40)

# 52-week position
week52_pos = None
if week52_high and week52_low and week52_high != week52_low:
    week52_pos = (price - week52_low) / (week52_high - week52_low) * 100

# Upside to analyst target
upside = ((target_mean - price) / price * 100) if target_mean and price else None

# ==================== HEADER ====================
change_class = "header-change-pos" if price_change >= 0 else "header-change-neg"
change_arrow = "▲" if price_change >= 0 else "▼"
company_name = yf_info.get("longName", ticker)

# Logo HTML — FMP Image-Endpoint direkt einbinden
initials = "".join(w[0] for w in company_name.split()[:2]).upper() if company_name else ticker[:2]
logo_html = f"""
<div style="position:relative;height:52px;width:52px;margin-right:16px;flex-shrink:0;">
    <div style="position:absolute;inset:0;background:#1a3a5c;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:700;color:#64b5f6;">{initials}</div>
    <img src="{logo_url}" style="position:absolute;inset:0;height:52px;width:52px;border-radius:8px;background:#fff;padding:4px;object-fit:contain;"
         onerror="this.style.visibility='hidden'">
</div>"""

st.markdown(f"""
<div class="header-wrap">
    <div style="display:flex; align-items:center;">
        {logo_html}
        <div>
            <div class="header-title">{company_name}</div>
            <div class="header-sub">{ticker} · {sector} · {industry}</div>
            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                <span style="background:#1a2744; color:#64b5f6; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600;">{recommendation}</span>
                {'<span style="background:#1a2e1a; color:#00e676; border-radius:6px; padding:3px 10px; font-size:0.78rem; font-weight:600;">📅 Earnings: ' + earnings_date_str + '</span>' if earnings_date_str else ''}
            </div>
        </div>
    </div>
    <div>
        <div class="header-price">${price:.2f}</div>
        <div class="{change_class}" style="text-align:right;">{change_arrow} {abs(price_change):.2f} ({abs(price_change_pct):.2f}%)</div>
        {'<div style="color:#546e7a; font-size:0.78rem; text-align:right; margin-top:4px;">Ziel: $' + f'{target_mean:.2f}' + ' <span style="color:' + ('#00e676' if upside and upside > 0 else '#ff5252') + '">(' + ('+' if upside and upside > 0 else '') + f'{upside:.1f}%)' + '</span></div>' if upside else ''}
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== SCORE + KEY METRICS ROW ====================
if show_rule_of_40:
    col_score, col_r40, col_roic, col_fcf, col_gm = st.columns([1.2, 1, 1, 1, 1])
else:
    col_score, col_roic, col_fcf, col_gm, col_rev = st.columns([1.2, 1, 1, 1, 1])

with col_score:
    sc = quality_score
    sc_color = score_color(sc)
    sc_lbl = score_label(sc)
    st.markdown(f"""
    <div class="score-section">
        <div class="score-title">Qualitäts-Score</div>
        <div class="score-num" style="color:{sc_color};">{sc}</div>
        <div class="score-label">{sc_lbl}</div>
    </div>
    """, unsafe_allow_html=True)

def mini_card(label, value, good, ok, fmt=".1f", suffix="", inverse=False):
    b = badge(value, good, ok, fmt, inverse)
    val_str = f"{value:{fmt}}{suffix}" if value is not None else "N/A"
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{val_str}</div>
        <div style="margin-top:6px;">{b}</div>
    </div>
    """

if show_rule_of_40:
    with col_r40:
        st.markdown(mini_card("Rule of 40", rule_of_40, 40, 20, ".1f", "%"), unsafe_allow_html=True)
with col_roic:
    st.markdown(mini_card("ROIC", roic_val, 20, 10, ".1f", "%"), unsafe_allow_html=True)
with col_fcf:
    st.markdown(mini_card("FCF Yield", fcf_yield, 5, 2, ".1f", "%"), unsafe_allow_html=True)
with col_gm:
    st.markdown(mini_card("Gross Margin", gross_margin, 60, 40, ".1f", "%"), unsafe_allow_html=True)
if not show_rule_of_40:
    with col_rev:
        st.markdown(mini_card("Rev. Growth", rev_growth, 15, 5, ".1f", "%"), unsafe_allow_html=True)

# ==================== 52-WEEK BAR ====================
if week52_pos is not None:
    bar_color = "#00e676" if week52_pos > 70 else "#ffd600" if week52_pos > 30 else "#ff5252"
    st.markdown(f"""
    <div style="background:#0d1526; border:1px solid #1e3a5f; border-radius:14px; padding:16px 22px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#78909c; font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:1px;">52-Wochen Range</span>
            <span style="color:#64b5f6; font-size:0.82rem; font-weight:600;">{week52_pos:.0f}% vom Tief</span>
        </div>
        <div style="background:#1e2d45; border-radius:8px; height:8px; position:relative;">
            <div style="background:{bar_color}; width:{week52_pos:.0f}%; height:100%; border-radius:8px;"></div>
            <div style="position:absolute; top:-4px; left:{week52_pos:.0f}%; transform:translateX(-50%);">
                <div style="background:{bar_color}; width:16px; height:16px; border-radius:50%; border:2px solid #080d18;"></div>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:8px;">
            <span style="color:#546e7a; font-size:0.78rem;">${week52_low:.2f}</span>
            <span style="color:#eceff1; font-size:0.85rem; font-weight:600;">${price:.2f}</span>
            <span style="color:#546e7a; font-size:0.78rem;">${week52_high:.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== CHART ====================
st.markdown("<div class='section-header'>📉 Kurs & Fair Value Kanal</div>", unsafe_allow_html=True)

hist_plot = hist.copy()
if len(hist_plot) >= 2:
    x = np.arange(len(hist_plot))
    close_prices = hist_plot["Close"].values

    try:
        coeff = np.polyfit(x, close_prices, 1)
        trend = np.polyval(coeff, x)
    except:
        trend = np.zeros(len(x))

    residuals = close_prices - trend
    std_res = np.std(residuals)

    upper2 = trend + 2 * std_res
    lower2 = trend - 2 * std_res
    upper3 = trend + 3 * std_res
    lower3 = trend - 3 * std_res

    # DCF Fair Value für Chart (konservative Defaults)
    dcf_fair_val = dcf_valuation(fcf, shares_outstanding,
                                  min(max(rev_growth, 3), 30), 2.5, 10, 10)

    # Volume subplot
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.78, 0.22],
        vertical_spacing=0.03
    )

    # Outer band (±3σ)
    fig.add_trace(go.Scatter(
        x=hist_plot.index, y=upper3,
        name="Oberes Band (3σ)", line=dict(color="rgba(100,181,246,0.0)"),
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=hist_plot.index, y=lower3,
        name="Fair Value Kanal (3σ)", line=dict(color="rgba(100,181,246,0.0)"),
        fill="tonexty", fillcolor="rgba(21,101,192,0.08)",
        showlegend=True
    ), row=1, col=1)

    # Inner band (±2σ)
    fig.add_trace(go.Scatter(
        x=hist_plot.index, y=upper2,
        name="Oberes Band (2σ)", line=dict(color="rgba(100,181,246,0.25)", dash="dot", width=1),
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=hist_plot.index, y=lower2,
        name="Unteres Band (2σ)", line=dict(color="rgba(100,181,246,0.25)", dash="dot", width=1),
        fill="tonexty", fillcolor="rgba(21,101,192,0.12)",
        showlegend=True
    ), row=1, col=1)

    # Trend
    fig.add_trace(go.Scatter(
        x=hist_plot.index, y=trend,
        name="Trendlinie", line=dict(color="#64b5f6", width=1.5, dash="dash"),
    ), row=1, col=1)

    # Price
    fig.add_trace(go.Scatter(
        x=hist_plot.index, y=hist_plot["Close"],
        name="Kurs", line=dict(color="#00e5ff", width=2),
        fill="tonexty", fillcolor="rgba(0,229,255,0.04)",
    ), row=1, col=1)

    # DCF Fair Value Linie
    if dcf_fair_val and dcf_fair_val > 0:
        fv_color = "#00e676" if dcf_fair_val > price else "#ff5252"
        fig.add_hline(y=dcf_fair_val, line_dash="dot", line_color=fv_color, line_width=2,
                      annotation_text=f"DCF Fair Value ${dcf_fair_val:.0f}",
                      annotation_font_color=fv_color, row=1, col=1)

    # Analyst target line
    if target_mean:
        fig.add_hline(y=target_mean, line_dash="dot", line_color="#ffd600", line_width=1.5,
                      annotation_text=f"Analyst Ziel ${target_mean:.0f}",
                      annotation_font_color="#ffd600", row=1, col=1)

    # Volume
    colors_vol = ["#00e676" if c >= o else "#ff5252"
                  for c, o in zip(hist_plot["Close"], hist_plot["Open"])]
    fig.add_trace(go.Bar(
        x=hist_plot.index, y=hist_plot["Volume"],
        name="Volumen", marker_color=colors_vol, opacity=0.6,
        showlegend=False
    ), row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,21,38,0.8)",
        height=580,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(13,21,38,0.8)",
            bordercolor="#1e3a5f", borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
        xaxis2=dict(showgrid=False),
        yaxis2=dict(showgrid=False, zeroline=False),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Chart insight
    current_pos = close_prices[-1] - trend[-1]
    pos_sigma = current_pos / std_res if std_res > 0 else 0
    pos_text = "deutlich überbewertet (>2σ über Trend)" if pos_sigma > 2 else \
               "leicht überbewertet (>1σ)" if pos_sigma > 1 else \
               "leicht unterbewertet (<-1σ)" if pos_sigma < -1 else \
               "deutlich unterbewertet (<-2σ)" if pos_sigma < -2 else \
               "fair bewertet (nahe Trend)"

    dcf_text = f" | DCF Fair Value: <strong style='color:{'#00e676' if dcf_fair_val and dcf_fair_val > price else '#ff5252'}'>${dcf_fair_val:.2f}</strong>" if dcf_fair_val else ""
    st.markdown(f"""
    <div class="insight-box">
        <strong>📊 Chart-Analyse:</strong> {ticker} notiert aktuell
        <strong style="color:{'#ff5252' if pos_sigma > 1 else '#00e676' if pos_sigma < -1 else '#ffd600'}">
        {pos_sigma:+.1f}σ</strong> vom linearen Trend —
        {pos_text}. Der Fair-Value-Kanal (±2σ) liegt zwischen
        <strong>${lower2[-1]:.2f}</strong> und <strong>${upper2[-1]:.2f}</strong>{dcf_text}.
    </div>
    """, unsafe_allow_html=True)

# ==================== TABS ====================
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Kennzahlen", "📈 Wachstum", "🏦 Fundamental", "⚖️ Bewertung",
    "📉 Chart Analyse", "🔍 Insider & Peers", "📰 News"
])

with tab1:
    st.markdown("<div class='section-header'>Kern-Kennzahlen</div>", unsafe_allow_html=True)
    if show_rule_of_40:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(mini_card("Rule of 40", rule_of_40, 40, 20, ".1f", "%"), unsafe_allow_html=True)
        with c2:
            st.markdown(mini_card("FCF Yield", fcf_yield, 5, 2, ".1f", "%"), unsafe_allow_html=True)
        with c3:
            st.markdown(mini_card("Gross Margin", gross_margin, 60, 40, ".1f", "%"), unsafe_allow_html=True)
        with c4:
            st.markdown(mini_card("ROIC", roic_val, 20, 10, ".1f", "%"), unsafe_allow_html=True)
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(mini_card("FCF Yield", fcf_yield, 5, 2, ".1f", "%"), unsafe_allow_html=True)
        with c2:
            st.markdown(mini_card("Gross Margin", gross_margin, 60, 40, ".1f", "%"), unsafe_allow_html=True)
        with c3:
            st.markdown(mini_card("ROIC", roic_val, 20, 10, ".1f", "%"), unsafe_allow_html=True)
        st.markdown(f"""
        <div class="insight-box">
        <strong>ℹ️ Rule of 40:</strong> Nicht angezeigt — diese Kennzahl ist primär für SaaS- und Cybersecurity-Unternehmen relevant
        ({sector} / {industry}).
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Margen</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(mini_card("Profit Margin", profit_margin, 15, 5, ".1f", "%"), unsafe_allow_html=True)
    with c2:
        st.markdown(mini_card("Operating Margin", operating_margin, 20, 10, ".1f", "%"), unsafe_allow_html=True)
    with c3:
        st.markdown(mini_card("Dividend Yield", dividend_yield, 3, 1, ".2f", "%"), unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='section-header'>Wachstum</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(mini_card("Revenue Growth", rev_growth, 15, 5, ".1f", "%"), unsafe_allow_html=True)
    with c2:
        st.markdown(mini_card("Earnings Growth", earnings_growth, 15, 5, ".1f", "%"), unsafe_allow_html=True)
    with c3:
        st.markdown(mini_card("FCF Yield", fcf_yield, 5, 2, ".1f", "%"), unsafe_allow_html=True)

    # Growth sparkline (if hist available)
    if len(hist) > 252:
        annual = hist["Close"].resample("YE").last().pct_change().dropna() * 100
        if len(annual) >= 2:
            fig_g = go.Figure(go.Bar(
                x=[str(y.year) for y in annual.index],
                y=annual.values,
                marker_color=["#00e676" if v >= 0 else "#ff5252" for v in annual.values],
                text=[f"{v:.1f}%" for v in annual.values],
                textposition="outside",
            ))
            fig_g.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,21,38,0.8)",
                height=280,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=True, zerolinecolor="#1e2d45"),
                xaxis=dict(showgrid=False),
                title=dict(text="Jährliche Kursperformance", font=dict(color="#64b5f6", size=13)),
            )
            st.plotly_chart(fig_g, use_container_width=True)

with tab3:
    st.markdown("<div class='section-header'>Bilanz</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Cap</div>
            <div class="metric-value">{fmt_large(market_cap)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Enterprise Value</div>
            <div class="metric-value">{fmt_large(enterprise_value)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Free Cash Flow</div>
            <div class="metric-value">{fmt_large(fcf)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Debt/Equity</div>
            <div class="metric-value">{safe_float(debt, 1)}</div>
        </div>""", unsafe_allow_html=True)

    # ── Aktienanzahl & Verwässerung ──
    st.markdown("<div class='section-header'>📊 Aktienstruktur & Verwässerung</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        so_str = f"{shares_outstanding/1e9:.3f}B" if shares_outstanding else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Aktien Ausstehend</div>
            <div class="metric-value">{so_str}</div>
            <div class="metric-sub">Shares Outstanding</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        sf_str = f"{shares_float/1e9:.3f}B" if shares_float else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Free Float</div>
            <div class="metric-value">{sf_str}</div>
            <div class="metric-sub">Handelbare Aktien</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        dil_color = "#ff5252" if dilution_pct and dilution_pct > 5 else "#ffd600" if dilution_pct and dilution_pct > 2 else "#00e676"
        dil_str = f"+{dilution_pct:.1f}%" if dilution_pct and dilution_pct > 0 else (f"{dilution_pct:.1f}%" if dilution_pct else "N/A")
        dil_badge = f'<span style="color:{dil_color}; font-weight:700;">{dil_str}</span>' if dilution_pct else '<span class="metric-badge-gray">N/A</span>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Verwässerung (5J)</div>
            <div class="metric-value">{dil_str}</div>
            <div style="margin-top:6px;">{dil_badge}</div>
            <div class="metric-sub">Aktienanzahl Veränderung</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        insider_pct = f"{pct_held_insider*100:.1f}%" if pct_held_insider else "N/A"
        inst_pct = f"{pct_held_institutions*100:.1f}%" if pct_held_institutions else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Besitzstruktur</div>
            <div class="metric-value" style="font-size:1rem;">{insider_pct} Insider</div>
            <div class="metric-sub">{inst_pct} Institutionen</div>
        </div>""", unsafe_allow_html=True)

    c5, c6 = st.columns(2)
    with c5:
        ncp_str = f"${net_cash_per_share:.2f}" if net_cash_per_share is not None else "N/A"
        ncp_color = "#00e676" if net_cash_per_share and net_cash_per_share > 0 else "#ff5252"
        ncp_badge = f'<span style="color:{ncp_color}; font-weight:700;">{ncp_str}</span>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Net Cash / Aktie</div>
            <div class="metric-value">{ncp_str}</div>
            <div style="margin-top:6px;">{ncp_badge}</div>
            <div class="metric-sub">Kasse minus Schulden je Aktie</div>
        </div>""", unsafe_allow_html=True)
    with c6:
        short_str = f"{short_pct_float*100:.1f}%" if short_pct_float else "N/A"
        short_color = "#ff5252" if short_pct_float and short_pct_float > 0.15 else "#ffd600" if short_pct_float and short_pct_float > 0.07 else "#00e676"
        short_badge = f'<span style="color:{short_color}; font-weight:700;">{short_str}</span>' if short_pct_float else '<span class="metric-badge-gray">N/A</span>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Short Interest</div>
            <div class="metric-value">{short_str}</div>
            <div style="margin-top:6px;">{short_badge}</div>
            <div class="metric-sub">% des Free Float leerverkauft</div>
        </div>""", unsafe_allow_html=True)

    # Share count history chart
    if share_history is not None:
        try:
            if isinstance(share_history, pd.Series):
                sh = share_history.dropna()
            elif isinstance(share_history, pd.DataFrame) and len(share_history.columns) > 0:
                sh = share_history.iloc[:, 0].dropna()
            else:
                sh = pd.Series(dtype=float)
            if len(sh) >= 4:
                fig_sh = go.Figure(go.Scatter(
                    x=sh.index, y=sh.values / 1e9,
                    mode="lines+markers",
                    line=dict(color="#ffd600", width=2),
                    marker=dict(size=5, color="#ffd600"),
                    fill="tozeroy",
                    fillcolor="rgba(255,214,0,0.06)",
                    name="Aktienanzahl (Mrd.)"
                ))
                fig_sh.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(13,21,38,0.8)",
                    height=200,
                    margin=dict(l=0, r=0, t=10, b=0),
                    showlegend=False,
                    yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False, title="Mrd. Aktien"),
                    xaxis=dict(showgrid=False),
                )
                st.plotly_chart(fig_sh, use_container_width=True)
                if dilution_pct:
                    dil_warn = "⚠️ Starke Verwässerung" if dilution_pct > 10 else "🟡 Moderate Verwässerung" if dilution_pct > 3 else "✅ Geringe Verwässerung / Rückkäufe"
                    st.markdown(f'<div class="insight-box"><strong>Aktienanzahl Trend:</strong> {dil_warn} ({dil_str} seit Messbeginn). Für Investoren ist ein Rückgang der Aktienanzahl positiv (Buybacks).</div>', unsafe_allow_html=True)
        except:
            pass

    st.markdown("<div class='section-header'>EPS</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Trailing EPS</div>
            <div class="metric-value">${safe_float(trailing_eps)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Forward EPS</div>
            <div class="metric-value">${safe_float(forward_eps)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        eps_growth = ((forward_eps - trailing_eps) / abs(trailing_eps) * 100) if trailing_eps and forward_eps else None
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">EPS Wachstum (fwd)</div>
            <div class="metric-value">{f"{eps_growth:.1f}%" if eps_growth is not None else "N/A"}</div>
        </div>""", unsafe_allow_html=True)

with tab4:
    st.markdown("<div class='section-header'>Bewertungsmultiples</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(mini_card("P/E Trailing", trailing_pe, 15, 25, ".1f", "x", inverse=True), unsafe_allow_html=True)
    with c2:
        st.markdown(mini_card("P/E Forward", forward_pe, 15, 25, ".1f", "x", inverse=True), unsafe_allow_html=True)
    with c3:
        st.markdown(mini_card("PEG Ratio", peg_ratio, 1.5, 2.5, ".2f", "", inverse=True), unsafe_allow_html=True)
    with c4:
        st.markdown(mini_card("Debt/Equity", debt, 50, 100, ".1f", "", inverse=True), unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(mini_card("Beta", beta, 0.8, 1.5, ".2f", ""), unsafe_allow_html=True)
    with c2:
        st.markdown(mini_card("Dividend Yield", dividend_yield, 3, 1, ".2f", "%"), unsafe_allow_html=True)
    with c3:
        pfcf_str = f"{price_to_fcf:.1f}x" if price_to_fcf else "N/A"
        pfcf_color = "#00e676" if price_to_fcf and price_to_fcf < 20 else "#ffd600" if price_to_fcf and price_to_fcf < 35 else "#ff5252"
        pfcf_badge = f'<span style="color:{pfcf_color}; font-weight:700;">{pfcf_str}</span>' if price_to_fcf else '<span class="metric-badge-gray">N/A</span>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Price / FCF</div>
            <div class="metric-value">{pfcf_str}</div>
            <div style="margin-top:6px;">{pfcf_badge}</div>
            <div class="metric-sub">&lt;20x = attraktiv</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        tsy_str = f"{total_shareholder_yield:.1f}%" if total_shareholder_yield else "N/A"
        tsy_color = "#00e676" if total_shareholder_yield and total_shareholder_yield > 5 else "#ffd600" if total_shareholder_yield and total_shareholder_yield > 2 else "#78909c"
        tsy_badge = f'<span style="color:{tsy_color}; font-weight:700;">{tsy_str}</span>' if total_shareholder_yield else '<span class="metric-badge-gray">N/A</span>'
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Shareholder Yield</div>
            <div class="metric-value">{tsy_str}</div>
            <div style="margin-top:6px;">{tsy_badge}</div>
            <div class="metric-sub">FCF Yield + Dividende</div>
        </div>""", unsafe_allow_html=True)

    # Analyst target
    if target_mean and price:
        st.markdown("<div class='section-header'>Analyst Konsensus</div>", unsafe_allow_html=True)
        upside_val = (target_mean - price) / price * 100
        up_color = "#00e676" if upside_val > 0 else "#ff5252"
        st.markdown(f"""
        <div class="insight-box">
            <strong>Kursziel:</strong> ${target_mean:.2f} |
            <strong style="color:{up_color}">
            {'▲' if upside_val > 0 else '▼'} {abs(upside_val):.1f}% Upside
            </strong> vom aktuellen Kurs |
            <strong>Empfehlung:</strong> {recommendation}
        </div>
        """, unsafe_allow_html=True)

    # DCF
    if show_dcf:
        st.markdown("<div class='section-header'>💰 DCF Rechner</div>", unsafe_allow_html=True)
        default_growth = min(max(int(rev_growth), 5), 30)
        st.markdown(f"""
        <div class="insight-box" style="margin-bottom:12px;">
            <strong>ℹ️ DCF Hinweis:</strong> Der DCF-Wert reagiert stark auf die Eingaben.
            Bei High-Growth-Aktien wie Halbleiter/KI-Unternehmen empfiehlt sich eine
            <strong>konservative Wachstumsrate</strong> (10–20%) und ein höherer Diskontsatz (10–12%),
            um Euphorie-Prämien zu vermeiden. Akt. Rev. Growth: <strong>{rev_growth:.1f}%</strong>.
        </div>
        """, unsafe_allow_html=True)
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            g_rate = st.slider("Wachstumsrate (%)", 0, 40, default_growth, 1, key="dcf_g")
        with d2:
            t_rate = st.slider("Terminal Growth (%)", 1, 5, 2, 1, key="dcf_t")
        with d3:
            d_rate = st.slider("Diskontrate (%)", 5, 15, 10, 1, key="dcf_d")
        with d4:
            yrs = st.slider("Jahre", 5, 15, 10, 1, key="dcf_y")

        fair_val = dcf_valuation(fcf, shares_outstanding, g_rate, t_rate, d_rate, yrs)
        if fair_val:
            margin = (fair_val - price) / price * 100
            m_color = "#00e676" if margin > 0 else "#ff5252"
            m_label = "Margin of Safety" if margin > 0 else "Überbewertung"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #0d2137, #0a1a2e); border:1px solid #1e3a5f; border-radius:16px; padding:22px; margin-top:10px; text-align:center;">
                <div style="color:#78909c; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">DCF Fairer Wert</div>
                <div style="color:#eceff1; font-size:2.5rem; font-weight:800;">${fair_val:.2f}</div>
                <div style="color:{m_color}; font-size:1rem; margin-top:6px; font-weight:600;">
                    {'▲' if margin > 0 else '▼'} {abs(margin):.1f}% {m_label}
                </div>
                <div style="color:#546e7a; font-size:0.78rem; margin-top:6px;">
                    Aktueller Kurs: ${price:.2f} | FCF: {fmt_large(fcf)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Nicht genug Daten für DCF-Berechnung (FCF oder Shares fehlen).")

# ==================== TAB 5: CHART ANALYSE ====================
with tab5:
    st.markdown("<div class='section-header'>📉 Technische Chart-Analyse</div>", unsafe_allow_html=True)

    chart_mode = st.radio(
        "Zeitrahmen", ["Täglich (5J)", "Wöchentlich (2J)", "Monatlich (5J)"],
        horizontal=True, key="chart_mode"
    )
    ema_options = st.multiselect(
        "EMAs anzeigen", ["EMA 20", "EMA 50", "EMA 100", "EMA 200"],
        default=["EMA 20", "EMA 50", "EMA 200"], key="ema_sel"
    )
    chart_type = st.radio("Chart-Typ", ["Candlestick", "Linie"], horizontal=True, key="ctype")

    if chart_mode == "Wöchentlich (2J)":
        chart_data = hist_weekly.copy()
        title_suffix = "Wochenkerzen"
    elif chart_mode == "Monatlich (5J)":
        chart_data = hist_monthly.copy()
        title_suffix = "Monatskerzen"
    else:
        chart_data = hist.copy()
        title_suffix = "Tageskerzen"

    if chart_data.empty:
        st.warning("Keine Daten für diesen Zeitrahmen verfügbar.")
    else:
        ema_periods = {"EMA 20": 20, "EMA 50": 50, "EMA 100": 100, "EMA 200": 200}
        ema_colors = {"EMA 20": "#ffd600", "EMA 50": "#00e5ff", "EMA 100": "#ff9100", "EMA 200": "#ef5350"}

        fig_ta = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            row_heights=[0.75, 0.25],
            vertical_spacing=0.03
        )

        if chart_type == "Candlestick":
            fig_ta.add_trace(go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"],
                high=chart_data["High"],
                low=chart_data["Low"],
                close=chart_data["Close"],
                name=f"{ticker} ({title_suffix})",
                increasing_line_color="#00e676",
                decreasing_line_color="#ff5252",
                increasing_fillcolor="#00e676",
                decreasing_fillcolor="#ff5252",
            ), row=1, col=1)
        else:
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index,
                y=chart_data["Close"],
                name=f"{ticker} ({title_suffix})",
                line=dict(color="#00e5ff", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,229,255,0.04)",
            ), row=1, col=1)

        for ema_name in ema_options:
            period = ema_periods[ema_name]
            if len(chart_data) >= period:
                ema_vals = compute_ema(chart_data["Close"], period)
                fig_ta.add_trace(go.Scatter(
                    x=chart_data.index,
                    y=ema_vals,
                    name=ema_name,
                    line=dict(color=ema_colors[ema_name], width=1.5),
                ), row=1, col=1)

        if target_mean:
            fig_ta.add_hline(y=target_mean, line_dash="dot", line_color="#ffd600", line_width=1.5,
                             annotation_text=f"Analyst Ziel ${target_mean:.0f}",
                             annotation_font_color="#ffd600", row=1, col=1)

        colors_vol_ta = ["#00e676" if c >= o else "#ff5252"
                         for c, o in zip(chart_data["Close"], chart_data["Open"])]
        fig_ta.add_trace(go.Bar(
            x=chart_data.index, y=chart_data["Volume"],
            name="Volumen", marker_color=colors_vol_ta, opacity=0.6,
            showlegend=False
        ), row=2, col=1)

        fig_ta.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)",
            height=620,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.01,
                xanchor="right", x=1,
                bgcolor="rgba(13,21,38,0.8)",
                bordercolor="#1e3a5f", borderwidth=1,
                font=dict(size=11)
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(showgrid=False, zeroline=False, rangeslider=dict(visible=False)),
            yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
            xaxis2=dict(showgrid=False),
            yaxis2=dict(showgrid=False, zeroline=False),
            hovermode="x unified",
            title=dict(text=f"{company_name} — {title_suffix}", font=dict(color="#64b5f6", size=14)),
        )
        st.plotly_chart(fig_ta, use_container_width=True)

        if ema_options and len(chart_data) > 0:
            current_price_c = chart_data["Close"].iloc[-1]
            ema_insights = []
            for ema_name in ema_options:
                period = ema_periods[ema_name]
                if len(chart_data) >= period:
                    ema_now = compute_ema(chart_data["Close"], period).iloc[-1]
                    pct_diff = (current_price_c - ema_now) / ema_now * 100
                    status = "oberhalb ✅" if pct_diff > 0 else "unterhalb ⚠️"
                    ema_insights.append(f"{ema_name}: {status} ({pct_diff:+.1f}%)")
            if ema_insights:
                st.markdown(f"""
                <div class="insight-box">
                    <strong>📊 EMA-Analyse ({title_suffix}):</strong> {' | '.join(ema_insights)}
                </div>
                """, unsafe_allow_html=True)

# ==================== TAB 6: INSIDER & PEERS ====================
with tab6:
    col_ins, col_peers = st.columns(2)

    # Insider
    with col_ins:
        st.markdown("<div class='section-header'>👤 Insider Transaktionen</div>", unsafe_allow_html=True)
        if show_insider and insider_df is not None and not insider_df.empty:
            try:
                show_cols = [c for c in ["Insider", "Relationship", "Transaction", "Value", "Date", "Shares"] if c in insider_df.columns]
                display_df = insider_df[show_cols].head(10).copy() if show_cols else insider_df.head(10).copy()
                # Style it
                for _, row in display_df.iterrows():
                    tx = str(row.get("Transaction", ""))
                    is_buy = "Buy" in tx or "Purchase" in tx or "Kauf" in tx
                    tx_class = "insider-buy" if is_buy else "insider-sell"
                    name = row.get("Insider", row.get("Name", "–"))
                    val = row.get("Value", "")
                    date = str(row.get("Date", ""))[:10]
                    val_str = f"${val:,.0f}" if isinstance(val, (int, float)) else str(val)
                    st.markdown(f"""
                    <div class="insider-row">
                        <span style="color:#b0bec5;">{str(name)[:20]}</span>
                        <span class="{tx_class}">{tx}</span>
                        <span style="color:#64b5f6;">{val_str}</span>
                        <span style="color:#546e7a;">{date}</span>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.caption(f"Fehler beim Anzeigen: {e}")
        else:
            st.markdown('<div class="insight-box">Keine Insider-Daten verfügbar.</div>', unsafe_allow_html=True)

    # Peer comparison
    with col_peers:
        st.markdown("<div class='section-header'>🔁 Peer Vergleich</div>", unsafe_allow_html=True)
        if show_peers and peers:
            peer_tickers = [ticker] + peers
            peer_data = []
            for pt in peer_tickers:
                try:
                    pi = yf.Ticker(pt).info
                    peer_data.append({
                        "Ticker": pt,
                        "Kurs": pi.get("currentPrice") or pi.get("regularMarketPrice"),
                        "P/E": pi.get("trailingPE"),
                        "Mkt Cap": pi.get("marketCap"),
                        "Rev Growth": (pi.get("revenueGrowth") or 0) * 100,
                        "Profit Mg": (pi.get("profitMargins") or 0) * 100,
                    })
                except:
                    pass

            if peer_data:
                pdf = pd.DataFrame(peer_data).set_index("Ticker")
                pdf["Mkt Cap"] = pdf["Mkt Cap"].apply(fmt_large)
                pdf["P/E"] = pdf["P/E"].apply(lambda v: f"{v:.1f}" if v else "N/A")
                pdf["Rev Growth"] = pdf["Rev Growth"].apply(lambda v: f"{v:.1f}%")
                pdf["Profit Mg"] = pdf["Profit Mg"].apply(lambda v: f"{v:.1f}%")
                pdf["Kurs"] = pdf["Kurs"].apply(lambda v: f"${v:.2f}" if v else "N/A")
                st.dataframe(pdf, use_container_width=True)
        elif not FMP_API_KEY:
            st.markdown('<div class="insight-box">FMP API Key erforderlich für Peer-Daten.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box">Keine Peers gefunden.</div>', unsafe_allow_html=True)

# ==================== TAB 7: NEWS ====================
with tab7:
    st.markdown("<div class='section-header'>📰 Aktuelle News</div>", unsafe_allow_html=True)
    if NEWS_API_KEY:
        try:
            url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={NEWS_API_KEY}&language=de&sortBy=publishedAt&pageSize=10"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                articles = r.json().get("articles", [])
                if articles:
                    for article in articles[:8]:
                        title = article.get("title", "")
                        source = article.get("source", {}).get("name", "")
                        pub_at = article.get("publishedAt", "")[:10]
                        url_a = article.get("url", "#")
                        desc = article.get("description", "") or ""
                        st.markdown(f"""
                        <div class="metric-card" style="margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                <span style="color:#64b5f6; font-size:0.75rem; font-weight:600;">{source}</span>
                                <span style="color:#546e7a; font-size:0.72rem;">{pub_at}</span>
                            </div>
                            <a href="{url_a}" target="_blank" style="color:#eceff1; font-size:0.9rem; font-weight:600; text-decoration:none; line-height:1.4;">
                                {title}
                            </a>
                            <div style="color:#78909c; font-size:0.78rem; margin-top:6px; line-height:1.4;">
                                {desc[:150]}{'…' if len(desc) > 150 else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Keine News gefunden.")
        except Exception as e:
            st.warning(f"News konnten nicht geladen werden: {e}")
    else:
        try:
            from datetime import datetime
            stock_obj = yf.Ticker(ticker)
            news_items = stock_obj.news
            if news_items:
                for item in news_items[:8]:
                    title = item.get("title", "")
                    publisher = item.get("publisher", "")
                    pub_time = item.get("providerPublishTime", 0)
                    link = item.get("link", "#")
                    pub_str = datetime.fromtimestamp(pub_time).strftime("%Y-%m-%d") if pub_time else ""
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span style="color:#64b5f6; font-size:0.75rem; font-weight:600;">{publisher}</span>
                            <span style="color:#546e7a; font-size:0.72rem;">{pub_str}</span>
                        </div>
                        <a href="{link}" target="_blank" style="color:#eceff1; font-size:0.9rem; font-weight:600; text-decoration:none; line-height:1.4;">
                            {title}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keine News über yFinance verfügbar. Für mehr News: NEWS_API_KEY setzen.")
        except:
            st.info("News konnten nicht geladen werden.")

# ==================== INSIGHTS ====================
st.markdown("<div class='section-header'>💡 Investor Insights</div>", unsafe_allow_html=True)

insights = []
if show_rule_of_40:
    if rule_of_40 >= 40:
        insights.append(f"✅ <strong>Rule of 40:</strong> {rule_of_40:.0f} — hervorragendes Wachstum+Profitabilitäts-Gleichgewicht.")
    elif rule_of_40 >= 20:
        insights.append(f"🟡 <strong>Rule of 40:</strong> {rule_of_40:.0f} — solide, aber Potenzial nach oben.")
    else:
        insights.append(f"🔴 <strong>Rule of 40:</strong> {rule_of_40:.0f} — Wachstum und/oder Profitabilität schwach.")

if roic_val and roic_val >= 20:
    insights.append(f"✅ <strong>ROIC {roic_val:.1f}%:</strong> Exzellente Kapitalallokation — Burggrabenindikator.")
elif roic_val and roic_val < 10:
    insights.append(f"⚠️ <strong>ROIC {roic_val:.1f}%:</strong> Kapitalrendite unter den Kapitalkosten — prüfen!")

if peg_ratio and peg_ratio < 1:
    insights.append(f"✅ <strong>PEG {peg_ratio:.2f}:</strong> Aktie erscheint günstig relativ zum Wachstum.")
elif peg_ratio and peg_ratio > 3:
    insights.append(f"⚠️ <strong>PEG {peg_ratio:.2f}:</strong> Hohe Bewertung relativ zum Wachstum.")

if week52_pos is not None and week52_pos < 30:
    insights.append(f"📉 Kurs nahe 52-Wochen-Tief ({week52_pos:.0f}% vom Tief) — mögliche Einstiegsgelegenheit.")

if not insights:
    insights.append("Nicht genug Daten für automatische Insights.")

for ins in insights:
    st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)

# ==================== DEBUG ====================
with st.expander("🔍 Debug: Rohdaten"):
    col1, col2 = st.columns(2)
    with col1:
        st.caption("yFinance Info")
        st.json({k: v for k, v in list(yf_info.items())[:30]})
    with col2:
        st.caption("FMP Metrics")
        st.json(fmp_metrics)

st.markdown('<div class="caption-text">Aktien-Tool Bäumer v4 · yFinance + FMP · Alle Daten ohne Gewähr</div>', unsafe_allow_html=True)
