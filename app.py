import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import requests
import re
import json
import time
import datetime as _dt

# ==================== CONFIG ====================
st.set_page_config(
    page_title="StocksMB",
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
        padding: 24px 28px;
        margin-bottom: 28px;
        display: flex;
        align-items: flex-start;
        box-shadow: 0 8px 32px rgba(0,120,255,0.15);
        overflow: hidden;
    }
    @media (max-width: 640px) {
        .header-wrap { padding: 18px 16px; border-radius: 14px; }
        .header-title { font-size: 1.4rem !important; }
        .header-price { font-size: 1.6rem !important; }
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

    /* CSS-Tooltip — funktioniert auf Desktop (hover) und Mobile (tap/focus) */
    .tt { position:relative; display:inline-block; cursor:help; }
    .tt .tt-box {
        visibility:hidden; opacity:0;
        position:absolute; bottom:130%; left:50%; transform:translateX(-50%);
        background:#0d2340; color:#b0bec5; font-size:0.65rem; line-height:1.5;
        padding:8px 12px; border-radius:8px; border:1px solid #1e3a5f;
        white-space:normal; width:220px; z-index:9999; pointer-events:none;
        transition:opacity 0.15s;
    }
    .tt:hover .tt-box, .tt:focus .tt-box { visibility:visible; opacity:1; }
    .tt-icon { color:#455a64; font-size:0.7rem; vertical-align:super; }

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

    /* Grok AI Analysis */
    .grok-box {
        background: linear-gradient(135deg, #0a1628, #0d1f3c);
        border: 1px solid #1e3a5f;
        border-left: 3px solid #7c3aed;
        border-radius: 14px;
        padding: 22px 26px;
        margin: 16px 0;
    }
    .grok-box h4 {
        color: #a78bfa;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0 0 6px 0;
    }
    .grok-box p {
        color: #b0bec5;
        font-size: 0.88rem;
        line-height: 1.7;
        margin: 0 0 10px 0;
    }
    .grok-box ul {
        color: #b0bec5;
        font-size: 0.88rem;
        line-height: 1.7;
        padding-left: 18px;
        margin: 0 0 10px 0;
    }
    .grok-box li { margin-bottom: 4px; }
    .grok-section-title {
        color: #64b5f6;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 14px 0 6px 0;
        border-bottom: 1px solid #1e3a5f;
        padding-bottom: 4px;
    }
    .grok-badge {
        display: inline-block;
        background: #1e1b4b;
        color: #a78bfa;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 8px;
    }

    /* Grok Chat */
    .chat-wrap {
        background: #0a1628;
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        padding: 18px 20px;
        margin: 12px 0;
        max-height: 420px;
        overflow-y: auto;
    }
    .chat-user-msg {
        display: flex;
        justify-content: flex-end;
        margin: 8px 0;
    }
    .chat-user-bubble {
        background: #1a2744;
        border-radius: 12px 12px 4px 12px;
        border-right: 3px solid #64b5f6;
        padding: 9px 14px;
        max-width: 82%;
        color: #e0e0e0;
        font-size: 0.87rem;
        line-height: 1.5;
    }
    .chat-ai-msg {
        display: flex;
        justify-content: flex-start;
        margin: 8px 0;
    }
    .chat-ai-bubble {
        background: #0d1f3c;
        border-radius: 12px 12px 12px 4px;
        border-left: 3px solid #a78bfa;
        padding: 9px 14px;
        max-width: 90%;
        color: #b0bec5;
        font-size: 0.87rem;
        line-height: 1.6;
    }

    /* Watchlist */
    .wl-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #0d1f3c;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        padding: 5px 10px;
        font-size: 0.82rem;
        color: #b0bec5;
        margin: 3px 0;
        width: 100%;
    }
    .wl-chip strong { color: #64b5f6; font-size: 0.85rem; }
    .wl-compare-box {
        background: #0a1628;
        border: 1px solid #1e3a5f;
        border-top: 3px solid #00e5ff;
        border-radius: 14px;
        padding: 20px 22px;
        margin: 16px 0;
    }

    /* Metric card tooltip ❓ */
    .mcard-tip-wrap {
        position: absolute;
        top: 10px;
        right: 12px;
    }
    .mcard-tip-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 17px;
        height: 17px;
        border-radius: 50%;
        background: rgba(100,181,246,0.12);
        color: #546e7a;
        font-size: 0.65rem;
        font-weight: 700;
        cursor: help;
        user-select: none;
        transition: background 0.15s, color 0.15s;
    }
    .mcard-tip-icon:hover,
    .mcard-tip-icon:focus {
        background: rgba(100,181,246,0.28);
        color: #64b5f6;
    }
    .mcard-tip-bubble {
        display: none;
        position: absolute;
        right: 0;
        top: 22px;
        background: #0d1f3c;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 0.76rem;
        color: #b0bec5;
        line-height: 1.55;
        width: 230px;
        z-index: 9999;
        box-shadow: 0 6px 24px rgba(0,0,0,0.6);
        pointer-events: none;
    }
    .mcard-tip-wrap:hover .mcard-tip-bubble,
    .mcard-tip-wrap:focus-within .mcard-tip-bubble {
        display: block;
    }

    /* KI-Analyse CTA Button */
    div[data-testid="stButton"] button[kind="secondary"]#btn_grok,
    div[data-testid="stBaseButton-secondary"][key="btn_grok"] button,
    .ki-cta-wrap div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #4c1d95, #6d28d9, #7c3aed) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 14px !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 20px rgba(124,58,237,0.45), 0 0 0 1px rgba(167,139,250,0.25) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        cursor: pointer !important;
    }
    .ki-cta-wrap div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #5b21b6, #7c3aed, #8b5cf6) !important;
        box-shadow: 0 6px 28px rgba(124,58,237,0.65), 0 0 0 2px rgba(167,139,250,0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Tab-Navigation Buttons ─────────────────────────────────── */
    div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"] {
        background: #0d1526 !important;
        border: 1px solid #1e3a5f !important;
        color: #78909c !important;
        border-radius: 6px 6px 0 0 !important;
        font-size: 0.72rem !important;
        padding: 6px 4px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"]:hover {
        background: #132040 !important;
        color: #b0bec5 !important;
        border-color: #2a4a7f !important;
    }
    div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-primary"] {
        background: rgba(21,101,192,0.25) !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
        border-radius: 6px 6px 0 0 !important;
        font-size: 0.72rem !important;
        padding: 6px 4px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        font-weight: 600 !important;
    }

    /* Mobile: kleinere Nav-Buttons */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"],
        div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-primary"] {
            font-size: 0.62rem !important;
            padding: 5px 2px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== API KEY ====================
import os

FMP_API_KEY    = os.getenv("FMP_API_KEY", "")
NEWS_API_KEY   = os.getenv("NEWS_API_KEY", "")
XAI_API_KEY    = os.getenv("XAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SEC_API_KEY    = os.getenv("SEC_API_KEY", "")   # sec-api.io (Segment Revenue + XBRL)
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")

# ── Supabase Auth & Watchlist helpers ─────────────────────────────────
def _sb_headers(access_token: str = "") -> dict:
    token = access_token or SUPABASE_KEY
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

def sb_login(email: str, password: str):
    """Returns (data_dict, error_str). data_dict has access_token + user."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None, "SUPABASE_URL / SUPABASE_KEY nicht gesetzt."
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10,
        )
        data = r.json()
        if r.status_code == 200 and data.get("access_token"):
            return data, None
        return None, data.get("error_description") or data.get("msg") or "Login fehlgeschlagen."
    except Exception as e:
        return None, str(e)

def sb_register(email: str, password: str):
    """Returns (data_dict, error_str)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None, "SUPABASE_URL / SUPABASE_KEY nicht gesetzt."
    try:
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10,
        )
        data = r.json()
        if r.status_code == 200 and data.get("id"):
            return data, None
        return None, data.get("error_description") or data.get("msg") or "Registrierung fehlgeschlagen."
    except Exception as e:
        return None, str(e)

def sb_load_watchlist(access_token: str) -> list[dict]:
    """Returns list of {ticker, name} dicts from Supabase."""
    if not SUPABASE_URL or not access_token:
        return []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/watchlists",
            headers={**_sb_headers(access_token), "Accept": "application/json"},
            params={"select": "ticker,name", "order": "added_at.asc"},
            timeout=10,
        )
        if r.status_code == 200:
            return [{"ticker": row["ticker"], "name": row.get("name") or row["ticker"]}
                    for row in r.json()]
    except Exception:
        pass
    return []

def sb_add_ticker(access_token: str, user_id: str, ticker: str, name: str = ""):
    if not SUPABASE_URL or not access_token:
        return
    try:
        requests.post(
            f"{SUPABASE_URL}/rest/v1/watchlists",
            headers={**_sb_headers(access_token), "Prefer": "return=minimal"},
            json={"user_id": user_id, "ticker": ticker, "name": name},
            timeout=10,
        )
    except Exception:
        pass

def sb_remove_ticker(access_token: str, ticker: str):
    if not SUPABASE_URL or not access_token:
        return
    try:
        requests.delete(
            f"{SUPABASE_URL}/rest/v1/watchlists",
            headers={**_sb_headers(access_token), "Prefer": "return=minimal"},
            params={"ticker": f"eq.{ticker}"},
            timeout=10,
        )
    except Exception:
        pass

# ==================== CACHE ====================
@st.cache_data(ttl=3600)
def _patch_info_from_statements(stock: "yf.Ticker", info: dict) -> dict:
    """
    Für japanische / nicht-US Aktien liefert yfinance.info oft 0/None für Margen,
    Wachstum und FCF. Fallback: direkt aus GuV, Cashflow und Bilanz berechnen.
    FCF-Patch läuft IMMER (unabhängig von Margins) — behebt JP-FCF-Yield=0-Bug.
    """
    info = dict(info)  # shallow copy — nie das cached dict mutieren

    def _get_df(*attr_names):
        for name in attr_names:
            try:
                df = getattr(stock, name, None)
                if df is not None and not df.empty:
                    return df
            except Exception:
                pass
        return None

    def _row(df, *names):
        for n in names:
            if n in df.index:
                return df.loc[n]
        return None

    # ── FCF immer patchen wenn 0/None (häufig bei JP/EU) ─────────────────
    if not info.get("freeCashflow"):
        # Versuch 1: operatingCashflow aus info (oft vorhanden wenn freeCashflow fehlt)
        ocf_info = info.get("operatingCashflow")
        if ocf_info:
            # CapEx aus info abziehen falls verfügbar; sonst OCF × 0.75 als konservativer Proxy
            capex_info = info.get("capitalExpenditures") or 0
            info["freeCashflow"] = int(ocf_info - abs(capex_info))
        else:
            # Versuch 2: aus Cash-Flow-Statement
            cf = _get_df("cash_flow", "cashflow")
            if cf is not None and len(cf.columns) >= 1:
                fcf_r = _row(cf, "Free Cash Flow", "FreeCashFlow")
                ocf_r = _row(cf,
                             "Operating Cash Flow", "OperatingCashFlow",
                             "Total Cash From Operating Activities",
                             "Cash From Operations")
                cap_r = _row(cf,
                             "Capital Expenditure", "CapitalExpenditure",
                             "Capital Expenditures",
                             "Purchase Of Property Plant And Equipment",
                             "Purchases of PPE")
                if fcf_r is not None:
                    v = float(fcf_r.iloc[0] or 0)
                    if v: info["freeCashflow"] = int(v)
                elif ocf_r is not None:
                    ocf = float(ocf_r.iloc[0] or 0)
                    cap = float(cap_r.iloc[0] or 0) if cap_r is not None else 0
                    if ocf: info["freeCashflow"] = int(ocf + cap)  # cap is negative

    # ── Margen + Wachstum: nur patchen wenn alle fehlen ──────────────────
    needs_margin_patch = not any([
        info.get("grossMargins"), info.get("operatingMargins"),
        info.get("profitMargins"), info.get("revenueGrowth"),
    ])
    if needs_margin_patch:
        fs = _get_df("income_stmt", "financials")
        if fs is not None and len(fs.columns) >= 2:
            rev = _row(fs, "Total Revenue", "TotalRevenue", "Revenue")
            gp  = _row(fs, "Gross Profit", "GrossProfit")
            op  = _row(fs, "Operating Income", "OperatingIncome", "EBIT")
            ni  = _row(fs, "Net Income", "NetIncome",
                       "Net Income Common Stockholders")
            if rev is not None:
                r0 = float(rev.iloc[0] or 0)
                r1 = float(rev.iloc[1] or 0)
                if r0 and r1:
                    info["revenueGrowth"] = (r0 / r1) - 1
                    info["totalRevenue"]  = int(r0)
                if r0:
                    if gp is not None: info["grossMargins"]     = float(gp.iloc[0] or 0) / r0
                    if op is not None: info["operatingMargins"] = float(op.iloc[0] or 0) / r0
                    if ni is not None: info["profitMargins"]    = float(ni.iloc[0] or 0) / r0

    return info


@st.cache_data(ttl=3600)
def load_yfinance(ticker: str):
    stock = yf.Ticker(ticker)
    info, hist, insider = {}, pd.DataFrame(), pd.DataFrame()
    try:
        info = stock.info
    except:
        pass
    try:
        # Patch missing margins/growth from financial statements (non-US stocks)
        info = _patch_info_from_statements(stock, info)
    except Exception:
        pass
    try:
        _today = _dt.date.today().strftime("%Y-%m-%d")
        _start5y = (_dt.date.today() - _dt.timedelta(days=5*365+10)).strftime("%Y-%m-%d")
        hist = stock.history(start=_start5y, end=_today)
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
        _today = _dt.date.today().strftime("%Y-%m-%d")
        _start2y = (_dt.date.today() - _dt.timedelta(days=2*365+10)).strftime("%Y-%m-%d")
        hist_weekly = stock.history(start=_start2y, end=_today, interval="1wk")
    except:
        pass
    try:
        _today = _dt.date.today().strftime("%Y-%m-%d")
        _start5y = (_dt.date.today() - _dt.timedelta(days=5*365+10)).strftime("%Y-%m-%d")
        hist_monthly = stock.history(start=_start5y, end=_today, interval="1mo")
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
def load_quarterly_financials(ticker: str):
    """Lädt Quartalsdaten: Umsatz, Nettogewinn, EPS der letzten 8 Quartale."""
    stock = yf.Ticker(ticker)
    rev, net, eps_q = pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float)
    try:
        qi = stock.quarterly_income_stmt
        if qi is not None and not qi.empty:
            for row in ["Total Revenue", "Revenue"]:
                if row in qi.index:
                    rev = qi.loc[row].dropna().sort_index()[::-1][:8][::-1]
                    break
            for row in ["Net Income", "Net Income Common Stockholders"]:
                if row in qi.index:
                    net = qi.loc[row].dropna().sort_index()[::-1][:8][::-1]
                    break
            for row in ["Diluted EPS", "Basic EPS"]:
                if row in qi.index:
                    eps_q = qi.loc[row].dropna().sort_index()[::-1][:8][::-1]
                    break
    except:
        pass
    return rev, net, eps_q

@st.cache_data(ttl=86400)
def load_annual_financials(ticker: str):
    """Jahresabschluss: Umsatz, Nettogewinn, EPS, FCF, EBITDA, CapEx, Goodwill (5 Jahre)."""
    stock = yf.Ticker(ticker)
    rev = pd.Series(dtype=float)
    net = pd.Series(dtype=float)
    eps = pd.Series(dtype=float)
    fcf = pd.Series(dtype=float)
    ebitda_s = pd.Series(dtype=float)
    shares_ann = pd.Series(dtype=float)
    capex_s = pd.Series(dtype=float)
    goodwill_s = pd.Series(dtype=float)
    try:
        inc = stock.income_stmt
        if inc is not None and not inc.empty:
            for row in ["Total Revenue", "Revenue"]:
                if row in inc.index:
                    rev = inc.loc[row].dropna().sort_index(); break
            for row in ["Net Income", "Net Income Common Stockholders"]:
                if row in inc.index:
                    net = inc.loc[row].dropna().sort_index(); break
            for row in ["Diluted EPS", "Basic EPS"]:
                if row in inc.index:
                    eps = inc.loc[row].dropna().sort_index(); break
            for row in ["EBITDA", "Normalized EBITDA"]:
                if row in inc.index:
                    ebitda_s = inc.loc[row].dropna().sort_index(); break
            for row in ["Diluted Average Shares", "Basic Average Shares", "Ordinary Shares Number"]:
                if row in inc.index:
                    shares_ann = inc.loc[row].dropna().sort_index(); break
    except Exception:
        pass
    try:
        cf = stock.cash_flow
        if cf is not None and not cf.empty:
            if "Free Cash Flow" in cf.index:
                fcf = cf.loc["Free Cash Flow"].dropna().sort_index()
            elif "Operating Cash Flow" in cf.index and "Capital Expenditure" in cf.index:
                fcf = (cf.loc["Operating Cash Flow"] + cf.loc["Capital Expenditure"]).dropna().sort_index()
            # CapEx (absolut, als positive Zahl für die Darstellung)
            for row in ["Capital Expenditure", "Purchase Of Property Plant And Equipment"]:
                if row in cf.index:
                    raw = cf.loc[row].dropna().sort_index()
                    capex_s = raw.abs()   # CapEx ist in yfinance negativ
                    break
    except Exception:
        pass
    try:
        bs = stock.balance_sheet
        if bs is not None and not bs.empty:
            for row in ["Goodwill", "Goodwill And Other Intangible Assets"]:
                if row in bs.index:
                    goodwill_s = bs.loc[row].dropna().sort_index(); break
    except Exception:
        pass
    return rev, net, eps, fcf, shares_ann, ebitda_s, capex_s, goodwill_s

@st.cache_data(ttl=86400)
def _sec_cik(ticker: str):
    """Ticker → zero-padded CIK string. Returns None on failure."""
    try:
        r = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers={"User-Agent": "StocksMB app@stocksmb.app"},
            timeout=10,
        )
        if r.status_code == 200:
            for entry in r.json().values():
                if entry.get("ticker", "").upper() == ticker.upper():
                    return str(entry["cik_str"]).zfill(10)
    except Exception:
        pass
    return None


@st.cache_data(ttl=86400)
def _sec_annual(ticker: str) -> dict:
    """
    SEC EDGAR XBRL — gratis, kein API-Key, bis zu 15 Jahre Jahresabschluss.
    Gibt Dict mit pd.Series: rev, net, eps, fcf, shares, ebitda
    Nur US-Aktien (10-K Pflicht). Rate-Limit: 10 req/s — durch Cache kein Problem.
    """
    cik = _sec_cik(ticker)
    if not cik:
        return {}
    try:
        r = requests.get(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            headers={"User-Agent": "StocksMB app@stocksmb.app"},
            timeout=20,
        )
        if r.status_code != 200:
            return {}
        gaap = r.json().get("facts", {}).get("us-gaap", {})
    except Exception:
        return {}

    def _extract(concept: str, unit: str = "USD") -> pd.Series:
        rows = gaap.get(concept, {}).get("units", {}).get(unit, [])
        ann = [d for d in rows if d.get("form") == "10-K" and d.get("fp") == "FY"]
        if not ann:
            return pd.Series(dtype=float)
        by_fy: dict = {}
        for d in ann:
            fy = d.get("fy")
            if fy and (fy not in by_fy or d.get("filed", "") > by_fy[fy].get("filed", "")):
                by_fy[fy] = d
        ordered = sorted(by_fy.values(), key=lambda x: x["end"])
        return pd.Series(
            [d["val"] for d in ordered],
            index=pd.to_datetime([d["end"] for d in ordered]),
        ).sort_index()

    def _first(*series) -> pd.Series:
        for s in series:
            if not s.empty:
                return s
        return pd.Series(dtype=float)

    rev = _first(
        _extract("Revenues"),
        _extract("RevenueFromContractWithCustomerExcludingAssessedTax"),
        _extract("SalesRevenueNet"),
        _extract("RevenuesNetOfInterestExpense"),
    )
    net = _first(
        _extract("NetIncomeLoss"),
        _extract("NetIncomeLossAvailableToCommonStockholdersBasic"),
    )
    eps = _first(
        _extract("EarningsPerShareDiluted", "USD/shares"),
        _extract("EarningsPerShareBasic",   "USD/shares"),
    )
    op_cf = _first(_extract("NetCashProvidedByUsedInOperatingActivities"))
    capex = _first(
        _extract("PaymentsToAcquirePropertyPlantAndEquipment"),
        _extract("CapitalExpendituresIncurredButNotYetPaid"),
    )
    shares = _first(
        _extract("WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
        _extract("CommonStockSharesOutstanding", "shares"),
    )
    op_inc = _first(_extract("OperatingIncomeLoss"))
    dna    = _first(
        _extract("DepreciationDepletionAndAmortization"),
        _extract("DepreciationAndAmortization"),
    )

    # FCF = Operating CF − CapEx
    fcf = pd.Series(dtype=float)
    if not op_cf.empty:
        if not capex.empty:
            idx = op_cf.index.intersection(capex.index)
            if len(idx) > 0:
                fcf = (op_cf.loc[idx] - capex.loc[idx]).sort_index()
        else:
            fcf = op_cf

    # EBITDA = Operating Income + D&A
    ebitda = pd.Series(dtype=float)
    if not op_inc.empty and not dna.empty:
        idx = op_inc.index.intersection(dna.index)
        if len(idx) > 0:
            ebitda = (op_inc.loc[idx] + dna.loc[idx]).sort_index()

    return {"rev": rev, "net": net, "eps": eps, "fcf": fcf, "shares": shares, "ebitda": ebitda}


@st.cache_data(ttl=86400)
def load_extended_financials(ticker: str, api_key: str = ""):
    """Bis zu 15 Jahre Jahresdaten — FMP primär (api_key als Cache-Key), yfinance Fallback."""
    def _clean(s: pd.Series) -> pd.Series:
        return s.replace(0, float("nan")).dropna().sort_index()

    rev = pd.Series(dtype=float)
    net = pd.Series(dtype=float)
    eps = pd.Series(dtype=float)
    fcf = pd.Series(dtype=float)
    ebitda_ext = pd.Series(dtype=float)
    shares = pd.Series(dtype=float)
    price_annual = pd.Series(dtype=float)

    if api_key:
        try:
            r = requests.get(
                f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}",
                params={"limit": 15, "apikey": api_key}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    dates, revs, nets, epss, shs, ebs = [], [], [], [], [], []
                    for d in data:
                        try:
                            dates.append(pd.Timestamp(d["date"]))
                            revs.append(float(d.get("revenue") or 0))
                            nets.append(float(d.get("netIncome") or 0))
                            epss.append(float(d.get("epsdiluted") or 0))
                            shs.append(float(d.get("weightedAverageShsOutDil") or 0))
                            ebs.append(float(d.get("ebitda") or 0))
                        except Exception:
                            continue
                    if dates:
                        rev        = _clean(pd.Series(revs, index=dates))
                        net        = _clean(pd.Series(nets, index=dates))
                        eps        = _clean(pd.Series(epss, index=dates))
                        shares     = _clean(pd.Series(shs,  index=dates))
                        ebitda_ext = _clean(pd.Series(ebs,  index=dates))
        except Exception:
            pass
        try:
            r2 = requests.get(
                f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}",
                params={"limit": 15, "apikey": api_key}, timeout=10)
            if r2.status_code == 200:
                data2 = r2.json()
                if isinstance(data2, list) and data2:
                    cf_dates, fcfs = [], []
                    for d in data2:
                        try:
                            cf_dates.append(pd.Timestamp(d["date"]))
                            fcfs.append(float(d.get("freeCashFlow") or 0))
                        except Exception:
                            continue
                    if cf_dates:
                        fcf = _clean(pd.Series(fcfs, index=cf_dates))
        except Exception:
            pass

    # SEC EDGAR XBRL Fallback — gratis, kein Key, bis 15 Jahre (nur US-Aktien)
    try:
        _sec = _sec_annual(ticker)
        if _sec:
            def _prefer_longer(current: pd.Series, sec_s: pd.Series) -> pd.Series:
                sec_s = _clean(sec_s)
                if sec_s.empty:
                    return current
                # Use SEC data if it's longer OR current is empty
                return sec_s if (current.empty or len(sec_s) > len(current)) else current
            rev        = _prefer_longer(rev,        _sec.get("rev",    pd.Series(dtype=float)))
            net        = _prefer_longer(net,        _sec.get("net",    pd.Series(dtype=float)))
            eps        = _prefer_longer(eps,        _sec.get("eps",    pd.Series(dtype=float)))
            fcf        = _prefer_longer(fcf,        _sec.get("fcf",    pd.Series(dtype=float)))
            shares     = _prefer_longer(shares,     _sec.get("shares", pd.Series(dtype=float)))
            ebitda_ext = _prefer_longer(ebitda_ext, _sec.get("ebitda", pd.Series(dtype=float)))
    except Exception:
        pass

    # yfinance fallback for any series still empty
    try:
        stock = yf.Ticker(ticker)
        inc = stock.income_stmt
        if inc is not None and not inc.empty:
            if rev.empty:
                for row in ["Total Revenue", "Revenue"]:
                    if row in inc.index:
                        rev = _clean(inc.loc[row]); break
            if net.empty:
                for row in ["Net Income", "Net Income Common Stockholders"]:
                    if row in inc.index:
                        net = _clean(inc.loc[row]); break
            if eps.empty:
                for row in ["Diluted EPS", "Basic EPS"]:
                    if row in inc.index:
                        eps = inc.loc[row].dropna().sort_index(); break
            if shares.empty:
                for row in ["Diluted Average Shares", "Basic Average Shares"]:
                    if row in inc.index:
                        shares = _clean(inc.loc[row]); break
            if ebitda_ext.empty:
                for row in ["EBITDA", "Normalized EBITDA"]:
                    if row in inc.index:
                        ebitda_ext = _clean(inc.loc[row]); break
        if fcf.empty:
            cf = stock.cash_flow
            if cf is not None and not cf.empty:
                if "Free Cash Flow" in cf.index:
                    fcf = _clean(cf.loc["Free Cash Flow"])
    except Exception:
        pass

    # Annual price performance (up to 15y from yfinance history)
    try:
        _15y_start = (_dt.date.today() - _dt.timedelta(days=15*365+20)).strftime("%Y-%m-%d")
        _h = yf.Ticker(ticker).history(start=_15y_start, end=_dt.date.today().strftime("%Y-%m-%d"))
        if not _h.empty:
            price_annual = _h["Close"].resample("YE").last().pct_change().dropna() * 100
    except Exception:
        pass

    return rev, net, eps, fcf, shares, price_annual, ebitda_ext

@st.cache_data(ttl=86400)
def load_earnings_surprises(ticker: str) -> list[dict]:
    """Lädt EPS Beat/Miss — FMP primär, yfinance als Fallback."""
    results = []

    # Attempt 1: FMP earnings-surprises (zuverlässigste Quelle)
    if FMP_API_KEY:
        try:
            r = requests.get(
                f"https://financialmodelingprep.com/api/v3/earnings-surprises/{ticker}",
                params={"apikey": FMP_API_KEY}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    for item in data[:8]:
                        act = item.get("actualEarningResult")
                        est = item.get("estimatedEarning")
                        if act is None:
                            continue
                        act, est = float(act), (float(est) if est is not None else None)
                        surp_pct = ((act - est) / abs(est) * 100) if est else 0
                        verdict = "Beat" if surp_pct > 2 else "Miss" if surp_pct < -2 else "In Line"
                        date_str = item.get("date", "")[:7]
                        try:
                            date_str = pd.Timestamp(item["date"]).strftime("%b %Y")
                        except Exception:
                            pass
                        results.append({
                            "date":     date_str,
                            "estimate": est,
                            "actual":   act,
                            "surp_pct": surp_pct,
                            "verdict":  verdict,
                        })
                    if results:
                        return results
        except Exception:
            pass

    # Attempt 2: yfinance earnings_history (yfinance >= 0.2.38)
    try:
        stock = yf.Ticker(ticker)
        eh = stock.earnings_history
        if eh is not None and not eh.empty:
            for date, row in eh.sort_index(ascending=False).head(8).iterrows():
                act_raw = row.get("epsActual") or row.get("Reported EPS")
                est_raw = row.get("epsEstimate") or row.get("EPS Estimate")
                if act_raw is None or pd.isna(act_raw):
                    continue
                act = float(act_raw)
                est = float(est_raw) if est_raw is not None and pd.notna(est_raw) else None
                surp_pct = ((act - est) / abs(est) * 100) if est else 0
                verdict = "Beat" if surp_pct > 2 else "Miss" if surp_pct < -2 else "In Line"
                results.append({
                    "date":     date.strftime("%b %Y") if hasattr(date, "strftime") else str(date)[:7],
                    "estimate": est,
                    "actual":   act,
                    "surp_pct": surp_pct,
                    "verdict":  verdict,
                })
            if results:
                return results
    except Exception:
        pass

    # Attempt 3: yfinance get_earnings_dates
    try:
        stock = yf.Ticker(ticker)
        try:
            df = stock.get_earnings_dates(limit=20)
        except Exception:
            df = stock.earnings_dates
        if df is not None and not df.empty:
            past = df[df["Reported EPS"].notna()].copy()
            if not past.empty:
                past = past.sort_index(ascending=False).head(8)
                for date, row in past.iterrows():
                    act_raw = row.get("Reported EPS")
                    est_raw = row.get("EPS Estimate")
                    if pd.isna(act_raw):
                        continue
                    act = float(act_raw)
                    est = float(est_raw) if pd.notna(est_raw) else None
                    surp_pct = ((act - est) / abs(est) * 100) if est else 0
                    verdict = "Beat" if surp_pct > 2 else "Miss" if surp_pct < -2 else "In Line"
                    results.append({
                        "date":     date.strftime("%b %Y") if hasattr(date, "strftime") else str(date)[:7],
                        "estimate": est,
                        "actual":   act,
                        "surp_pct": surp_pct,
                        "verdict":  verdict,
                    })
                if results:
                    return results
    except Exception:
        pass

    # Attempt 4: yfinance quarterly EPS aus income_stmt (nur Actual, kein Estimate-Vergleich)
    try:
        stock = yf.Ticker(ticker)
        qi = stock.quarterly_income_stmt
        if qi is not None and not qi.empty:
            for row_name in ["Diluted EPS", "Basic EPS"]:
                if row_name in qi.index:
                    eps_series = qi.loc[row_name].dropna().sort_index(ascending=False).head(8)
                    for date, val in eps_series.items():
                        results.append({
                            "date":     date.strftime("%b %Y") if hasattr(date, "strftime") else str(date)[:7],
                            "estimate": None,
                            "actual":   float(val),
                            "surp_pct": 0,
                            "verdict":  "In Line",
                        })
                    if results:
                        return results
    except Exception:
        pass

    return results


@st.cache_data(ttl=86400)
def load_segment_data(ticker: str) -> dict:
    """
    Lädt Produkt- und Geo-Segmentdaten von FMP.
    Gibt {'product': [...], 'geo': [...]} zurück.
    Jeder Eintrag: {'date': str, 'segments': {name: value}}.
    """
    result = {"product": [], "geo": []}
    if not FMP_API_KEY:
        return result
    for key, endpoint in [
        ("product", "revenue-product-segmentation"),
        ("geo",     "revenue-geographic-segmentation"),
    ]:
        try:
            r = requests.get(
                f"https://financialmodelingprep.com/api/v4/{endpoint}",
                params={"symbol": ticker, "period": "annual", "apikey": FMP_API_KEY},
                timeout=10,
            )
            if r.status_code == 200:
                raw = r.json()
                if isinstance(raw, list):
                    for entry in raw[:6]:           # max. 6 Jahre
                        if not isinstance(entry, dict):
                            continue
                        date_str = entry.get("date", "")
                        segs = {k: float(v) for k, v in entry.items()
                                if k != "date" and v is not None and str(v).replace("-","").replace(".","").isdigit()}
                        if segs:
                            result[key].append({"date": date_str[:4], "segments": segs})
                    result[key].sort(key=lambda x: x["date"])
        except Exception:
            pass
    return result


# ── Persistenter Disk-Cache (überlebt App-Neustarts auf Railway) ────────────
# Bevorzugt /data (Railway Volume) – Fallback ./sec_cache (überlebt Restarts,
# nicht Redeployments). XBRL-Daten: permanent. Query-Listen: 30-Tage-TTL.

def _sec_cache_dir() -> str:
    """Gibt vorhandenes Cache-Verzeichnis zurück (erstellt es bei Bedarf)."""
    for candidate in ["/data/sec_cache", "./sec_cache", "/tmp/sec_cache"]:
        try:
            os.makedirs(candidate, exist_ok=True)
            return candidate
        except OSError:
            continue
    return "/tmp"


def _dcache_get(key: str, ttl_days: float = None):
    """Liest gecachten Wert vom Disk. None wenn nicht vorhanden oder abgelaufen."""
    path = os.path.join(_sec_cache_dir(), f"{key}.json")
    try:
        if os.path.exists(path):
            if ttl_days is not None:
                age = (time.time() - os.path.getmtime(path)) / 86400
                if age > ttl_days:
                    return None
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return None


def _dcache_set(key: str, data) -> None:
    """Schreibt Wert als JSON auf Disk."""
    path = os.path.join(_sec_cache_dir(), f"{key}.json")
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


# ── sec-api.io Segment Revenue (XBRL-to-JSON) ──────────────────────────────

def _clean_seg_name(raw: str) -> str:
    """Bereinigt XBRL-Member-Namen zu lesbarem Text.
    Beispiele: 'aapl:iPhoneMember' → 'iPhone', 'srt:AmericasMember' → 'Americas'
    """
    if not raw:
        return raw
    if ":" in raw:
        raw = raw.split(":", 1)[1]
    for suffix in ["ReportableSegment", "OperatingSegment", "Segment", "Member"]:
        if raw.endswith(suffix):
            raw = raw[: -len(suffix)]
    # CamelCase → space-separated (handles 'GoogleServices' → 'Google Services')
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", raw)
    result = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", " ", spaced)
    return result.strip() or raw


@st.cache_data(ttl=86400)
def _secapi_query(ticker: str, form_type: str = "10-K", count: int = 10) -> list:
    """Filing-Liste via sec-api.io Query API.
    Disk-Cache TTL: 30 Tage (neue 10-K erscheinen nur jährlich).
    Gibt [{accessionNo, periodOfReport, filedAt, ...}, ...] zurück.
    """
    cache_key = f"q_{ticker.upper()}_{form_type.replace('/', '_')}_{count}"
    cached = _dcache_get(cache_key, ttl_days=30)
    if isinstance(cached, list):
        return cached

    if not SEC_API_KEY:
        return []
    try:
        r = requests.post(
            f"https://api.sec-api.io?token={SEC_API_KEY}",
            json={
                "query": {
                    "query_string": {
                        "query": f'ticker:{ticker} AND formType:"{form_type}"'
                    }
                },
                "from": "0",
                "size": str(count),
                "sort": [{"filedAt": {"order": "desc"}}],
            },
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json().get("data", [])
            _dcache_set(cache_key, data)
            return data
    except Exception:
        pass
    return []


@st.cache_data(ttl=604800)
def _secapi_xbrl(accession_no: str) -> dict:
    """XBRL-to-JSON Konverter via sec-api.io.
    Disk-Cache: permanent (historische Filings ändern sich nie — 1× API-Call pro Filing).
    """
    cache_key = f"xbrl_{accession_no.replace('-', '_')}"
    cached = _dcache_get(cache_key)          # kein TTL — XBRL ist unveränderlich
    if isinstance(cached, dict) and cached:
        return cached

    if not SEC_API_KEY:
        return {}
    try:
        r = requests.get(
            "https://api.sec-api.io/xbrl-to-json",
            params={"accession-no": accession_no, "token": SEC_API_KEY},
            timeout=25,
        )
        if r.status_code == 200:
            data = r.json()
            _dcache_set(cache_key, data)
            return data
    except Exception:
        pass
    return {}


def _extract_segments_from_xbrl(xbrl: dict) -> tuple:
    """
    Parst Produkt- und Geo-Segmente aus einem sec-api.io XBRL-JSON-Dict.

    Strategie: Erst gezielter Scan bekannter Income-Sections, dann Breit-Scan
    aller Sections nach beliebigem Konzept mit Segment-Dimension.
    Trennt nach Axis-Typ:
      - ProductOrService / ProductAndService → product_segs
      - Geographical / Geographic            → geo_segs
    """
    INCOME_SECTIONS = [
        "StatementsOfIncome", "StatementsOfOperations",
        "ConsolidatedStatementsOfIncome", "ConsolidatedStatementsOfOperations",
        "StatementsOfEarnings", "IncomeStatement",
        "ConsolidatedStatementsOfOperationsAndComprehensiveIncome",
        "ConsolidatedStatementsOfIncomeAndComprehensiveIncome",
    ]
    REVENUE_CONCEPTS = [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues", "Revenue", "SalesRevenueNet", "NetRevenues",
        "TotalRevenues", "NetRevenue", "SalesRevenueGoodsNet",
        "NetSales", "TotalNetSales",
    ]

    def _has_seg_dim(items_list):
        """Returns True if any item in the list has a ProductOrService/Geographical dimension."""
        for it in items_list:
            seg = it.get("segment")
            if seg is None:
                continue
            for s in (seg if isinstance(seg, list) else [seg]):
                d = s.get("dimension", "")
                if "ProductOrService" in d or "ProductAndService" in d or \
                   "Geographical" in d or "Geographic" in d:
                    return True
        return False

    # ── Pass 1: targeted (known sections + known revenue concepts) ─────
    items: list = []
    for sec in INCOME_SECTIONS:
        section = xbrl.get(sec, {})
        if not isinstance(section, dict):
            continue
        for concept in REVENUE_CONCEPTS:
            data = section.get(concept)
            if isinstance(data, list) and data and _has_seg_dim(data):
                items = data
                break
        if items:
            break

    # ── Pass 2: broad scan — any section, any concept with segment dim ─
    if not items:
        for sec_key, sec_data in xbrl.items():
            if not isinstance(sec_data, dict):
                continue
            for concept, data in sec_data.items():
                if not isinstance(data, list) or not data:
                    continue
                # Only pick revenue/sales-looking concepts in broad scan
                c_lower = concept.lower()
                if not any(k in c_lower for k in ["revenue", "sales", "netsales", "netrevenue"]):
                    continue
                if _has_seg_dim(data):
                    items = data
                    break
            if items:
                break

    if not items:
        return {}, {}

    def _period_months(item: dict) -> int:
        p = item.get("period") or {}
        try:
            return round(
                (pd.Timestamp(p["endDate"]) - pd.Timestamp(p["startDate"])).days / 30.44
            )
        except Exception:
            return 0

    # Keep only 12-month entries (annual); fall back to all if none found
    annual = [i for i in items if abs(_period_months(i) - 12) <= 1]
    if not annual:
        annual = items

    product_segs: dict = {}
    geo_segs: dict = {}

    for item in annual:
        seg = item.get("segment")
        if seg is None:
            continue  # total consolidated value — not a segment row

        segs = seg if isinstance(seg, list) else [seg]

        # Allow up to 2 dims: take the one that is the segment axis
        seg_dims = [s for s in segs if any(k in s.get("dimension", "") for k in
                    ["ProductOrService", "ProductAndService", "Geographical", "Geographic"])]
        if not seg_dims:
            continue
        # If there are non-segment extra dims (e.g. currency), still process the segment dim
        dim    = seg_dims[0].get("dimension", "")
        member = seg_dims[0].get("value", "")

        try:
            val = float(item.get("value") or 0)
        except (ValueError, TypeError):
            continue
        if val == 0:
            continue

        name = _clean_seg_name(member)

        if "ProductOrService" in dim or "ProductAndService" in dim:
            if name not in product_segs or val > product_segs[name]:
                product_segs[name] = val
        elif "Geographical" in dim or "Geographic" in dim:
            if name not in geo_segs or val > geo_segs[name]:
                geo_segs[name] = val

    return product_segs, geo_segs


@st.cache_data(ttl=86400)
def load_secapi_segments(ticker: str) -> dict:
    """
    Holt Segment Revenue (Produkt + Geografie) über bis zu 15 Jahre via sec-api.io XBRL.

    Ablauf:
      1. Query API → Liste von 10-K Filings (Accession Numbers + Perioden)
      2. Pro Filing: XBRL-to-JSON → Segment-Extraktion
      3. Zeitreihe nach Datum sortiert zurückgeben

    Gibt zurück:
      {
        "product": [{"date": "2023", "segments": {"iPhone": 200e9, ...}}, ...],
        "geo":     [{"date": "2022", "segments": {"Americas": 160e9, ...}}, ...]
      }

    Rate-Limit-Hinweis: 1 Query-Call + N XBRL-Calls pro Ticker.
    Durch @st.cache_data(ttl=86400) wird nur 1× täglich gefetcht.
    XBRL-Cache hat TTL=7 Tage (Filings unveränderlich).
    """
    empty: dict = {"product": [], "geo": []}
    if not SEC_API_KEY:
        return empty

    filings = _secapi_query(ticker, form_type="10-K", count=15)
    if not filings:
        return empty

    product_tl: list = []
    geo_tl: list = []

    for filing in filings:
        accn = filing.get("accessionNo", "")
        if not accn:
            continue

        period_str = filing.get("periodOfReport") or filing.get("filedAt", "")
        year = str(period_str)[:4]
        if not year.isdigit():
            continue

        xbrl = _secapi_xbrl(accn)
        if not xbrl:
            continue

        prod_segs, geo_segs = _extract_segments_from_xbrl(xbrl)

        if prod_segs:
            product_tl.append({"date": year, "segments": prod_segs})
        if geo_segs:
            geo_tl.append({"date": year, "segments": geo_segs})

    product_tl.sort(key=lambda x: x["date"])
    geo_tl.sort(key=lambda x: x["date"])

    return {"product": product_tl, "geo": geo_tl}


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

# ==================== WATCHLIST DATA ====================
@st.cache_data(ttl=3600)
def load_watchlist_metrics(t: str) -> dict:
    """Kompakte Kennzahlen für Watchlist-Vergleich (gecacht)."""
    try:
        info = yf.Ticker(t).info
        mc  = info.get("marketCap")
        fcf = info.get("freeCashflow")
        return {
            "name":     info.get("shortName", t),
            "price":    info.get("currentPrice") or info.get("regularMarketPrice"),
            "mkt_cap":  mc,
            "gm":       (info.get("grossMargins") or 0) * 100,
            "op_mg":    (info.get("operatingMargins") or 0) * 100,
            "net_mg":   (info.get("profitMargins") or 0) * 100,
            "rev_gr":   (info.get("revenueGrowth") or 0) * 100,
            "fcf_y":    (fcf / mc * 100) if fcf and mc else 0.0,
            "roe":      (info.get("returnOnEquity") or 0) * 100,
            "pe":       info.get("trailingPE"),
        }
    except Exception:
        return {"name": t, "price": None, "mkt_cap": None,
                "gm": 0, "op_mg": 0, "net_mg": 0,
                "rev_gr": 0, "fcf_y": 0, "roe": 0, "pe": None}

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

# ==================== SECTOR BENCHMARKS ====================
# Typische Medianwerte je Sektor (S&P 500 historische Durchschnitte)
# Fallback-Peers wenn FMP keine Peers liefert (Free-Tier-Limit)
SECTOR_PEERS_FALLBACK = {
    "Technology":             ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "ORCL", "ADBE", "CRM"],
    "Healthcare":             ["JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY", "TMO", "ABT"],
    "Consumer Cyclical":      ["AMZN", "TSLA", "HD", "NKE", "MCD", "SBUX", "TGT", "LOW"],
    "Consumer Defensive":     ["WMT", "PG", "KO", "COST", "PEP", "PM", "MO", "CL"],
    "Financial Services":     ["JPM", "BAC", "WFC", "GS", "MS", "BLK", "C", "AXP"],
    "Energy":                 ["XOM", "CVX", "COP", "SLB", "EOG", "PXD", "MPC", "PSX"],
    "Industrials":            ["HON", "UPS", "CAT", "RTX", "LMT", "GE", "DE", "MMM"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "T", "VZ", "CMCSA", "SNAP"],
    "Utilities":              ["NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL"],
    "Real Estate":            ["AMT", "PLD", "CCI", "EQIX", "O", "SPG", "WELL", "AVB"],
    "Basic Materials":        ["LIN", "APD", "SHW", "FCX", "NEM", "AA", "NUE", "ECL"],
}

SECTOR_BENCHMARKS = {
    "Technology": {
        "Bruttomarge": 65.0, "Op. Marge": 22.0, "Gewinnmarge": 18.0,
        "ROIC": 22.0, "Umsatzwachstum": 12.0, "FCF Yield": 2.5,
    },
    "Healthcare": {
        "Bruttomarge": 60.0, "Op. Marge": 18.0, "Gewinnmarge": 14.0,
        "ROIC": 16.0, "Umsatzwachstum": 8.0, "FCF Yield": 3.0,
    },
    "Consumer Cyclical": {
        "Bruttomarge": 38.0, "Op. Marge": 10.0, "Gewinnmarge": 7.0,
        "ROIC": 14.0, "Umsatzwachstum": 6.0, "FCF Yield": 3.5,
    },
    "Consumer Defensive": {
        "Bruttomarge": 40.0, "Op. Marge": 12.0, "Gewinnmarge": 9.0,
        "ROIC": 18.0, "Umsatzwachstum": 5.0, "FCF Yield": 4.0,
    },
    "Financial Services": {
        "Bruttomarge": 55.0, "Op. Marge": 28.0, "Gewinnmarge": 22.0,
        "ROIC": 12.0, "Umsatzwachstum": 8.0, "FCF Yield": 4.0,
    },
    "Energy": {
        "Bruttomarge": 35.0, "Op. Marge": 14.0, "Gewinnmarge": 10.0,
        "ROIC": 10.0, "Umsatzwachstum": 5.0, "FCF Yield": 5.0,
    },
    "Industrials": {
        "Bruttomarge": 32.0, "Op. Marge": 12.0, "Gewinnmarge": 8.0,
        "ROIC": 12.0, "Umsatzwachstum": 6.0, "FCF Yield": 3.5,
    },
    "Communication Services": {
        "Bruttomarge": 55.0, "Op. Marge": 18.0, "Gewinnmarge": 14.0,
        "ROIC": 14.0, "Umsatzwachstum": 7.0, "FCF Yield": 3.0,
    },
    "Utilities": {
        "Bruttomarge": 48.0, "Op. Marge": 20.0, "Gewinnmarge": 12.0,
        "ROIC": 7.0, "Umsatzwachstum": 4.0, "FCF Yield": 2.0,
    },
    "Real Estate": {
        "Bruttomarge": 52.0, "Op. Marge": 28.0, "Gewinnmarge": 18.0,
        "ROIC": 7.0, "Umsatzwachstum": 6.0, "FCF Yield": 3.0,
    },
    "Basic Materials": {
        "Bruttomarge": 28.0, "Op. Marge": 10.0, "Gewinnmarge": 7.0,
        "ROIC": 10.0, "Umsatzwachstum": 5.0, "FCF Yield": 4.0,
    },
}

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

# ==================== TECHNICAL INDICATOR HELPERS ====================
def compute_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(com=period - 1, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(com=period - 1, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))

def compute_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def compute_fibonacci(high: float, low: float):
    diff = high - low
    levels = {
        "0.0 %":   high,
        "23.6 %":  high - 0.236 * diff,
        "38.2 %":  high - 0.382 * diff,
        "50.0 %":  high - 0.500 * diff,
        "61.8 %":  high - 0.618 * diff,
        "78.6 %":  high - 0.786 * diff,
        "100.0 %": low,
    }
    return levels

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

# ==================== PIOTROSKI F-SCORE ====================
@st.cache_data(ttl=86400)
def load_piotroski(ticker: str):
    """Lädt Jahresabschlüsse und berechnet den Piotroski F-Score (0-9)."""
    try:
        stock = yf.Ticker(ticker)
        income  = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cash_flow
    except Exception:
        return None

    def _get(df, keys, col=0):
        if df is None or df.empty or col >= len(df.columns):
            return None
        for k in keys:
            if k in df.index:
                try:
                    v = df.loc[k].iloc[col]
                    return float(v) if pd.notna(v) else None
                except Exception:
                    pass
        return None

    # ── Jahreswerte holen ───────────────────────────────────────────────
    # Spalte 0 = aktuellstes Geschäftsjahr (T), Spalte 1 = Vorjahr (T-1)
    ta_t  = _get(balance, ["Total Assets"])
    ta_t1 = _get(balance, ["Total Assets"], 1)

    ni_t  = _get(income, ["Net Income"])
    ni_t1 = _get(income, ["Net Income"], 1)

    cfo_t  = _get(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    cfo_t1 = _get(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"], 1)

    rev_t  = _get(income, ["Total Revenue", "Revenue"])
    rev_t1 = _get(income, ["Total Revenue", "Revenue"], 1)

    gp_t   = _get(income, ["Gross Profit"])
    gp_t1  = _get(income, ["Gross Profit"], 1)

    ltd_t  = _get(balance, ["Long Term Debt", "Long-Term Debt"]) or 0
    ltd_t1 = _get(balance, ["Long Term Debt", "Long-Term Debt"], 1) or 0

    ca_t   = _get(balance, ["Current Assets",     "Total Current Assets"])
    ca_t1  = _get(balance, ["Current Assets",     "Total Current Assets"], 1)
    cl_t   = _get(balance, ["Current Liabilities","Total Current Liabilities"])
    cl_t1  = _get(balance, ["Current Liabilities","Total Current Liabilities"], 1)

    sh_t   = _get(balance, ["Ordinary Shares Number", "Share Issued", "Common Stock"])
    sh_t1  = _get(balance, ["Ordinary Shares Number", "Share Issued", "Common Stock"], 1)

    # ── Abgeleitete Kennzahlen ─────────────────────────────────────────
    roa_t   = ni_t  / ta_t  if ni_t  is not None and ta_t  and ta_t  > 0 else None
    roa_t1  = ni_t1 / ta_t1 if ni_t1 is not None and ta_t1 and ta_t1 > 0 else None
    cfo_ta  = cfo_t / ta_t  if cfo_t is not None and ta_t  and ta_t  > 0 else None

    # Leverage = LTD / Ø Total Assets
    avg_ta    = (ta_t + ta_t1) / 2 if ta_t and ta_t1 else ta_t
    avg_ta_t1 = (ta_t1 + (_get(balance, ["Total Assets"], 2) or ta_t1)) / 2
    lev_t   = ltd_t  / avg_ta    if avg_ta    and avg_ta    > 0 else None
    lev_t1  = ltd_t1 / avg_ta_t1 if avg_ta_t1 and avg_ta_t1 > 0 else None

    cr_t    = ca_t  / cl_t  if ca_t  and cl_t  and cl_t  > 0 else None
    cr_t1   = ca_t1 / cl_t1 if ca_t1 and cl_t1 and cl_t1 > 0 else None

    gm_t    = gp_t  / rev_t  if gp_t  is not None and rev_t  and rev_t  > 0 else None
    gm_t1   = gp_t1 / rev_t1 if gp_t1 is not None and rev_t1 and rev_t1 > 0 else None

    # Asset Turnover: Umsatz / Anfangsbestand Gesamtkapital (= TA Vorjahr)
    at_t  = rev_t  / ta_t1 if rev_t  and ta_t1 and ta_t1 > 0 else None
    ta_t2 = _get(balance, ["Total Assets"], 2)
    at_t1 = rev_t1 / ta_t2 if rev_t1 and ta_t2 and ta_t2 > 0 else (
            rev_t1 / ta_t1 if rev_t1 and ta_t1 and ta_t1 > 0 else None)

    fy_t  = balance.columns[0].year if not balance.empty else "T"
    fy_t1 = balance.columns[1].year if not balance.empty and len(balance.columns) > 1 else "T-1"

    # ── 9 Kriterien ────────────────────────────────────────────────────
    def _crit(name, group, passed, val_str, hint):
        return {"name": name, "group": group,
                "passed": passed, "value": val_str, "hint": hint}

    def _pct(v):
        return f"{v*100:.1f}%" if v is not None else "N/A"
    def _pp(v):
        return f"{v*100:+.1f}pp" if v is not None else "N/A"
    def _fmt(v):
        return fmt_large(v) if v is not None else "N/A"

    delta_roa = (roa_t - roa_t1)   if roa_t  is not None and roa_t1 is not None else None
    delta_lev = (lev_t - lev_t1)   if lev_t  is not None and lev_t1 is not None else None
    delta_cr  = (cr_t  - cr_t1)    if cr_t   is not None and cr_t1  is not None else None
    delta_gm  = (gm_t  - gm_t1)    if gm_t   is not None and gm_t1  is not None else None
    delta_at  = (at_t  - at_t1)    if at_t   is not None and at_t1  is not None else None

    share_chg = ((sh_t / sh_t1) - 1) if sh_t and sh_t1 and sh_t1 > 0 else None
    no_dilution = (sh_t <= sh_t1 * 1.01) if share_chg is not None else None

    criteria = [
        # ── Rentabilität ──
        _crit("ROA positiv",
              "Rentabilität",
              (roa_t > 0)       if roa_t  is not None else None,
              _pct(roa_t),
              f"ROA {fy_t}: {_pct(roa_t)} — Nettogewinn / Gesamtkapital > 0"),

        _crit("Operativer Cashflow > 0",
              "Rentabilität",
              (cfo_t > 0)       if cfo_t  is not None else None,
              _fmt(cfo_t),
              f"CFO {fy_t}: {_fmt(cfo_t)} — Operatives Geschäft generiert echten Cash"),

        _crit("ΔROA positiv",
              "Rentabilität",
              (delta_roa > 0)   if delta_roa is not None else None,
              _pp(delta_roa),
              f"ROA {fy_t}: {_pct(roa_t)} vs {fy_t1}: {_pct(roa_t1)} → {_pp(delta_roa)}"),

        _crit("Gewinnqualität (Accruals)",
              "Rentabilität",
              (cfo_ta > roa_t)  if cfo_ta is not None and roa_t is not None else None,
              f"CFO/TA {_pct(cfo_ta)} vs ROA {_pct(roa_t)}",
              "CFO/Gesamtkapital > ROA — Gewinne sind durch Cash gedeckt, nicht durch Bilanzierungstricks"),

        # ── Kapitalstruktur ──
        _crit("Verschuldung gesunken",
              "Kapitalstruktur",
              (delta_lev < 0)   if delta_lev is not None else None,
              _pp(delta_lev),
              f"LTD/Ø-Aktiva {fy_t}: {_pct(lev_t)} vs {fy_t1}: {_pct(lev_t1)} → {_pp(delta_lev)}"),

        _crit("Liquidität gestiegen",
              "Kapitalstruktur",
              (delta_cr > 0)    if delta_cr is not None else None,
              f"{delta_cr:+.2f}" if delta_cr is not None else "N/A",
              f"Current Ratio {fy_t}: {f'{cr_t:.2f}' if cr_t else 'N/A'} vs {fy_t1}: {f'{cr_t1:.2f}' if cr_t1 else 'N/A'}"),

        _crit("Keine Aktienverwässerung",
              "Kapitalstruktur",
              no_dilution,
              f"{share_chg*100:+.1f}%" if share_chg is not None else "N/A",
              "Keine neuen Aktien ausgegeben (≤1% Toleranz) — Schutz des Anteilswertes"),

        # ── Operative Effizienz ──
        _crit("Bruttomarge gestiegen",
              "Operative Effizienz",
              (delta_gm > 0)    if delta_gm is not None else None,
              _pp(delta_gm),
              f"Gross Margin {fy_t}: {_pct(gm_t)} vs {fy_t1}: {_pct(gm_t1)} → {_pp(delta_gm)}"),

        _crit("Asset Turnover gestiegen",
              "Operative Effizienz",
              (delta_at > 0)    if delta_at is not None else None,
              f"{delta_at:+.3f}" if delta_at is not None else "N/A",
              f"Umsatz/Anfangs-Aktiva {fy_t}: {f'{at_t:.3f}' if at_t else 'N/A'} vs {fy_t1}: {f'{at_t1:.3f}' if at_t1 else 'N/A'}"),
    ]

    score     = sum(1 for c in criteria if c["passed"] is True)
    available = sum(1 for c in criteria if c["passed"] is not None)

    return {
        "criteria": criteria,
        "score": score,
        "available": available,
        "fy_t":  fy_t,
        "fy_t1": fy_t1,
    }

# ==================== MOAT ANALYSIS ====================
def compute_moat(sector, industry, gross_margin, roic_val, operating_margin,
                 profit_margin, rev_growth, market_cap, debt, employees=None):
    ind = industry.lower()
    sec = sector.lower()

    # ── Moat-Treiber erkennen ──────────────────────────────────────────
    moat_types = []

    # Network Effects
    _net = ["internet", "social", "marketplace", "platform", "payment",
            "exchange", "gaming", "search", "e-commerce", "advertising"]
    if any(k in ind or k in sec for k in _net):
        moat_types.append(("🌐 Netzwerkeffekte",
            "Das Produkt wird wertvoller je mehr Nutzer es hat. Starker Verteidigungswall gegen Konkurrenz."))

    # Switching Costs
    _sw = ["software", "cloud", "saas", "data", "it service", "financial data",
           "information technology", "enterprise", "erp", "crm", "database"]
    if any(k in ind for k in _sw):
        moat_types.append(("🔒 Wechselkosten",
            "Kunden sind tief integriert — der Wechsel zu Konkurrenz ist teuer und riskant (Datenverlust, Schulungen, Kompatibilität)."))

    # Intangible Assets (Brands, Patents)
    _int = ["pharma", "biotech", "drug", "brand", "luxury", "beverage", "tobacco",
            "cosmetic", "media", "entertainment", "semiconductor", "aerospace"]
    if any(k in ind for k in _int):
        moat_types.append(("💡 Immaterielle Assets",
            "Patente, Marken oder Lizenzen schützen das Geschäftsmodell. Wettbewerber können das Produkt nicht einfach kopieren."))

    # Cost Advantages
    _cost = ["retail", "logistic", "transport", "shipping", "distribution",
             "mining", "steel", "commodity", "energy", "oil", "gas", "wholesale"]
    if any(k in ind for k in _cost):
        moat_types.append(("💰 Kostenvorteile",
            "Grosse Skalierung oder Zugang zu günstigen Ressourcen ermöglicht tiefere Preise als Konkurrenten."))

    # Efficient Scale (Natural Monopolies)
    _esc = ["utilit", "railroad", "airport", "infrastructure", "telecom",
            "water", "waste", "pipeline", "grid"]
    if any(k in ind or k in sec for k in _esc):
        moat_types.append(("⚖️ Effiziente Skalierung",
            "Natürliches Monopol oder regulierter Markt — ein zweiter Anbieter würde den Markt unrentabel machen."))

    # Falls keine Kategorie zutrifft, auf Margen basieren
    if not moat_types:
        if gross_margin and gross_margin > 55:
            moat_types.append(("💎 Preissetzungsmacht",
                "Aussergewöhnlich hohe Bruttomargen deuten auf Pricing Power und schwache Konkurrenz hin."))

    # ── Marktstruktur heuristisch ───────────────────────────────────────
    _mono = ["utilit", "railroad", "water supply", "postal"]
    _oligo = ["semiconductor", "aerospace", "defense", "integrated oil",
              "pharmaceutical", "auto", "airline", "wireless telecom"]
    _duo  = ["credit service", "payment process", "rating agency", "operating system"]

    if any(k in ind for k in _mono) or any(k in sec for k in ["utilities"]):
        market_structure = "Monopol / Reguliert"
        market_color = "#64b5f6"
    elif any(k in ind for k in _duo):
        market_structure = "Duopol"
        market_color = "#00e5ff"
    elif any(k in ind for k in _oligo):
        market_structure = "Oligopol"
        market_color = "#ffd600"
    else:
        market_structure = "Wettbewerb"
        market_color = "#90a4ae"

    # ── Burggraben-Breite ───────────────────────────────────────────────
    points = 0
    max_pts = 0

    def _chk(val, good, ok, w):
        nonlocal points, max_pts
        if val is None:
            return
        max_pts += w
        if val >= good:
            points += w
        elif val >= ok:
            points += w * 0.5

    _chk(gross_margin,    60, 40, 30)
    _chk(roic_val,        20, 10, 30)
    _chk(operating_margin,25, 15, 20)
    _chk(profit_margin,   15,  5, 10)
    _chk(rev_growth,      10,  3, 10)

    moat_score = round(points / max_pts * 100) if max_pts else 0

    # Bonus: bekannte Moat-Treiber vorhanden
    if len(moat_types) >= 2:
        moat_score = min(100, moat_score + 8)
    if len(moat_types) >= 1:
        moat_score = min(100, moat_score + 4)

    if moat_score >= 65:
        moat_width = "Wide Moat"
        moat_color = "#00e676"
        moat_icon  = "🏰"
        moat_desc  = "Breiter, nachhaltiger Wettbewerbsvorteil. Das Unternehmen kann voraussichtlich über 20+ Jahre überdurchschnittliche Renditen erwirtschaften."
    elif moat_score >= 35:
        moat_width = "Narrow Moat"
        moat_color = "#ffd600"
        moat_icon  = "🛡️"
        moat_desc  = "Schmaler Wettbewerbsvorteil. Vorteil vorhanden, aber Risiko der Erosion durch Technologie- oder Marktveränderungen."
    else:
        moat_width = "No Moat"
        moat_color = "#ff5252"
        moat_icon  = "⚠️"
        moat_desc  = "Kein klar erkennbarer struktureller Wettbewerbsvorteil. Margen und Renditen unter Druck durch Konkurrenz."

    return {
        "moat_width": moat_width,
        "moat_color": moat_color,
        "moat_icon":  moat_icon,
        "moat_desc":  moat_desc,
        "moat_score": moat_score,
        "moat_types": moat_types,
        "market_structure": market_structure,
        "market_color": market_color,
    }

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

# ==================== MAKRO DASHBOARD ====================
def _fred_last(series_id: str, n: int = 1) -> list[float]:
    """Gibt die letzten n gültigen Werte einer FRED-Zeitreihe zurück (kein API-Key nötig)."""
    try:
        r = requests.get(
            f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}",
            timeout=8,
        )
        if not r.ok:
            return []
        vals: list[float] = []
        for line in reversed(r.text.strip().split("\n")[1:]):
            parts = line.split(",")
            if len(parts) == 2 and parts[1].strip() not in (".", ""):
                try:
                    vals.append(float(parts[1].strip()))
                except ValueError:
                    pass
            if len(vals) >= n:
                break
        return vals
    except Exception:
        return []


@st.cache_data(ttl=3600)
def load_macro_data() -> dict:
    """Wechselkurse (yfinance) + Makro-Indikatoren (FRED, kein Key nötig)."""
    out: dict = {"fx": {}, "macro": {}}

    # ── Wechselkurse ──────────────────────────────────────────────────
    fx_map = {
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "USDJPY=X",
        "USD/CHF": "USDCHF=X",
        "GBP/USD": "GBPUSD=X",
        "USD/CNY": "USDCNY=X",
        "USD/CAD": "USDCAD=X",
    }
    for label, sym in fx_map.items():
        try:
            h = yf.Ticker(sym).history(period="2d", interval="1d")
            if len(h) >= 2:
                px   = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2])
                pct  = (px - prev) / prev * 100
            elif len(h) == 1:
                px, pct = float(h["Close"].iloc[-1]), 0.0
            else:
                continue
            out["fx"][label] = {"price": px, "pct": pct}
        except Exception:
            pass

    # ── US-Makro via FRED ──────────────────────────────────────────────
    # Inflation (CPI YoY berechnet aus CPIAUCSL)
    cpi = _fred_last("CPIAUCSL", 13)
    if len(cpi) >= 13:
        yoy = (cpi[0] / cpi[12] - 1) * 100
        out["macro"]["🇺🇸 Inflation"] = {"value": round(yoy, 1), "unit": "%"}

    # Arbeitslosigkeit
    unemp = _fred_last("UNRATE")
    if unemp:
        out["macro"]["🇺🇸 Arbeitslosigkeit"] = {"value": unemp[0], "unit": "%"}

    # Fed Funds Rate
    fed = _fred_last("FEDFUNDS")
    if fed:
        out["macro"]["🇺🇸 Fed Rate"] = {"value": fed[0], "unit": "%"}

    # 10J US-Staatsanleihe
    t10 = _fred_last("DGS10")
    if t10:
        out["macro"]["🇺🇸 10J Rendite"] = {"value": t10[0], "unit": "%"}

    # ── Eurozone via FRED ──────────────────────────────────────────────
    # HICP YoY (bereits in %)
    ez_cpi = _fred_last("CP0000EZ19M086NEST")
    if ez_cpi:
        out["macro"]["🇪🇺 Inflation"] = {"value": ez_cpi[0], "unit": "%"}

    # EZB Einlagesatz
    ecb = _fred_last("ECBDFR")
    if ecb:
        out["macro"]["🇪🇺 EZB Rate"] = {"value": ecb[0], "unit": "%"}

    # ── Japan / China (einfache Proxies) ──────────────────────────────
    jp_cpi = _fred_last("JPNCPIALLMINMEI", 13)
    if len(jp_cpi) >= 13:
        jp_yoy = (jp_cpi[0] / jp_cpi[12] - 1) * 100
        out["macro"]["🇯🇵 Inflation"] = {"value": round(jp_yoy, 1), "unit": "%"}

    # ── Buffett-Indikator: Wilshire 5000 Total Market Cap / US GDP ────
    try:
        # BOGZ1FL073164003Q = US total corporate equity market cap (millions USD, quarterly)
        _eq = _fred_last("BOGZ1FL073164003Q")
        _gdp = _fred_last("GDP")   # billions USD, quarterly
        if _eq and _gdp and _gdp[0]:
            _bi = round(_eq[0] / (_gdp[0] * 1000) * 100, 1)  # both in millions → %
            out["buffett"] = _bi
    except Exception:
        pass

    # ── S&P 500 PEG Ratio ─────────────────────────────────────────────
    try:
        _spy = yf.Ticker("SPY")
        _spy_info = _spy.info
        _sp_pe = _spy_info.get("trailingPE")
        _sp_eg = (_spy_info.get("earningsGrowth") or 0) * 100
        if _sp_pe and _sp_eg and _sp_eg > 0:
            out["sp500_peg"] = round(_sp_pe / _sp_eg, 2)
        elif _sp_pe:
            # Fallback: use 5-year avg earnings growth estimate (~7-8% for S&P 500)
            out["sp500_pe"] = round(_sp_pe, 1)
    except Exception:
        pass

    # ── Sektor-Heatmap via SPDR ETFs (MTD) ────────────────────────────
    _sector_etfs = {
        "Tech": "XLK", "Finanzen": "XLF", "Energie": "XLE",
        "Health": "XLV", "Konsum": "XLY", "Industrie": "XLI",
        "Komm.": "XLC", "Immo": "XLRE", "Rohst.": "XLB", "Versorger": "XLU",
    }
    _m_start = _dt.date.today().replace(day=1).strftime("%Y-%m-%d")
    _m_end   = _dt.date.today().strftime("%Y-%m-%d")
    sector_perf: dict = {}
    for _sname, _etf in _sector_etfs.items():
        try:
            _sh = yf.Ticker(_etf).history(start=_m_start, end=_m_end)
            if len(_sh) >= 2:
                sector_perf[_sname] = round(
                    (_sh["Close"].iloc[-1] / _sh["Close"].iloc[0] - 1) * 100, 1)
        except Exception:
            pass
    out["sectors"] = sector_perf

    # ── VIX ───────────────────────────────────────────────────────────
    try:
        _vix = yf.Ticker("^VIX").history(period="2d")
        if not _vix.empty:
            out["vix"] = round(float(_vix["Close"].iloc[-1]), 1)
    except Exception:
        pass

    # ── Markt-Sentiment (eigene Berechnung aus VIX + SPY-Momentum + MA) ──
    try:
        _today_str  = _dt.date.today().strftime("%Y-%m-%d")
        _y1_str     = (_dt.date.today() - _dt.timedelta(days=260)).strftime("%Y-%m-%d")
        _spy_h = yf.Ticker("SPY").history(start=_y1_str, end=_today_str)
        if len(_spy_h) >= 50:
            _spy_last  = float(_spy_h["Close"].iloc[-1])
            _spy_30d   = float(_spy_h["Close"].iloc[-22]) if len(_spy_h) >= 22 else _spy_last
            _spy_200ma = float(_spy_h["Close"].tail(200).mean())
            _mom_30d   = (_spy_last / _spy_30d - 1) * 100   # % 30-Tage-Momentum
            _above_200 = _spy_last > _spy_200ma

            # VIX-Komponente (0-40 Punkte, invertiert: niedriger VIX = mehr Gier)
            _vix_val = out.get("vix", 20)
            _vix_score = max(0, min(40, int((35 - _vix_val) / 35 * 40)))

            # Momentum-Komponente (0-35 Punkte)
            _mom_score = max(0, min(35, int((_mom_30d + 10) / 20 * 35)))

            # MA-Komponente (0-25 Punkte)
            _ma_score = 25 if _above_200 else 0

            _fg_score  = max(0, min(100, _vix_score + _mom_score + _ma_score))
            if _fg_score >= 75:   _fg_rating = "Extreme Greed"
            elif _fg_score >= 55: _fg_rating = "Greed"
            elif _fg_score >= 45: _fg_rating = "Neutral"
            elif _fg_score >= 25: _fg_rating = "Fear"
            else:                 _fg_rating = "Extreme Fear"
            out["fear_greed"] = {"score": _fg_score, "rating": _fg_rating}
    except Exception:
        pass

    return out


# ==================== INDICES + NEWS ====================
@st.cache_data(ttl=300)
def load_indices():
    symbols = {
        "S&P 500":     ("^GSPC",    "$"),
        "Dow Jones":   ("^DJI",     "$"),
        "Nasdaq":      ("^IXIC",    "$"),
        "DAX":         ("^GDAXI",   ""),
        "Nikkei 225":  ("^N225",    "¥"),
        "Hang Seng":   ("^HSI",     ""),
        "FTSE 100":    ("^FTSE",    ""),
        "Euro Stoxx":  ("^STOXX50E",""),
        "Bitcoin":     ("BTC-USD",  "$"),
        "Gold":        ("GC=F",     "$"),
    }
    result = {}
    for name, (sym, cur) in symbols.items():
        try:
            h = yf.Ticker(sym).history(period="2d", interval="1d")
            if len(h) >= 2:
                px = h["Close"].iloc[-1]
                prev = h["Close"].iloc[-2]
                chg = px - prev
                pct = chg / prev * 100
            elif len(h) == 1:
                px = h["Close"].iloc[-1]
                chg, pct = 0.0, 0.0
            else:
                continue
            result[name] = {"sym": sym, "price": px, "change": chg, "pct": pct, "cur": cur}
        except Exception:
            pass
    return result

@st.cache_data(ttl=600)
def load_market_news():
    headlines = []
    try:
        news = yf.Ticker("^GSPC").news or []
        for item in news[:6]:
            title = item.get("content", {}).get("title") or item.get("title", "")
            provider = (item.get("content", {}).get("provider", {}) or {}).get("displayName") or item.get("publisher", "")
            if title:
                headlines.append({"title": title, "source": provider})
        if not headlines:
            raise ValueError("empty")
    except Exception:
        pass
    if not headlines:
        try:
            news = yf.Ticker("SPY").news or []
            for item in news[:6]:
                title = item.get("content", {}).get("title") or item.get("title", "")
                provider = (item.get("content", {}).get("provider", {}) or {}).get("displayName") or item.get("publisher", "")
                if title:
                    headlines.append({"title": title, "source": provider})
        except Exception:
            pass
    return headlines[:4]


# ==================== STOCK PICKS ====================
_GROWTH_POOL = {
    "NVDA":  "KI-Chip-Marktführer mit explosivem Datencenter-Wachstum",
    "META":  "Social-Media-Gigant mit starker KI-Monetarisierung & Margenstärke",
    "AMZN":  "E-Commerce & Cloud (AWS) mit beschleunigtem Free-Cashflow",
    "CRWD":  "Cybersecurity-Leader mit hohem Anteil wiederkehrender SaaS-Erlöse",
    "NOW":   "ServiceNow – Enterprise-Workflow-KI mit >20 % ARR-Wachstum",
    "PLTR":  "Datenanalyse & KI-Plattform mit starkem US-Government-Momentum",
    "NFLX":  "Streaming-Leader mit wachsendem Werbeumsatz und Preissetzungsmacht",
    "UBER":  "Ride-Hailing & Delivery – erstmals profitabel mit FCF-Wachstum",
    "FICO":  "Kreditscoring-Monopol mit nachhaltiger Preissetzungsmacht",
    "APP":   "AppLovin – Mobile-Ad-Tech mit außergewöhnlichem Margenwachstum",
}
_VALUE_POOL = {
    "GOOGL": "Alphabet – KI-Leader mit günstigem Forward-KGV trotz Marktdominanz",
    "BRK-B": "Berkshire Hathaway – diversifizierter Qualitätskonzern mit riesigem Cash-Berg",
    "V":     "Visa – unerschütterliches Zahlungsnetzwerk mit über 50 % Nettomargen",
    "ASML":  "Halbleiter-Monopolist für EUV-Lithographie – kein echter Wettbewerber",
    "JNJ":   "Johnson & Johnson – Healthcare-Dividendenaristokrat mit breitem Moat",
    "BLK":   "BlackRock – weltgrößter Asset Manager mit stabilem Gebührenstrom",
    "UNH":   "UnitedHealth – diversifiziertes Gesundheitsunternehmen mit starkem Moat",
    "CB":    "Chubb – Versicherungskonzern mit herausragender Underwriting-Qualität",
    "ABBV":  "AbbVie – Pharma mit starker Pipeline nach Humira-Ablösung",
    "MSFT":  "Microsoft – Cloud-Plattform (Azure + Copilot) mit stabilem Dividendenwachstum",
}
# (ticker, description, estimated_div_growth_years)
_DIVIDEND_POOL = {
    "KO":  ("Coca-Cola – 62 Jahre konsekutive Dividendenerhöhungen, globaler Getränke-Moat", 62),
    "PG":  ("Procter & Gamble – 67 Jahre, breites Markenportfolio mit Preissetzungsmacht", 67),
    "PEP": ("PepsiCo – 52 Jahre, Food & Beverages mit globalem Vertriebsnetz", 52),
    "LOW": ("Lowe's – 61 Jahre, Heimwerker-Einzelhandel mit starkem Free-Cashflow", 61),
    "ADP": ("Automatic Data Processing – 49 Jahre, Payroll-Monopolist mit Netzwerkeffekten", 49),
    "ITW": ("Illinois Tool Works – 60 Jahre, diversifizierter Industriekonzern mit 80/20-Strategie", 60),
    "MCD": ("McDonald's – 48 Jahre, globales Franchise-Modell mit hohen Asset-Light-Margen", 48),
    "KMB": ("Kimberly-Clark – 52 Jahre, Konsumgüter mit stabilen Cashflows", 52),
    "AFL": ("Aflac – 41 Jahre, Krankenversicherung mit solidem Underwriting-Ergebnis", 41),
    "SYY": ("Sysco – 54 Jahre, größter US-Lebensmittelvertrieb mit starker Marktposition", 54),
    "CVX": ("Chevron – 37 Jahre, integrierter Ölkonzern mit diszipliniertem Kapitalrückfluss", 37),
    "JNJ": ("Johnson & Johnson – 62 Jahre, Healthcare-Gigant mit breitem Pharma- & MedTech-Moat", 62),
}

_OVERHYPED_POOL = {
    "TSLA":  "Tesla — extrem hohes KGV trotz verlangsamtem Wachstum & wachsender EV-Konkurrenz",
    "PLTR":  "Palantir — KUV >30x bei moderatem Wachstum, Bewertung diskonnektiert von Fundamentals",
    "SNOW":  "Snowflake — Wachstum verlangsamt, Cloud-Bewertung noch deutlich über Branchenniveau",
    "RIVN":  "Rivian — hohe Cash-Verbrennung, Verluste je produziertem Fahrzeug, Liquiditätsrisiko",
    "COIN":  "Coinbase — stark zyklisch, Kryptoabhängigkeit, Bewertung folgt Sentimentzyklen",
    "RBLX":  "Roblox — verlustreich trotz hoher User-Zahlen, fragliches Monetarisierungsmodell",
    "AI":    "C3.ai — Marketing-lastig, schwaches Umsatzwachstum bei anhaltend hoher KUV-Bewertung",
    "LCID":  "Lucid Motors — minimale Produktion, extrem hohe Burn Rate, unsichere Finanzierung",
    "BYND":  "Beyond Meat — Umsatz schrumpft, tiefe Verluste, Plant-Based-Hype deutlich verpufft",
    "PATH":  "UiPath — Wachstumsverlangsamung im RPA-Markt bei weiterhin ambitionierter Bewertung",
    "MSTR":  "MicroStrategy — kein operatives Kerngeschäft, reine Bitcoin-Wette mit Hebel-Risiko",
    "SMCI":  "Super Micro — Bilanzierungsprobleme, Delisting-Risiko, extrem hohe Kursvolatilität",
}

def _safe_div_yield(info: dict, price: float) -> float:
    """Berechnet Dividend Yield sauber aus trailingAnnualDividendRate / price."""
    annual = info.get("trailingAnnualDividendRate") or 0
    raw_dy = (info.get("dividendYield") or 0) * 100
    if annual and price and price > 0:
        computed = (annual / price) * 100
        dy = computed if (abs(computed - raw_dy) > 2 or raw_dy > 15) else raw_dy
    else:
        dy = raw_dy
    return min(dy, 25.0)  # cap at 25 %


# ── Qualitäts-Screener für Landing Page ───────────────────────────────────────
_SCREENER_WATCHLIST = [
    "AAPL","MSFT","GOOGL","META","AMZN","NVDA","AVGO",
    "CRM","ADBE","NOW","INTU","PANW","DDOG","MDB",
    "TSM","ASML","AMAT","AMD",
    "BRK-B","JPM","V","MA","AXP","SPGI","MCO",
    "LLY","NVO","UNH","TMO","ISRG","ABT",
    "COST","MCD","NKE","BKNG","CMG",
    "CAT","HON","LIN","ETN",
    "JNJ","PG","KO","WMT","HD",
    "MSCI","MELI","CPRT","FICO","ROP",
]

def _sc_score(info: dict) -> int:
    s = 0
    rg = info.get("revenueGrowth") or 0
    if rg > 0.20: s += 20
    elif rg > 0.10: s += 12
    elif rg > 0.03: s += 6
    gm = info.get("grossMargins") or 0
    if gm > 0.60: s += 20
    elif gm > 0.40: s += 12
    elif gm > 0.25: s += 6
    om = info.get("operatingMargins") or 0
    if om > 0.25: s += 15
    elif om > 0.15: s += 9
    elif om > 0.05: s += 4
    fcf = info.get("freeCashflow") or 0
    mkt = info.get("marketCap") or 1
    fcy = fcf / mkt if mkt else 0
    if fcy > 0.05: s += 15
    elif fcy > 0.02: s += 8
    elif fcy > 0: s += 4
    roe = info.get("returnOnEquity") or 0
    if roe > 0.25: s += 15
    elif roe > 0.15: s += 9
    elif roe > 0.08: s += 4
    de = info.get("debtToEquity") or 0
    if de < 30: s += 10
    elif de < 80: s += 5
    if (info.get("trailingEps") or 0) > 0: s += 5
    return min(s, 100)

def _sc_fair_value(info: dict) -> float | None:
    eps    = info.get("trailingEps") or 0
    rg_pct = (info.get("revenueGrowth") or 0) * 100
    fcf    = info.get("freeCashflow") or 0
    shares = info.get("sharesOutstanding") or 0
    graham = eps * (8.5 + 2 * rg_pct) if (eps > 0 and 0 < rg_pct <= 50) else None
    fcf_fv = (fcf * 20) / shares if (fcf > 0 and shares > 0) else None
    if graham and fcf_fv:
        return round(graham * 0.4 + fcf_fv * 0.6, 2)
    return round(graham or fcf_fv, 2) if (graham or fcf_fv) else None

@st.cache_data(ttl=14400, show_spinner=False)
def load_screener_data() -> list[dict]:
    """Screent ~50 Qualitätstitel; gecacht für 4 Stunden."""
    results = []
    for tkr in _SCREENER_WATCHLIST:
        try:
            info  = yf.Ticker(tkr).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not price:
                continue
            score = _sc_score(info)
            fv    = _sc_fair_value(info)
            if score >= 65 and fv and price < fv * 0.92:
                discount = (fv - price) / fv * 100
                results.append({
                    "ticker":   tkr,
                    "name":     (info.get("shortName") or tkr)[:28],
                    "price":    price,
                    "fv":       fv,
                    "discount": discount,
                    "score":    score,
                    "currency": info.get("currency", "USD"),
                    "sector":   info.get("sector", ""),
                })
        except Exception:
            pass
    results.sort(key=lambda x: x["score"] * x["discount"], reverse=True)
    return results[:8]


@st.cache_data(ttl=43200)
def load_stock_picks():
    growth_results, value_results, div_results, hype_results = [], [], [], []

    # ── Growth & Value ──────────────────────────────────────────────────
    for pool, results in [(_GROWTH_POOL, growth_results), (_VALUE_POOL, value_results)]:
        for t, desc in pool.items():
            try:
                info = yf.Ticker(t).info
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                fwd_pe = info.get("forwardPE")
                rev_growth = (info.get("revenueGrowth") or 0) * 100
                eps_growth = (info.get("earningsGrowth") or 0) * 100
                fcf = info.get("freeCashflow") or 0
                mktcap = info.get("marketCap") or 1
                fcf_yield = (fcf / mktcap * 100) if fcf else None
                roe = (info.get("returnOnEquity") or 0) * 100
                week52h = info.get("fiftyTwoWeekHigh") or price
                week52l = info.get("fiftyTwoWeekLow") or price
                w52_pos = ((price - week52l) / (week52h - week52l) * 100) if week52h > week52l else 50
                results.append({
                    "ticker": t, "name": info.get("shortName") or t, "desc": desc,
                    "price": price, "fwd_pe": fwd_pe,
                    "rev_growth": rev_growth, "eps_growth": eps_growth,
                    "fcf_yield": fcf_yield, "roe": roe, "w52_pos": w52_pos,
                })
            except Exception:
                pass

    # ── Dividend Aristocrats ────────────────────────────────────────────
    for t, (desc, div_years) in _DIVIDEND_POOL.items():
        try:
            info = yf.Ticker(t).info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            if not price:
                continue

            dy = _safe_div_yield(info, price)
            payout = (info.get("payoutRatio") or 0) * 100
            roe = (info.get("returnOnEquity") or 0) * 100
            fcf = info.get("freeCashflow") or 0
            mktcap = info.get("marketCap") or 1
            eps_growth = (info.get("earningsGrowth") or 0) * 100
            rev_growth = (info.get("revenueGrowth") or 0) * 100
            week52h = info.get("fiftyTwoWeekHigh") or price
            week52l = info.get("fiftyTwoWeekLow") or price
            w52_pos = ((price - week52l) / (week52h - week52l) * 100) if week52h > week52l else 50

            # ── Dividend Trap Checks ────────────────────────────────────
            trap_flags = []
            if dy > 8:
                trap_flags.append("Yield >8 %")
            if payout > 75 and payout < 200:
                trap_flags.append("Payout >75 %")
            if fcf < 0:
                trap_flags.append("FCF negativ")
            if eps_growth < -15:
                trap_flags.append("Gewinn rückläufig")
            if w52_pos < 15:
                trap_flags.append("Kurs nahe 52W-Tief")

            # Skip if 3+ trap flags (likely a value trap)
            if len(trap_flags) >= 3:
                continue

            # Quality filter: yield must be in meaningful range
            if dy < 1.0 or dy > 10.0:
                continue

            # Quality score: rewards yield, low payout, positive FCF, high ROE
            fcf_yield_val = (fcf / mktcap * 100) if fcf and mktcap else 0
            quality_score = (
                dy * 3
                + max(0, 70 - payout) * 0.3
                + max(0, roe) * 0.2
                + (5 if fcf > 0 else -5)
                + min(div_years, 60) * 0.1
            )

            div_results.append({
                "ticker": t, "name": info.get("shortName") or t, "desc": desc,
                "price": price, "div_yield": dy, "payout": payout,
                "div_years": div_years, "roe": roe, "fcf_yield": fcf_yield_val,
                "w52_pos": w52_pos, "quality_score": quality_score,
                "trap_flags": trap_flags,
            })
        except Exception:
            pass

    # ── Overhyped / Overvalued ──────────────────────────────────────────
    for t, desc in _OVERHYPED_POOL.items():
        try:
            info = yf.Ticker(t).info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            if not price:
                continue
            ps_ratio    = info.get("priceToSalesTrailing12Months")
            pe_ratio    = info.get("trailingPE") or info.get("forwardPE")
            fcf         = info.get("freeCashflow") or 0
            mktcap      = info.get("marketCap") or 1
            fcf_yield   = (fcf / mktcap * 100) if fcf else None
            short_float = (info.get("shortPercentOfFloat") or 0) * 100
            target      = info.get("targetMeanPrice")
            analyst_up  = ((target - price) / price * 100) if target and price else None
            week52h     = info.get("fiftyTwoWeekHigh") or price
            week52l     = info.get("fiftyTwoWeekLow") or price
            w52_pos     = ((price - week52l) / (week52h - week52l) * 100) if week52h > week52l else 50
            # Hype score: high P/S + high P/E + negative FCF + high short float
            hype_score = (
                (ps_ratio or 0) * 2
                + (min(pe_ratio, 200) if pe_ratio and pe_ratio > 0 else 50) * 0.3
                + (10 if fcf < 0 else 0)
                + short_float * 0.5
            )
            # Warning flags
            warn_flags = []
            if ps_ratio and ps_ratio > 10:  warn_flags.append(f"KUV {ps_ratio:.0f}x")
            if pe_ratio  and pe_ratio > 80:  warn_flags.append(f"KGV {pe_ratio:.0f}x")
            if fcf < 0:                      warn_flags.append("FCF negativ")
            if short_float > 10:             warn_flags.append(f"Short {short_float:.0f}%")
            if analyst_up is not None and analyst_up < -5:
                warn_flags.append(f"Über Analystenziel")
            hype_results.append({
                "ticker": t, "name": info.get("shortName") or t, "desc": desc,
                "price": price, "ps_ratio": ps_ratio, "pe_ratio": pe_ratio,
                "fcf_yield": fcf_yield, "short_float": short_float,
                "analyst_up": analyst_up, "w52_pos": w52_pos,
                "hype_score": hype_score, "warn_flags": warn_flags,
            })
        except Exception:
            pass

    growth_results.sort(key=lambda x: (x["rev_growth"] or 0) + (x["w52_pos"] or 0) * 0.3, reverse=True)
    value_results.sort(key=lambda x: (x["fcf_yield"] or 0) * 2 + (x["roe"] or 0) * 0.5, reverse=True)
    div_results.sort(key=lambda x: x["quality_score"], reverse=True)
    hype_results.sort(key=lambda x: x["hype_score"], reverse=True)
    return growth_results[:8], value_results[:8], div_results[:8], hype_results[:8]


# ==================== KI ANALYSE (Grok + Gemini Fallback) ====================

# Preferred model order — newest first, only verified stable names as fallback
_GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-1.5-flash",
]

@st.cache_data(ttl=86400)
def _discover_gemini_models(api_key: str) -> list[str]:
    """Fragt die ListModels-API ab und gibt generateContent-fähige Modelle zurück."""
    try:
        resp = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key},
            timeout=10,
        )
        if not resp.ok:
            return []
        available = {
            m["name"].replace("models/", "")
            for m in resp.json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
        }
        # Return preferred order filtered to what's actually available,
        # then append any other discovered models not in our list
        ordered = [m for m in _GEMINI_MODELS if m in available]
        extras  = sorted(available - set(_GEMINI_MODELS))
        return ordered + extras
    except Exception:
        return []


def _call_gemini(api_key: str, model: str,
                 messages: list, max_tokens: int, temperature: float) -> str:
    """Gemini native REST API — key als ?key= Parameter, kein Auth-Header."""
    system_parts = []
    contents = []
    for msg in messages:
        if msg["role"] == "system":
            system_parts.append({"text": msg["content"]})
        else:
            g_role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": g_role, "parts": [{"text": msg["content"]}]})

    body = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
    }
    if system_parts:
        body["systemInstruction"] = {"parts": system_parts}

    for api_ver in ("v1beta", "v1"):
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:generateContent",
            params={"key": api_key},
            headers={"Content-Type": "application/json"},
            json=body,
            timeout=60,
        )
        if resp.status_code == 404:
            continue
        if not resp.ok:
            raise ValueError(f"HTTP {resp.status_code}: {resp.text[:250]}")
        data = resp.json()
        candidate = data["candidates"][0]
        text = candidate["content"]["parts"][0]["text"]
        if candidate.get("finishReason") == "MAX_TOKENS":
            text += "\n\n⚠️ *(Antwort wurde durch Token-Limit abgeschnitten — bitte erneut versuchen)*"
        return text
    raise ValueError(f"Modell '{model}' in v1beta und v1 nicht gefunden")


def _try_gemini(messages: list, max_tokens: int,
                temperature: float, api_key: str) -> tuple[str, str]:
    """
    Versucht alle verfügbaren Gemini-Modelle (via ListModels + Fallback-Liste).
    Gibt (text, model_name) bei Erfolg oder ("", alle_fehler) zurück.
    """
    models = _discover_gemini_models(api_key) or _GEMINI_MODELS
    errors = []
    for model in models:
        try:
            text = _call_gemini(api_key, model, messages, max_tokens, temperature)
            return text, model
        except Exception as e:
            errors.append(f"{model}: {str(e)[:120]}")
    return "", " | ".join(errors) if errors else "Keine Modelle verfügbar"


def call_ki_api(system_prompt: str, user_message: str,
                gemini_key: str,
                max_tokens: int = 3500) -> tuple[str, str]:
    """Ruft Gemini an. Gibt (antwort_text, provider_label) zurück."""
    if not gemini_key:
        return ("⚠️ Kein API-Key konfiguriert. Bitte GEMINI_API_KEY "
                "in den Railway-Umgebungsvariablen setzen.", "")
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}]
    text, detail = _try_gemini(messages, max_tokens, 0.4, gemini_key)
    if text:
        return text, f"Gemini · {detail}"
    return (f"⚠️ KI-Anfrage fehlgeschlagen — {detail}", "")


def call_ki_chat(system_prompt: str, messages: list, gemini_key: str) -> str:
    """Chat-Modus via Gemini."""
    if not gemini_key:
        return "⚠️ Kein GEMINI_API_KEY konfiguriert."
    all_msgs = [{"role": "system", "content": system_prompt}] + messages
    text, detail = _try_gemini(all_msgs, 1800, 0.5, gemini_key)
    if text:
        return text
    return f"⚠️ Gemini nicht verfügbar — {detail}"



def build_grok_prompt(
    company_name, ticker, sector, industry,
    price, market_cap, quality_score,
    rev_growth, gross_margin, roic_val, fcf_yield,
    profit_margin, operating_margin, peg_ratio,
    rule_of_40, show_rule_of_40,
    net_cash_per_share, price_to_fcf, short_pct_float,
    total_shareholder_yield, dilution_pct,
    moat, piotroski,
    dcf_fair_val,
    insider_ownership=None, institutional_ownership=None,
) -> tuple[str, str]:
    """Baut System-Prompt und User-Message für die Grok-Analyse."""

    system = """Du bist ein erfahrener Aktienanalyst mit CFA-Zertifizierung und 20 Jahren Erfahrung.
Analysiere Aktien prägnant, ehrlich und auf Deutsch.

WICHTIG: Beurteile Kennzahlen immer relativ zum Sektor. Ein Industriekonzern (Siemens, BASF) mit 25% Bruttomargen kann einen starken Burggraben haben — verglichen mit NVIDIA (75%) ist das kein Versagen, sondern Branchennorm. Kapitalintensive Sektoren (Industrie, Energie, Materialien) haben systemisch niedrigere Margen als asset-light Technologie.

Strukturiere deine Antwort IMMER exakt so (Markdown-frei, nur diese fünf Abschnitte):

BULL CASE
- [Stärke 1 — quantitativ, mit Sektorbenchmark]
- [Stärke 2 — qualitativ: Patente / Marke / Kundenbindung / Netzwerkeffekte / Regulierung / Management]
- [Stärke 3 — weiterer struktureller Vorteil]

BEAR CASE
- [3 konkrete Risiken oder Schwächen, relativ zur Branche bewertet]

INVESTMENT THESE
[2-3 Sätze: Kernthese — warum kaufen oder nicht kaufen? Nenne explizit den Sektor-Kontext und ob die Kennzahlen für die Branche stark oder schwach sind.]

BEWERTUNG
[1-2 Sätze zum aktuellen Kurs vs. fairen Wert. Ergänze einen qualitativen Hinweis zu Moat-Faktoren die sich nicht aus Zahlen ablesen lassen (z.B. Patentschutz, langfristige Kundenverträge, Technologievorsprung).]

KI-EINFLUSS
[Kategorisiere in EINER Zeile: "🚀 KI-Profiteur", "⚠️ KI-Disruptionsrisiko", "⚡ Beides (ambivalent)" oder "➖ KI-neutral". Wichtig: SaaS- und Softwareunternehmen sind oft ambivalent — KI verbessert ihr Produkt, bedroht aber gleichzeitig ihr Geschäftsmodell durch KI-Agenten/Generalisten-Tools. Nenne konkret: (1) was durch KI gestärkt wird, (2) was durch KI bedroht ist, (3) ob das Management eine überzeugende KI-Strategie hat.]

ROT-FLAGS
- [maximal 3 klare Warnsignale — oder "Keine kritischen Warnsignale erkannt"]

SEGMENTE
[Schlüssle die wichtigsten Umsatzsegmente des Unternehmens auf. Format: "Segment — ca. X% des Umsatzes — kurze Einschätzung (wachsend/stabil/rückläufig)". Nenne 3-5 Hauptsegmente. Falls das Unternehmen kein klassisches Multi-Segment-Geschäft hat, beschreibe die wichtigsten Produktkategorien oder Regionen. Nutze dein Wissen über das Unternehmen — keine Erfindungen, aber auch kein "Daten nicht verfügbar".]

Hinweis am Ende: Schreib einen einzeiligen Satz dass quantitative Zahlen allein keine vollständige Moat-Analyse erlauben und Geschäftsberichte sowie Branchenexpertise empfohlen werden. Keine Anlageberatung.

Sei direkt. Vermeide Marketing-Floskeln. Wenn Daten fehlen, schreib kurz warum."""

    def _fmt(v, suffix="%", decimals=1):
        if v is None:
            return "N/A"
        return f"{v:.{decimals}f}{suffix}"

    mc_str = f"${market_cap/1e9:.1f}B" if market_cap else "N/A"
    dcf_str = f"${dcf_fair_val:.2f}" if dcf_fair_val else "N/A"
    moat_str = moat["moat_width"] if moat else "N/A"
    moat_types_str = ", ".join(t[0] for t in moat["moat_types"]) if moat and moat["moat_types"] else "keine erkannt"
    piotroski_str = f"{piotroski['score']}/{piotroski['available']}" if piotroski else "N/A"

    r40_line = f"Rule of 40: {_fmt(rule_of_40)}" if show_rule_of_40 else ""
    dilution_line = f"Verwässerung (5J): {_fmt(dilution_pct)}" if dilution_pct is not None else ""
    short_line = f"Short Interest: {_fmt(short_pct_float * 100 if short_pct_float else None)}" if short_pct_float else ""
    net_cash_line = f"Net Cash/Aktie: {_fmt(net_cash_per_share, suffix='$', decimals=2)}" if net_cash_per_share is not None else ""

    # Determine capital intensity for sector context
    _sec_l = (sector or "").lower()
    _ind_l = (industry or "").lower()
    _is_cap_int = any(k in _sec_l or k in _ind_l for k in [
        "industrial", "manufactur", "capital goods", "conglomerat", "materials",
        "mining", "steel", "chemical", "energy", "utilities", "oil", "gas", "infrastructure"])
    _is_fin = any(k in _sec_l for k in ["financial", "bank", "insurance"])
    _is_pharma = any(k in _sec_l or k in _ind_l for k in ["healthcare", "pharma", "biotech", "drug"])
    if _is_cap_int:
        _cap_ctx = ("Kapitalintensiver Sektor: Margen und ROIC sind strukturell niedriger als bei "
                    "Technologieunternehmen. Branchenübliche Benchmarks: Bruttomarge >30-40%, ROIC >10-12%. "
                    "Bitte Kennzahlen explizit im Sektorvergleich (nicht vs. Tech-Benchmarks) beurteilen.")
        _sector_peers = "Sektorpeers: andere Industriekonzerne / Kapitalgutkompanien"
    elif _is_fin:
        _cap_ctx = ("Finanzsektor: Margen nicht mit Industrie oder Tech vergleichbar. "
                    "Relevante Kennzahlen: ROE, Net Interest Margin, Cost-Income-Ratio. "
                    "Bitte branchenspezifisch beurteilen.")
        _sector_peers = "Sektorpeers: andere Banken / Versicherungen / Finanzdienstleister"
    elif _is_pharma:
        _cap_ctx = ("FuE-intensiver Sektor: hohe Bruttomarge (Patentschutz), aber massive Investitionen in "
                    "Forschung und klinische Studien drücken Nettomarge. Pipeline-Qualität und Patentlaufzeiten "
                    "entscheidend. Bitte explizit auf Patentschutz und Pipeline eingehen.")
        _sector_peers = "Sektorpeers: andere Pharma- / Biotech-Unternehmen"
    else:
        _cap_ctx = ("Asset-light / Technologiesektor: hohe Skalierbarkeit, niedrige Grenzkosten. "
                    "Margen und ROIC deutlich über Industriedurchschnitt normal. "
                    "Bitte auf technologischen Vorsprung und Plattform-Netzwerkeffekte eingehen.")
        _sector_peers = "Sektorpeers: andere Technologie- / Softwareunternehmen"

    user_msg = f"""Analysiere {company_name} ({ticker}):

STAMMDATEN
Sektor: {sector} | Branche: {industry}
Kurs: ${price:.2f} | Marktkapitalisierung: {mc_str}

BRANCHEN-KONTEXT
{_cap_ctx}
{_sector_peers}

QUALITÄT (relativ zu Sektornorm beurteilen)
Qualitäts-Score: {quality_score}/100
Bruttomarge: {_fmt(gross_margin)}
ROIC: {_fmt(roic_val)}
FCF Yield: {_fmt(fcf_yield)}
Gewinnmarge: {_fmt(profit_margin)}
Operative Marge: {_fmt(operating_margin)}
Umsatzwachstum: {_fmt(rev_growth)}
{r40_line}

BEWERTUNG
PEG Ratio: {_fmt(peg_ratio, suffix='x', decimals=2)}
Price/FCF: {_fmt(price_to_fcf, suffix='x', decimals=1)}
DCF Fair Value (konservativ): {dcf_str}
Total Shareholder Yield: {_fmt(total_shareholder_yield)}

BURGGRABEN
Moat-Breite: {moat_str}
Moat-Treiber (quantitativ): {moat_types_str}
Hinweis: Ergänze im Abschnitt BURGGRABEN-QUALITÄT qualitative Faktoren (Patente, Marke, Verträge, Management).

RISIKEN
Piotroski F-Score: {piotroski_str}
{dilution_line}
{short_line}

BILANZ
{net_cash_line}

MANAGEMENT (Proxy-Signale)
Insider-Ownership: {_fmt(insider_ownership * 100) if insider_ownership else "N/A"}
Institutionell: {_fmt(institutional_ownership * 100) if institutional_ownership else "N/A"}
Verwässerung (5J): {_fmt(dilution_pct) if dilution_pct is not None else "N/A"}

Gib deine Analyse gemäß der vorgegebenen Struktur. Schließe mit dem Abschnitt SEGMENTE ab — nutze dein allgemeines Wissen über {company_name}, da XBRL-Segmentdaten nicht immer verfügbar sind."""

    return system, user_msg


# ==================== SESSION ====================
if "ticker" not in st.session_state:
    st.session_state["ticker"] = ""
if "show_landing" not in st.session_state:
    st.session_state["show_landing"] = True
if "search_input" not in st.session_state:
    st.session_state["search_input"] = ""
if "search_msg" not in st.session_state:
    st.session_state["search_msg"] = ""
if "suggestions" not in st.session_state:
    st.session_state["suggestions"] = []
if "grok_analysis" not in st.session_state:
    st.session_state["grok_analysis"] = ""
if "grok_ticker" not in st.session_state:
    st.session_state["grok_ticker"] = ""
if "grok_provider" not in st.session_state:
    st.session_state["grok_provider"] = ""
if "grok_chat" not in st.session_state:
    st.session_state["grok_chat"] = []
if "grok_chat_ctx" not in st.session_state:
    st.session_state["grok_chat_ctx"] = ""
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []
if "show_wl_compare" not in st.session_state:
    st.session_state["show_wl_compare"] = False
if "sb_user" not in st.session_state:
    st.session_state["sb_user"] = None
if "sb_access_token" not in st.session_state:
    st.session_state["sb_access_token"] = ""
if "sb_auth_msg" not in st.session_state:
    st.session_state["sb_auth_msg"] = ""
if "wachstum_expanded" not in st.session_state:
    st.session_state["wachstum_expanded"] = None
if "seg_expanded" not in st.session_state:
    st.session_state["seg_expanded"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0

def _go_to_ticker(t):
    st.session_state["ticker"] = t
    st.session_state["show_landing"] = False
    st.session_state["search_input"] = t
    st.session_state["search_msg"] = ""
    st.session_state["active_tab"] = 0
    st.session_state["suggestions"] = []
    st.session_state["_open_sidebar"] = True

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <span style='font-size:2rem;'>📈</span>
        <div style='color:#64b5f6; font-size:1.3rem; font-weight:700; margin-top:6px;'>StocksMB</div>
        <div style='color:#37474f; font-size:0.75rem;'>Aktienanalyse Tool</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Smarte Suche mit Autofill
    search_raw = st.text_input(
        "Suche",
        value=st.session_state["search_input"],
        label_visibility="collapsed",
        placeholder="Ticker, Name, ISIN oder WKN…"
    )

    # Autofill: Live-Vorschläge ab 2 Zeichen (vor dem Suchen-Button)
    _sb_q = search_raw.strip()
    if len(_sb_q) >= 2:
        _sb_ac = search_by_name(_sb_q)
        if _sb_ac:
            for _s in _sb_ac[:5]:
                _lbl = f"{_s['ticker']} — {_s['name'][:24]}"
                if st.button(_lbl, use_container_width=True, key=f"sbac_{_s['ticker']}_{_sb_q}"):
                    _go_to_ticker(_s["ticker"])
                    st.rerun()

    search_btn = st.button("🔍 Suchen", use_container_width=True)

    if search_btn and _sb_q:
        with st.spinner("Suche…"):
            resolved, msg, sugg = resolve_search_input(search_raw)
        st.session_state["search_input"] = search_raw
        st.session_state["search_msg"] = msg
        st.session_state["suggestions"] = sugg
        if resolved:
            _go_to_ticker(resolved)
            st.rerun()

    if st.session_state["search_msg"]:
        st.markdown(f"<div style='color:#64b5f6; font-size:0.8rem; padding:6px 4px;'>{st.session_state['search_msg']}</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>⚡ Schnellauswahl</div>", unsafe_allow_html=True)
    quick = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "SAP"]
    cols = st.columns(2)
    for i, t in enumerate(quick):
        if cols[i % 2].button(t, use_container_width=True, key=f"q_{t}"):
            _go_to_ticker(t)
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if not st.session_state["show_landing"] and st.button("🏠 Startseite", use_container_width=True):
        st.session_state["show_landing"] = True
        st.rerun()

    st.markdown("<div class='section-header'>⚙️ Einstellungen</div>", unsafe_allow_html=True)
    show_peers = st.toggle("Peer-Vergleich anzeigen", value=True)
    show_insider = st.toggle("Insider-Transaktionen", value=True)
    show_dcf = st.toggle("DCF Rechner", value=True)

    # ── Konto ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🔐 Konto</div>", unsafe_allow_html=True)
    _sb_user = st.session_state.get("sb_user")
    if _sb_user:
        st.markdown(
            f"<div style='color:#64b5f6;font-size:0.78rem;padding:4px 0 6px 0;"
            f"word-break:break-all;'>👤 {_sb_user.get('email','')}</div>",
            unsafe_allow_html=True)
        if st.button("Abmelden", use_container_width=True, key="sb_logout"):
            st.session_state["sb_user"] = None
            st.session_state["sb_access_token"] = ""
            st.session_state["sb_auth_msg"] = ""
            st.session_state["watchlist"] = []
            st.rerun()
    else:
        _auth_tab_login, _auth_tab_reg = st.tabs(["Anmelden", "Registrieren"])
        with _auth_tab_login:
            _li_email = st.text_input("E-Mail", key="li_email", label_visibility="collapsed",
                                       placeholder="E-Mail")
            _li_pw    = st.text_input("Passwort", key="li_pw", type="password",
                                       label_visibility="collapsed", placeholder="Passwort")
            if st.button("Anmelden", use_container_width=True, key="li_btn"):
                with st.spinner("…"):
                    _data, _err = sb_login(_li_email.strip(), _li_pw)
                if _err:
                    st.session_state["sb_auth_msg"] = f"❌ {_err}"
                else:
                    st.session_state["sb_user"] = _data.get("user") or {}
                    st.session_state["sb_user"]["email"] = (_data.get("user") or {}).get("email", _li_email.strip())
                    st.session_state["sb_access_token"] = _data["access_token"]
                    st.session_state["sb_auth_msg"] = "✅ Angemeldet"
                    _loaded = sb_load_watchlist(_data["access_token"])
                    if _loaded:
                        _existing = {w["ticker"] for w in st.session_state["watchlist"]}
                        for _w in _loaded:
                            if _w["ticker"] not in _existing:
                                st.session_state["watchlist"].append(_w)
                    st.rerun()
        with _auth_tab_reg:
            _rg_email = st.text_input("E-Mail", key="rg_email", label_visibility="collapsed",
                                       placeholder="E-Mail")
            _rg_pw    = st.text_input("Passwort", key="rg_pw", type="password",
                                       label_visibility="collapsed", placeholder="Passwort (min. 6 Zeichen)")
            if st.button("Registrieren", use_container_width=True, key="rg_btn"):
                with st.spinner("…"):
                    _data, _err = sb_register(_rg_email.strip(), _rg_pw)
                if _err:
                    st.session_state["sb_auth_msg"] = f"❌ {_err}"
                else:
                    st.session_state["sb_auth_msg"] = "✅ Konto erstellt — bitte anmelden."
        if st.session_state.get("sb_auth_msg"):
            _msg_clr = "#00e676" if st.session_state["sb_auth_msg"].startswith("✅") else "#ff5252"
            st.markdown(
                f"<div style='font-size:0.75rem;color:{_msg_clr};padding:4px 0;'>"
                f"{st.session_state['sb_auth_msg']}</div>",
                unsafe_allow_html=True)

    # ── Watchlist ──────────────────────────────────────────────────────
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⭐ Watchlist</div>", unsafe_allow_html=True)
    _sb_wl = st.session_state.get("watchlist", [])
    if _sb_wl:
        for _w in list(_sb_wl):
            _wc1, _wc2 = st.columns([5, 1])
            with _wc1:
                if st.button(f"📈 **{_w['ticker']}** — {_w['name'][:18]}",
                             key=f"wl_nav_{_w['ticker']}", use_container_width=True):
                    _go_to_ticker(_w["ticker"])
                    st.rerun()
            with _wc2:
                if st.button("✕", key=f"wl_del_{_w['ticker']}", help="Entfernen"):
                    st.session_state["watchlist"] = [
                        x for x in st.session_state["watchlist"] if x["ticker"] != _w["ticker"]]
                    sb_remove_ticker(st.session_state.get("sb_access_token", ""), _w["ticker"])
                    st.rerun()
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        _cmp_lbl = "📊 Vergleich ausblenden" if st.session_state["show_wl_compare"] else "📊 Vergleich anzeigen"
        if st.button(_cmp_lbl, use_container_width=True, key="wl_toggle_cmp",
                     disabled=len(_sb_wl) < 2,
                     help="Mindestens 2 Aktien merken" if len(_sb_wl) < 2 else ""):
            st.session_state["show_wl_compare"] = not st.session_state["show_wl_compare"]
            st.rerun()
        if len(_sb_wl) < 2:
            st.caption("Mindestens 2 Aktien merken für Vergleich.")
    else:
        st.caption("Noch keine Aktien gemerkt — bei einer Aktie auf ⭐ Merken klicken.")

# ==================== LANDING PAGE ====================
if st.session_state["show_landing"]:
    st.markdown("""
    <div style="text-align:center; padding:48px 0 32px 0;">
        <div style="font-size:3rem; font-weight:800; color:#fff; letter-spacing:-1px;">
            📈 <span style="color:#00e5ff;">Stocks</span>MB
        </div>
        <div style="color:#64b5f6; font-size:1.1rem; margin-top:10px;">
            Professionelle Aktienanalyse — Ticker, Name, ISIN oder WKN eingeben
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Prominente Suche mit Autofill
    lc1, lc2, lc3 = st.columns([1, 3, 1])
    with lc2:
        landing_search = st.text_input(
            "Aktie suchen",
            label_visibility="collapsed",
            placeholder="z.B.  NVDA  ·  Siemens  ·  DE0007164600  ·  723610",
            key="landing_search_input"
        )

        # Autofill: Live-Vorschläge ab 2 Zeichen
        _ls = landing_search.strip()
        if len(_ls) >= 2:
            _ac_results = search_by_name(_ls)
            if _ac_results:
                for _s in _ac_results[:5]:
                    _lbl = f"**{_s['ticker']}** — {_s['name']}"
                    if _s.get('exchange'):
                        _lbl += f" · {_s['exchange']}"
                    if st.button(_lbl, key=f"ac_land_{_s['ticker']}_{_ls}", use_container_width=True):
                        _go_to_ticker(_s["ticker"])
                        st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        if st.button("🔍  Aktie analysieren", use_container_width=True, type="primary"):
            if _ls:
                with st.spinner("Suche…"):
                    resolved, msg, sugg = resolve_search_input(landing_search)
                if resolved:
                    _go_to_ticker(resolved)
                    st.rerun()
                elif sugg:
                    for _s in sugg[:5]:
                        if st.button(f"**{_s['ticker']}** — {_s['name']}", key=f"ac_land2_{_s['ticker']}", use_container_width=True):
                            _go_to_ticker(_s["ticker"])
                            st.rerun()
                else:
                    st.warning("Kein Ergebnis. Bitte Ticker oder Firmenname prüfen.")

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)

    # ── Marktüberblick ──
    st.markdown("<div class='section-header'>🌍 Marktüberblick</div>", unsafe_allow_html=True)
    with st.spinner("Lade Indizes…"):
        indices_data = load_indices()

    if indices_data:
        idx_cols = st.columns(len(indices_data))
        for col, (name, d) in zip(idx_cols, indices_data.items()):
            pct = d["pct"]
            clr = "#00e676" if pct >= 0 else "#ff5252"
            arrow = "▲" if pct >= 0 else "▼"
            px_str = f"{d['cur']}{d['price']:,.0f}"
            col.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:14px 8px; cursor:default;">
                <div class="metric-label" style="font-size:0.7rem;">{name}</div>
                <div style="color:#eceff1; font-size:1.05rem; font-weight:700; margin:4px 0;">{px_str}</div>
                <div style="color:{clr}; font-size:0.82rem; font-weight:600;">{arrow} {abs(pct):.2f}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Makro-Dashboard ───────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Makro-Dashboard</div>", unsafe_allow_html=True)
    with st.spinner("Lade Makrodaten…"):
        macro = load_macro_data()

    _FX_TIPS = {
        "EUR/USD": "Euro zu US-Dollar. Steigt der Wert, wird der Euro stärker (gut für europäische Importeure, schlecht für Exporteure).",
        "USD/JPY": "US-Dollar zu Japanischem Yen. Hohe Werte = schwacher Yen. Bank of Japan hält Zinsen historisch niedrig.",
        "USD/CHF": "US-Dollar zu Schweizer Franken. CHF gilt als sicherer Hafen — steigt oft in Krisenzeiten.",
        "GBP/USD": "Britisches Pfund zu US-Dollar (auch 'Cable' genannt). Sensitiv gegenüber UK-Wirtschaftsdaten.",
        "USD/CNY": "US-Dollar zu Chinesischem Yuan (Renminbi). Wichtig für globale Handelsdynamik und EM-Märkte.",
        "USD/CAD": "US-Dollar zu Kanadischem Dollar. Stark korreliert mit Ölpreisen (Kanada = großer Ölexporteur).",
    }
    _MACRO_TIPS = {
        "🇺🇸 Inflation":      "US-Verbraucherpreisindex (CPI) Jahr-über-Jahr. Zielwert der Fed: ~2 %. Über 3 % = restriktive Geldpolitik wahrscheinlich.",
        "🇺🇸 Arbeitslosigkeit":"US-Arbeitslosenquote (UNRATE). Unter 4 % gilt als Vollbeschäftigung. Niedrige Werte = starke Wirtschaft, aber auch Inflationsdruck.",
        "🇺🇸 Fed Rate":       "US-Leitzins (Federal Funds Rate). Bestimmt Kreditkosten weltweit. Hohe Zinsen belasten Wachstumsaktien stärker (höherer Diskontierungssatz).",
        "🇺🇸 10J Rendite":    "Rendite 10-jähriger US-Staatsanleihen. Wichtiger Benchmark für Bewertungen. Steigt die Rendite, sinken oft Aktienmultiples (KGV).",
        "🇪🇺 Inflation":      "Eurozone HICP (harmonisierter Verbraucherpreisindex) Jahr-über-Jahr. EZB-Zielwert: 2 %.",
        "🇪🇺 EZB Rate":       "EZB-Einlagesatz. Beeinflusst Kreditkosten in der Eurozone. Höhere Zinsen stärken tendenziell den Euro.",
        "🇯🇵 Inflation":      "Japan CPI Jahr-über-Jahr. Japan kämpfte jahrzehntelang mit Deflation. Steigende Inflation ermöglicht der BoJ Zinserhöhungen.",
    }

    if macro["fx"]:
        st.markdown("<div style='color:#546e7a; font-size:0.75rem; margin-bottom:6px;'>💱 Wechselkurse</div>",
                    unsafe_allow_html=True)
        fx_cols = st.columns(len(macro["fx"]))
        for col, (label, d) in zip(fx_cols, macro["fx"].items()):
            pct = d["pct"]
            clr = "#00e676" if pct >= 0 else "#ff5252"
            arrow = "▲" if pct >= 0 else "▼"
            _tip = _FX_TIPS.get(label, "")
            _tip_html = (f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                         f'<span class="tt-box">{_tip}</span></span>') if _tip else ""
            col.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:10px 6px;">
                <div class="metric-label" style="font-size:0.68rem;">{label}{_tip_html}</div>
                <div style="color:#eceff1; font-size:0.95rem; font-weight:700; margin:3px 0;">
                    {d['price']:.{4 if d['price'] < 10 else 2}f}
                </div>
                <div style="color:{clr}; font-size:0.75rem;">{arrow} {abs(pct):.2f}%</div>
            </div>""", unsafe_allow_html=True)

    if macro["macro"]:
        st.markdown("<div style='color:#546e7a; font-size:0.75rem; margin:10px 0 6px 0;'>🌐 Makro-Indikatoren</div>",
                    unsafe_allow_html=True)
        macro_items = list(macro["macro"].items())
        mc_cols = st.columns(len(macro_items))
        for col, (label, d) in zip(mc_cols, macro_items):
            val = d["value"]
            unit = d["unit"]
            if "Inflation" in label:
                clr = "#ff5252" if val > 3.0 else "#ffd600" if val > 2.0 else "#00e676"
            elif "Arbeitslosigkeit" in label:
                clr = "#ff5252" if val > 6.0 else "#ffd600" if val > 4.5 else "#00e676"
            else:
                clr = "#64b5f6"
            _tip = _MACRO_TIPS.get(label, "")
            _tip_html = (f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                         f'<span class="tt-box">{_tip}</span></span>') if _tip else ""
            col.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:10px 6px;">
                <div class="metric-label" style="font-size:0.68rem; line-height:1.3;">{label}{_tip_html}</div>
                <div style="color:{clr}; font-size:1.0rem; font-weight:700; margin:4px 0;">
                    {val:.1f}{unit}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Buffett-Indikator & S&P 500 PEG ──────────────────────────────
    _bi = macro.get("buffett")
    _sp_peg = macro.get("sp500_peg")
    _sp_pe  = macro.get("sp500_pe")
    if _bi or _sp_peg or _sp_pe:
        _bi_col, _peg_col = st.columns(2)

        if _bi:
            with _bi_col:
                if _bi < 75:   _bi_clr, _bi_lbl = "#00e676", "Unterbewertet"
                elif _bi < 90: _bi_clr, _bi_lbl = "#69f0ae", "Fair bewertet"
                elif _bi < 115:_bi_clr, _bi_lbl = "#ffd600", "Leicht überbewertet"
                elif _bi < 140:_bi_clr, _bi_lbl = "#ff8f00", "Überbewertet"
                else:          _bi_clr, _bi_lbl = "#ff5252", "Stark überbewertet"
                _bi_pct_bar = min(int(_bi / 200 * 100), 100)
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:#b0bec5;">Buffett-Indikator'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">Gesamte US-Marktkapitalisierung ÷ US-BIP. Buffett: "wahrscheinlich der beste Einzelindikator für Börsenbewertungen." Historischer Mittelwert: ~80–100%. Über 140% = Warnsignal.</span></span></span>'
                    f'<span style="color:{_bi_clr};font-weight:700;">{_bi:.0f}%</span></div>'
                    f'<div style="background:#0d1526;border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_bi_pct_bar}%;height:5px;border-radius:4px;background:{_bi_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>0%</span><span style="color:{_bi_clr};">{_bi_lbl}</span><span>200%</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;75% = günstig · 75–90% = fair · 90–115% = leicht teuer · &gt;115% = teuer · &gt;140% = Warnsignal</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        if _sp_peg or _sp_pe:
            with _peg_col:
                if _sp_peg:
                    if _sp_peg < 1.5:   _peg_clr, _peg_lbl = "#00e676", "Günstig"
                    elif _sp_peg < 2.0: _peg_clr, _peg_lbl = "#69f0ae", "Fair"
                    elif _sp_peg < 3.0: _peg_clr, _peg_lbl = "#ffd600", "Teuer"
                    else:               _peg_clr, _peg_lbl = "#ff5252", "Sehr teuer"
                    _peg_bar = min(int(_sp_peg / 5 * 100), 100)
                    _peg_display = f"PEG {_sp_peg:.2f}x"
                else:
                    _peg_clr, _peg_lbl, _peg_bar = "#64b5f6", f"KGV {_sp_pe:.0f}", 50
                    _peg_display = f"KGV {_sp_pe:.1f}x (kein EPS-Wachstum verfügbar)"
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:#b0bec5;">S&amp;P 500 PEG'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">KGV (trailing) ÷ Gewinnwachstum%. Berücksichtigt Wachstum — besser als reines KGV. Historisch fair: 1,5–2,0x. Unter 1,5x = günstig, über 3x = sehr teuer.</span></span></span>'
                    f'<span style="color:{_peg_clr};font-weight:700;">{_peg_display}</span></div>'
                    f'<div style="background:#0d1526;border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_peg_bar}%;height:5px;border-radius:4px;background:{_peg_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>0x</span><span style="color:{_peg_clr};">{_peg_lbl}</span><span>5x</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;1,5x = günstig · 1,5–2,0x = fair · 2–3x = teuer · &gt;3x = sehr teuer · Ø Hist: ~1,8x</div>'
                    f'</div>',
                    unsafe_allow_html=True)

    # ── Sektor-Heatmap + Sentiment ────────────────────────────────────
    _sh_col, _sent_col = st.columns([3, 2])

    with _sh_col:
        if macro.get("sectors"):
            st.markdown("<div style='color:#546e7a; font-size:0.75rem; margin:10px 0 6px 0;'>🗺️ Sektor-Performance (MTD)</div>",
                        unsafe_allow_html=True)
            _secs = macro["sectors"]
            _sorted_secs = sorted(_secs.items(), key=lambda x: x[1], reverse=True)
            _heat_cols = st.columns(len(_sorted_secs))
            for col, (sname, pct) in zip(_heat_cols, _sorted_secs):
                if pct >= 2:
                    bg, clr = "rgba(0,230,118,0.15)", "#00e676"
                elif pct >= 0.5:
                    bg, clr = "rgba(0,230,118,0.07)", "#69f0ae"
                elif pct >= -0.5:
                    bg, clr = "rgba(100,181,246,0.08)", "#90a4ae"
                elif pct >= -2:
                    bg, clr = "rgba(255,82,82,0.07)", "#ff8a65"
                else:
                    bg, clr = "rgba(255,82,82,0.15)", "#ff5252"
                arrow = "▲" if pct >= 0 else "▼"
                col.markdown(f"""
                <div style="background:{bg}; border:1px solid {clr}33; border-radius:6px;
                             text-align:center; padding:8px 4px;">
                    <div style="font-size:0.62rem; color:#546e7a; line-height:1.2;">{sname}</div>
                    <div style="color:{clr}; font-size:0.78rem; font-weight:700; margin-top:3px;">
                        {arrow}{abs(pct):.1f}%
                    </div>
                </div>""", unsafe_allow_html=True)

    with _sent_col:
        st.markdown("<div style='color:#546e7a; font-size:0.75rem; margin:10px 0 6px 0;'>😨 Markt-Sentiment</div>",
                    unsafe_allow_html=True)
        _vix = macro.get("vix")
        _fg  = macro.get("fear_greed", {})

        _has_sentiment = bool(_vix or _fg)

        if _vix:
            _vix_clr = "#ff5252" if _vix > 25 else "#ffd600" if _vix > 18 else "#00e676"
            _vix_lbl = "Hohe Volatilität" if _vix > 25 else "Moderat" if _vix > 18 else "Ruhig"
            _vix_pct = min(int(_vix / 50 * 100), 100)
            st.markdown(
                f'<div class="insight-box" style="padding:10px 14px 6px 14px; margin-bottom:6px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:4px;">'
                f'<span style="color:#b0bec5;">VIX<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                f'<span class="tt-box">CBOE Volatilitätsindex. Misst erwartete S&P-500-Schwankungen (30 Tage). Unter 15 = ruhig · 15–25 = moderat · über 25 = Angst/Unsicherheit.</span></span></span>'
                f'<span style="color:{_vix_clr};font-weight:700;">{_vix}</span></div>'
                f'<div style="background:#0d1526;border-radius:4px;height:5px;">'
                f'<div style="width:{_vix_pct}%;height:5px;border-radius:4px;background:{_vix_clr};"></div></div>'
                f'<div style="font-size:0.68rem;color:#546e7a;margin-top:2px;">{_vix_lbl}</div>'
                f'</div>',
                unsafe_allow_html=True)

        if _fg:
            _fs = _fg["score"]
            _fr = _fg.get("rating", "").replace("_", " ").title()
            _fg_clr = "#ff5252" if _fs < 25 else "#ffd600" if _fs < 45 else \
                      "#90a4ae" if _fs < 55 else "#ffd600" if _fs < 75 else "#00e676"
            st.markdown(
                f'<div class="insight-box" style="padding:10px 14px 6px 14px; margin-bottom:6px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:4px;">'
                f'<span style="color:#b0bec5;">Sentiment-Score<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                f'<span class="tt-box">Eigene Berechnung aus: VIX-Level (40%) + SPY 30-Tage-Momentum (35%) + SPY über 200-Tage-MA (25%). Kein CNN-Datenfeed.</span></span></span>'
                f'<span style="color:{_fg_clr};font-weight:700;">{_fs} — {_fr}</span></div>'
                f'<div style="background:#0d1526;border-radius:4px;height:5px;">'
                f'<div style="width:{_fs}%;height:5px;border-radius:4px;background:{_fg_clr};"></div></div>'
                f'</div>',
                unsafe_allow_html=True)

        if _has_sentiment:
            st.markdown('<div style="font-size:0.65rem;color:#37474f;margin-top:2px;">VIX: CBOE · Sentiment: eigene Berechnung (VIX + SPY-Momentum + 200-MA)</div>',
                        unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── Aktienempfehlungen Accordion ──
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    with st.expander("💡  Aktienideen — Growth · Value · Dividende · Overhyped  (täglich aktualisiert)", expanded=False):
        with st.spinner("Lade Aktienempfehlungen…"):
            _gp, _vp, _dp, _hp = load_stock_picks()

        def _badge(label, value, suffix="", fmt=".0f", color="#64b5f6"):
            if value is None or value == 0:
                return ""
            try:
                val_str = f"{value:{fmt}}{suffix}"
            except Exception:
                val_str = f"{value}{suffix}"
            return (f"<span style='background:rgba(100,181,246,0.1);color:{color};"
                    f"border-radius:5px;padding:2px 7px;font-size:0.71rem;"
                    f"font-weight:600;margin-right:4px;white-space:nowrap;'>"
                    f"{label}&thinsp;{val_str}</span>")

        def _trend_bar(pos, accent):
            pos = max(0, min(100, pos or 50))
            bar_clr = accent if pos > 62 else "#ffd600" if pos > 35 else "#ff5252"
            return (f"<div style='margin-top:7px;'>"
                    f"<div style='display:flex;justify-content:space-between;"
                    f"font-size:0.63rem;color:#37474f;margin-bottom:2px;'>"
                    f"<span>52W-Tief</span><span style='color:#546e7a;'>{pos:.0f}%</span>"
                    f"<span>52W-Hoch</span></div>"
                    f"<div style='background:#1e2d45;border-radius:4px;height:4px;'>"
                    f"<div style='background:{bar_clr};width:{pos}%;height:4px;"
                    f"border-radius:4px;transition:width 0.4s;'></div></div></div>")

        def _pick_card(s, accent, badges_html, extra_html=""):
            price_str = f"${s['price']:,.2f}" if s['price'] else "—"
            return f"""
            <div style='background:linear-gradient(135deg,#0d1f3c,#0a1628);
                 border:1px solid #1e3a5f;border-left:3px solid {accent};
                 border-radius:12px;padding:13px 15px;margin-bottom:10px;'>
              <div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px;'>
                <span style='color:{accent};font-size:1.02rem;font-weight:800;
                      letter-spacing:0.5px;'>{s["ticker"]}</span>
                <span style='color:#b0bec5;font-size:0.82rem;font-weight:600;'>{price_str}</span>
              </div>
              <div style='color:#546e7a;font-size:0.72rem;margin-bottom:5px;'>{s["name"]}</div>
              <div style='color:#90a4ae;font-size:0.78rem;line-height:1.45;margin-bottom:8px;'>{s["desc"]}</div>
              <div style='line-height:2;'>{badges_html}</div>
              {extra_html}
              {_trend_bar(s["w52_pos"], accent)}
            </div>"""

        # ── Zeile 1: Growth | Value ──────────────────────────────────────
        _col_g, _col_v = st.columns(2)

        with _col_g:
            st.markdown(
                "<div style='color:#00e5ff;font-size:0.82rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;"
                "padding-bottom:7px;border-bottom:1px solid rgba(0,229,255,0.2);'>"
                "🚀 Growth &amp; Momentum</div>",
                unsafe_allow_html=True)
            for s in _gp:
                b = (_badge("Rev▲", s["rev_growth"], "%", ".0f", "#00e676") +
                     _badge("EPS▲", s["eps_growth"], "%", ".0f", "#69f0ae") +
                     _badge("FCF", s["fcf_yield"], "%", ".1f", "#40c4ff"))
                st.markdown(_pick_card(s, "#00e5ff", b), unsafe_allow_html=True)

        with _col_v:
            st.markdown(
                "<div style='color:#a78bfa;font-size:0.82rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;"
                "padding-bottom:7px;border-bottom:1px solid rgba(124,58,237,0.3);'>"
                "💎 Value — Buffett-Style</div>",
                unsafe_allow_html=True)
            for s in _vp:
                b = (_badge("KGV", s["fwd_pe"], "x", ".1f", "#ce93d8") +
                     _badge("ROE", s["roe"], "%", ".0f", "#f48fb1") +
                     _badge("FCF", s["fcf_yield"], "%", ".1f", "#a5d6a7"))
                st.markdown(_pick_card(s, "#a78bfa", b), unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── Zeile 2: Dividende | Overhyped ───────────────────────────────
        _col_d, _col_h = st.columns(2)

        with _col_d:
            st.markdown(
                "<div style='color:#f59e0b;font-size:0.82rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;"
                "padding-bottom:7px;border-bottom:1px solid rgba(245,158,11,0.3);'>"
                "🏆 Dividend Aristocrats</div>",
                unsafe_allow_html=True)
            for s in _dp:
                trap_html = ""
                if s["trap_flags"]:
                    trap_html = (f"<div style='color:#ffd600;font-size:0.68rem;"
                                 f"margin-bottom:4px;'>⚠️ {', '.join(s['trap_flags'])}</div>")
                years_b = (
                    f"<span style='background:rgba(245,158,11,0.12);color:#fbbf24;"
                    f"border-radius:5px;padding:2px 7px;font-size:0.71rem;"
                    f"font-weight:600;margin-right:4px;'>{s['div_years']} Jahre▲</span>"
                )
                b = (years_b +
                     _badge("Yield", s["div_yield"], "%", ".1f", "#f59e0b") +
                     _badge("Payout", s["payout"] if s["payout"] > 0 else None, "%", ".0f", "#fca5a5"))
                st.markdown(_pick_card(s, "#f59e0b", b, trap_html), unsafe_allow_html=True)

        with _col_h:
            st.markdown(
                "<div style='color:#ff5252;font-size:0.82rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;"
                "padding-bottom:7px;border-bottom:1px solid rgba(255,82,82,0.3);'>"
                "🔥 Overhyped / Overvalued</div>",
                unsafe_allow_html=True)
            for s in _hp:
                warn_html = ""
                if s["warn_flags"]:
                    warn_html = (f"<div style='color:#ff5252;font-size:0.68rem;"
                                 f"margin-bottom:4px;'>🚨 {' · '.join(s['warn_flags'])}</div>")
                b = (_badge("KUV", s["ps_ratio"], "x", ".1f", "#ff5252") +
                     _badge("KGV", s["pe_ratio"] if s["pe_ratio"] and s["pe_ratio"] < 999 else None, "x", ".0f", "#ff7043") +
                     _badge("Short", s["short_float"] if s["short_float"] > 2 else None, "%", ".0f", "#ffd600"))
                if s["analyst_up"] is not None and s["analyst_up"] < 0:
                    b += _badge("Upside", s["analyst_up"], "%", ".0f", "#ef9a9a")
                st.markdown(_pick_card(s, "#ff5252", b, warn_html), unsafe_allow_html=True)

        st.markdown(
            "<div style='color:#37474f;font-size:0.68rem;text-align:center;margin-top:4px;'>"
            "⚠️ Keine Anlageberatung · Daten via Yahoo Finance · Aktualisierung alle 12 Std.</div>",
            unsafe_allow_html=True)

    # ── Qualitäts-Screener ─────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    with st.expander("🔍  Qualitäts-Screener — Score ≥ 65 & günstig unter Fair Value  (4h Cache)", expanded=False):
        with st.spinner("Screener läuft (~30 Sek. beim ersten Aufruf)…"):
            _sc_picks = load_screener_data()
        if not _sc_picks:
            st.info("Aktuell keine Aktien mit Score ≥ 65 gefunden, die ≥ 8 % unter Fair Value handeln.")
        else:
            st.markdown(
                "<div style='color:#546e7a;font-size:0.75rem;margin-bottom:8px;'>"
                f"<b>{len(_sc_picks)} Treffer</b> · Score ≥ 65 · Kurs ≥ 8 % unter geschätztem Fair Value · "
                "Sortiert nach Score × Discount</div>",
                unsafe_allow_html=True)
            for _sp in _sc_picks:
                _sp_cur  = _sp["currency"]
                _sp_disc = _sp["discount"]
                _sp_disc_clr = "#00e676" if _sp_disc >= 15 else "#ffd600" if _sp_disc >= 10 else "#90a4ae"
                _sp_score_clr = "#00e676" if _sp["score"] >= 80 else "#ffd600" if _sp["score"] >= 70 else "#90a4ae"
                st.markdown(f"""
                <div class="metric-card" style="padding:10px 14px;margin-bottom:8px;display:flex;
                     align-items:center;justify-content:space-between;gap:8px;">
                  <div style="min-width:52px;">
                    <div style="color:#eceff1;font-size:0.95rem;font-weight:700;">{_sp['ticker']}</div>
                    <div style="color:#546e7a;font-size:0.68rem;">{_sp.get('sector','')}</div>
                  </div>
                  <div style="flex:1;min-width:0;">
                    <div style="color:#90a4ae;font-size:0.78rem;white-space:nowrap;overflow:hidden;
                         text-overflow:ellipsis;">{_sp['name']}</div>
                  </div>
                  <div style="text-align:right;white-space:nowrap;">
                    <span style="color:{_sp_score_clr};font-size:0.82rem;font-weight:700;">
                      Score {_sp['score']}</span>
                    <span style="color:#546e7a;font-size:0.78rem;margin:0 6px;">·</span>
                    <span style="color:#b0bec5;font-size:0.78rem;">
                      {_sp['price']:.2f} {_sp_cur}</span>
                    <span style="color:#546e7a;font-size:0.78rem;margin:0 4px;">→ FV</span>
                    <span style="color:#64b5f6;font-size:0.78rem;">{_sp['fv']:.2f}</span>
                    <span style="color:{_sp_disc_clr};font-size:0.82rem;font-weight:700;margin-left:8px;">
                      -{_sp_disc:.1f}%</span>
                  </div>
                </div>""", unsafe_allow_html=True)
        st.markdown(
            "<div style='color:#37474f;font-size:0.68rem;text-align:center;margin-top:6px;'>"
            "⚠️ Vereinfachte Berechnung (Graham + FCF) · Kein Anlageberatung · Cache 4h</div>",
            unsafe_allow_html=True)

    # ── Top 10 pro Sektor ──────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    with st.expander("🌍  Top 10 Aktien pro Sektor — Global", expanded=False):
        _SECTOR_TOPS = {
            "💻 Tech": [
                ("AAPL","Apple","iPhone-Ökosystem & Services"),
                ("MSFT","Microsoft","Cloud (Azure) & KI-Plattform"),
                ("NVDA","Nvidia","KI-Chips & Datacenter"),
                ("TSM","TSMC","Weltgrößter Chip-Auftragsfertiger"),
                ("AVGO","Broadcom","Netzwerk-Chips & VMware"),
                ("ASML","ASML","Monopol Lithographie-Maschinen (EUV)"),
                ("ORCL","Oracle","Cloud-Datenbanken & ERP"),
                ("SAP","SAP","Enterprise-Software, Marktführer Europa"),
                ("ADBE","Adobe","Kreativ-Software & KI-Tools"),
                ("CRM","Salesforce","CRM-Plattform & KI-Agents"),
            ],
            "🏥 Health": [
                ("LLY","Eli Lilly","Marktführer GLP-1 Adipositas/Diabetes"),
                ("UNH","UnitedHealth","Größter US-Krankenversicherer"),
                ("NVO","Novo Nordisk","Ozempic/Wegovy — GLP-1 Pionier"),
                ("JNJ","J&J","Medizintechnik & Pharma-Dividende"),
                ("AZN","AstraZeneca","Onkologie & Atemwegsmedizin"),
                ("ABBV","AbbVie","Botox, Humira & Oncology Pipeline"),
                ("MRK","Merck & Co.","Keytruda — Immuntherapie-Marktführer"),
                ("TMO","Thermo Fisher","Life-Science Tools & CRO"),
                ("ISRG","Intuitive Surgical","Da Vinci Roboter-OP — Quasi-Monopol"),
                ("DHR","Danaher","Labor & Diagnostik Konglomerat"),
            ],
            "💰 Finance": [
                ("BRK-B","Berkshire","Buffetts Holding-Konglomerat"),
                ("JPM","JPMorgan","Größte US-Bank nach Assets"),
                ("V","Visa","Globales Zahlungsnetzwerk"),
                ("MA","Mastercard","Duopol Zahlungsabwicklung"),
                ("BAC","Bank of America","Universal-Bank mit Wealth Mgmt"),
                ("GS","Goldman Sachs","Investment Banking & Trading"),
                ("SPGI","S&P Global","Rating-Agentur & Finanzdaten"),
                ("MSCI","MSCI","Index-Anbieter & Analytics"),
                ("AXP","Amex","Premium-Kreditkarten & Rewards"),
                ("BX","Blackstone","Weltgrößter alternativer Asset Manager"),
            ],
            "🛒 Konsum": [
                ("AMZN","Amazon","E-Commerce & AWS Cloud"),
                ("MCD","McDonald's","Globale Franchise-Maschinerie"),
                ("COST","Costco","Mitgliedschaftsmodell & Loyalität"),
                ("HD","Home Depot","Nr. 1 Baumarkt USA"),
                ("NKE","Nike","Premium-Sportmarke global"),
                ("BKNG","Booking","Weltführer Online-Reisebuchung"),
                ("SBUX","Starbucks","Premium-Kaffeemarke global"),
                ("TJX","TJX","Off-Price Retail, resilientes Modell"),
                ("CMG","Chipotle","Wachstums-Fast-Casual-Restaurant"),
                ("ABNB","Airbnb","Plattform-Marktführer Kurzzeit-Mieten"),
            ],
            "📡 Komm.": [
                ("GOOGL","Alphabet","Google Search, YouTube, Cloud"),
                ("META","Meta","Facebook, Instagram, WhatsApp"),
                ("NFLX","Netflix","Streaming-Marktführer global"),
                ("DIS","Disney","Content, Parks & ESPN"),
                ("TMUS","T-Mobile US","Wachstumsstärkster US-Mobilfunker"),
                ("SPOT","Spotify","Audio-Streaming Marktführer"),
                ("VZ","Verizon","Stabiler Dividenden-Telko USA"),
                ("WBD","Warner Bros.","Max-Streaming & TV-Content"),
                ("NTES","NetEase","Gaming & Online-Dienste China"),
                ("SNAP","Snap","Junge Zielgruppe, AR-Fokus"),
            ],
            "🏭 Industrie": [
                ("CAT","Caterpillar","Bau- & Bergbaumaschinen global"),
                ("DE","John Deere","Landmaschinen & Precision Farming"),
                ("HON","Honeywell","Industrie-Automation & Aerospace"),
                ("RTX","RTX","Rüstung & Triebwerke (Pratt & Whitney)"),
                ("ETN","Eaton","Energiemanagement & Elektrifizierung"),
                ("GE","GE Aerospace","Flugzeugtriebwerke — Weltmarktführer"),
                ("UPS","UPS","Globales Logistik-Netzwerk"),
                ("ADP","ADP","Payroll & HR Software, Quasi-Monopol"),
                ("ITW","Illinois Tool","80 fokussierte Industrie-Divisionen"),
                ("PH","Parker Hannifin","Motion & Control Systems"),
            ],
            "⚡ Energie": [
                ("XOM","ExxonMobil","Größte westliche Öl-Gesellschaft"),
                ("CVX","Chevron","Integrierter Öl-Konzern USA"),
                ("SHEL","Shell","Europas größter Energie-Konzern"),
                ("TTE","TotalEnergies","Französischer Energie-Riese"),
                ("COP","ConocoPhillips","Effizienter US-Öl/Gas-Explorer"),
                ("EOG","EOG Resources","Effizienter US-Shale-Produzent"),
                ("SLB","SLB","Weltführer Öl-Services"),
                ("NEE","NextEra","Weltführer Wind & Solar-Energie"),
                ("ENB","Enbridge","Pipeline-Infrastruktur Nordamerika"),
                ("PSX","Phillips 66","Raffinerie & Midstream"),
            ],
            "🛡️ Basis": [
                ("PG","Procter & Gamble","Tide, Pampers, Gillette — Marken-Stärke"),
                ("KO","Coca-Cola","Getränke-Ikone, starke Dividende"),
                ("PEP","PepsiCo","Getränke + Frito-Lay Snacks"),
                ("WMT","Walmart","Weltgrößter Einzelhändler"),
                ("PM","Philip Morris","Iqos & Zyn — Rauchfrei-Transformation"),
                ("MDLZ","Mondelēz","Oreo, Milka & Cadbury"),
                ("CL","Colgate","Zahnpflege-Weltmarktführer"),
                ("UL","Unilever","Dove, Knorr — FMCG-Konzern"),
                ("COST","Costco","Mitgliedschaft-Loyalität & Wachstum"),
                ("MO","Altria","US-Tabak, hohe Dividendenrendite"),
            ],
            "🏗️ Material": [
                ("LIN","Linde","Industriegase-Weltmarktführer"),
                ("BHP","BHP Group","Bergbau-Riese: Eisenerz & Kupfer"),
                ("RIO","Rio Tinto","Eisenerz, Aluminium, Kupfer"),
                ("FCX","Freeport","Weltgrößter Kupfer-Miner"),
                ("NEM","Newmont","Größter Goldproduzent weltweit"),
                ("APD","Air Products","Wasserstoff & Industriegase"),
                ("SHW","Sherwin-Williams","Marktführer Farben USA"),
                ("ALB","Albemarle","Lithium-Produzent für E-Mobilität"),
                ("VALE","Vale","Brasiliens Eisenerz & Nickel-Riese"),
                ("NUE","Nucor","Effizienter US-Stahlproduzent"),
            ],
            "🏢 Immo": [
                ("PLD","Prologis","Logistik-REITs, Amazon-Lager"),
                ("AMT","American Tower","Mobilfunk-Türme global"),
                ("EQIX","Equinix","Weltführer Rechenzentren-REITs"),
                ("SPG","Simon Property","Premium-Einkaufszentren USA"),
                ("O","Realty Income","Monthly Dividend Company"),
                ("CCI","Crown Castle","US-Mobilfunk-Infrastruktur"),
                ("PSA","Public Storage","Self-Storage Nr. 1 USA"),
                ("WELL","Welltower","Seniorenwohnungen & Healthcare"),
                ("DLR","Digital Realty","Rechenzentren & Cloud-Infra"),
                ("AVB","AvalonBay","Premium-Appartements USA"),
            ],
        }

        _sec_tabs = st.tabs(list(_SECTOR_TOPS.keys()))
        for _stab, (_sec_name, _stocks) in zip(_sec_tabs, _SECTOR_TOPS.items()):
            with _stab:
                _sc1, _sc2 = st.columns(2)
                for _i, (_tk, _nm, _ds) in enumerate(_stocks):
                    _col = _sc1 if _i < 5 else _sc2
                    with _col:
                        st.markdown(
                            f"<div style='background:linear-gradient(135deg,#0d1f3c,#0a1628);"
                            f"border:1px solid #1e3a5f;border-radius:10px;"
                            f"padding:10px 13px;margin-bottom:8px;'>"
                            f"<div style='display:flex;justify-content:space-between;"
                            f"align-items:baseline;margin-bottom:2px;'>"
                            f"<span style='color:#64b5f6;font-size:0.95rem;font-weight:800;"
                            f"letter-spacing:0.4px;'>{_tk}</span>"
                            f"<span style='color:#546e7a;font-size:0.7rem;'>{_nm}</span>"
                            f"</div>"
                            f"<div style='color:#78909c;font-size:0.73rem;line-height:1.4;'>{_ds}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        if st.button(f"→ {_tk} analysieren", key=f"sec_{_sec_name}_{_tk}",
                                     use_container_width=True):
                            _go_to_ticker(_tk)
                            st.rerun()

    # ── Schlagzeilen ──
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📰 Aktuelle Marktschlagzeilen</div>", unsafe_allow_html=True)
    with st.spinner("Lade Nachrichten…"):
        headlines = load_market_news()

    if headlines:
        for h in headlines:
            src = f"<span style='color:#546e7a; font-size:0.72rem; margin-left:8px;'>{h['source']}</span>" if h['source'] else ""
            st.markdown(f"""
            <div class="metric-card" style="padding:14px 18px;">
                <div style="color:#eceff1; font-size:0.92rem; line-height:1.4;">📌 {h['title']}{src}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card" style="color:#546e7a; text-align:center;">Keine Nachrichten verfügbar</div>', unsafe_allow_html=True)

    # ── Schnellauswahl auf Landing ──
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⚡ Beliebte Aktien</div>", unsafe_allow_html=True)
    popular = [
        ("AAPL","Apple"), ("MSFT","Microsoft"), ("NVDA","NVIDIA"), ("AMZN","Amazon"),
        ("GOOGL","Alphabet"), ("META","Meta"), ("TSLA","Tesla"), ("SAP","SAP"),
    ]
    pop_cols = st.columns(len(popular))
    for col, (t, name) in zip(pop_cols, popular):
        if col.button(f"**{t}**\n{name}", use_container_width=True, key=f"lp_{t}"):
            _go_to_ticker(t)
            st.rerun()

    st.stop()

# ==================== MAIN DATA ====================
# Auto-open sidebar when navigating from landing page
if st.session_state.pop("_open_sidebar", False):
    components.html("""<script>
        var btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
        if (btn) { setTimeout(function(){ btn.click(); }, 300); }
    </script>""", height=0, width=0)

ticker = st.session_state["ticker"]

with st.spinner(f"Lade Daten für {ticker}..."):
    yf_info, hist, insider_df = load_yfinance(ticker)
    fmp_metrics, peers, analyst_data = load_fmp_metrics(ticker)
    hist_weekly, hist_monthly, share_history, splits_data = load_yfinance_extended(ticker)
    q_rev, q_net, q_eps = load_quarterly_financials(ticker)
    earnings_surprises   = load_earnings_surprises(ticker)
    a_rev, a_net, a_eps, a_fcf, a_shares, a_ebitda, a_capex, a_goodwill = load_annual_financials(ticker)
    # Segmentdaten: sec-api.io bevorzugt, FMP als Fallback
    _secapi_seg = load_secapi_segments(ticker) if SEC_API_KEY else {"product": [], "geo": []}
    _fmp_seg    = load_segment_data(ticker)
    seg_data = {
        "product": _secapi_seg["product"] or _fmp_seg["product"],
        "geo":     _secapi_seg["geo"]     or _fmp_seg["geo"],
    }

if hist.empty or not yf_info:
    st.markdown(f"""
    <div style="background:#0d1526; border:1px solid #ff5252; border-radius:14px; padding:32px 36px; margin:32px 0; text-align:center;">
        <div style="font-size:2.5rem; margin-bottom:12px;">🔍</div>
        <div style="color:#ff5252; font-size:1.3rem; font-weight:700; margin-bottom:10px;">Aktie nicht gefunden: <code>{ticker}</code></div>
        <div style="color:#78909c; font-size:0.9rem; line-height:1.7; margin-bottom:20px;">
            Mögliche Ursachen:<br>
            • Ticker falsch geschrieben (z.B. <strong>AAPL</strong> statt <em>Apple</em>)<br>
            • Europäische Aktien benötigen Börsen-Suffix: <strong>SAP.DE</strong>, <strong>NOVN.SW</strong>, <strong>ASML.AS</strong><br>
            • Japanische Aktien: 4-stellige Nummer + <strong>.T</strong> (z.B. <strong>7203.T</strong> für Toyota, <strong>6758.T</strong> für Sony)<br>
            • Delisted oder OTC-Aktie — yFinance hat keine Daten
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Zurück zur Startseite", key="err_back"):
        st.session_state["show_landing"] = True
        st.session_state["ticker"] = ""
        st.rerun()
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
# ── Dividend Yield Sanity-Check ──────────────────────────────────────────────
# yfinance sometimes delivers stale/wrong values. Recompute from annual rate.
_annual_div_rate = yf_info.get("trailingAnnualDividendRate") or 0
if _annual_div_rate and price and price > 0:
    _computed_yield = (_annual_div_rate / price) * 100
    # If the two sources differ a lot, trust the computed one
    if abs(_computed_yield - dividend_yield) > 2 or dividend_yield > 15:
        dividend_yield = _computed_yield
# Hard cap: yields above 25% are almost always data errors (ex-dividend artifact etc.)
if dividend_yield > 25:
    dividend_yield = 0.0
_div_yield_suspicious = dividend_yield > 15  # flag for display
shares_outstanding = yf_info.get("sharesOutstanding")
shares_float = yf_info.get("floatShares")
shares_short = yf_info.get("sharesShort")
short_ratio = yf_info.get("shortRatio")
pct_held_insider = yf_info.get("heldPercentInsiders")
pct_held_institutions = yf_info.get("heldPercentInstitutions")
trailing_eps = yf_info.get("trailingEps")
forward_eps = yf_info.get("forwardEps")
enterprise_value = yf_info.get("enterpriseValue")
ebitda = yf_info.get("ebitda")
ebitda_margin = (ebitda / revenue * 100) if (ebitda and revenue and revenue > 0) else None
ev_ebitda = (enterprise_value / ebitda) if (enterprise_value and ebitda and ebitda > 0) else None
week52_high = yf_info.get("fiftyTwoWeekHigh")
week52_low = yf_info.get("fiftyTwoWeekLow")
target_mean = yf_info.get("targetMeanPrice")
recommendation = yf_info.get("recommendationKey", "").replace("_", " ").title()
sector = yf_info.get("sector", "")
industry = yf_info.get("industry", "")

# Peer-Fallback: wenn FMP keine Peers liefert → Sektor-basierte Liste
if not peers and sector:
    peers = [t for t in SECTOR_PEERS_FALLBACK.get(sector, []) if t != ticker][:5]

# Logo: FMP Image-Endpoint (öffentlich, kein API-Key nötig)
logo_url = f"https://financialmodelingprep.com/image-stock/{ticker}.png"

# Rule of 40 nur für SaaS/Tech/Cyber relevant
show_rule_of_40 = is_saas_or_cyber(sector, industry)

# Verwässerung berechnen — aus Jahresabschluss (Diluted Average Shares), bereits split-bereinigt
dilution_pct = None
if not a_shares.empty and len(a_shares) >= 2:
    try:
        _sh = a_shares.sort_index()
        oldest = float(_sh.iloc[0])
        newest = float(_sh.iloc[-1])
        if oldest > 0:
            dilution_pct = (newest - oldest) / oldest * 100
    except Exception:
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
    yf_info.get("trailingPegRatio") or yf_info.get("pegRatio")
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

moat = compute_moat(sector, industry, gross_margin, roic_val, operating_margin,
                    profit_margin, rev_growth, market_cap, debt,
                    employees=yf_info.get("fullTimeEmployees"))

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
    <div style="display:flex; align-items:center; flex:1; min-width:0;">
        {logo_html}
        <div style="min-width:0; flex:1;">
            <div class="header-title" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{company_name}</div>
            <div class="header-sub">{ticker} · {sector} · {industry}</div>
            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                <span style="background:#1a2744; color:#64b5f6; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600;">{recommendation}</span>
                {'<span style="background:#1a2e1a; color:#00e676; border-radius:6px; padding:3px 10px; font-size:0.78rem; font-weight:600;">📅 Earnings: ' + earnings_date_str + '</span>' if earnings_date_str else ''}
            </div>
            <div style="margin-top:12px;">
                <div class="header-price" style="font-size:1.8rem; text-align:left;">${price:.2f}</div>
                <div class="{change_class}">{change_arrow} {abs(price_change):.2f} ({abs(price_change_pct):.2f}%)</div>
                {'<div style="color:#546e7a; font-size:0.78rem; margin-top:2px;">Ziel: $' + f'{target_mean:.2f}' + ' <span style="color:' + ('#00e676' if upside and upside > 0 else '#ff5252') + '">(' + ('+' if upside and upside > 0 else '') + f'{upside:.1f}%)' + '</span></div>' if upside else ''}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='color:#37474f;font-size:0.7rem;margin:-8px 0 10px 0;'>"
    "⏱ Kursdaten via Yahoo Finance · ca. 15–20 Min. verzögert · Keine Echtzeitkurse</div>",
    unsafe_allow_html=True)

# ── Watchlist-Button ──────────────────────────────────────────────
_wl_curr = st.session_state.get("watchlist", [])
_in_wl   = any(w["ticker"] == ticker for w in _wl_curr)
_wl_b1, _ = st.columns([1, 6])
with _wl_b1:
    if _in_wl:
        if st.button("✅ Gemerkt", key="wl_rm", help="Aus Watchlist entfernen"):
            st.session_state["watchlist"] = [w for w in _wl_curr if w["ticker"] != ticker]
            sb_remove_ticker(st.session_state.get("sb_access_token", ""), ticker)
            st.rerun()
    else:
        if st.button("⭐ Merken", key="wl_add", help="Zur Watchlist hinzufügen"):
            st.session_state["watchlist"] = _wl_curr + [{"ticker": ticker, "name": company_name}]
            _uid = (st.session_state.get("sb_user") or {}).get("id", "")
            sb_add_ticker(st.session_state.get("sb_access_token", ""), _uid, ticker, company_name)
            st.rerun()

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

_METRIC_TOOLTIPS = {
    "ROIC":              "Return on Invested Capital — Wie viel Gewinn erzielt das Unternehmen pro investiertem Kapital. >20% = exzellent, >10% = gut.",
    "FCF Yield":         "Free Cashflow Yield — FCF / Marktkapitalisierung. Zeigt, wie viel realen Cashflow man pro investiertem Euro erhält. >5% = attraktiv.",
    "Gross Margin":      "Bruttomarge — Umsatz minus direkte Herstellkosten. Hohe Marge (>60%) deutet auf Preissetzungsmacht hin.",
    "Rev. Growth":       "Umsatzwachstum (YoY) — Jährliches Wachstum des Umsatzes. >15% = stark, >5% = solide, <0% = schrumpfend.",
    "Rule of 40":        "SaaS-Kennzahl: Umsatzwachstum % + FCF-Marge % sollte ≥40 sein. Balanciert Wachstum und Profitabilität.",
    "PEG Ratio":         "Price/Earnings-to-Growth — KGV geteilt durch Gewinnwachstum. <1 = günstig, 1–2 = fair, >2 = teuer relativ zum Wachstum.",
    "Op. Margin":        "Operative Marge — Operatives Ergebnis / Umsatz. Misst die Effizienz des Kerngeschäfts. >20% = stark.",
    "Net Margin":        "Gewinnmarge — Nettogewinn / Umsatz. Zeigt, wie viel vom Umsatz als Reingewinn bleibt. >15% = ausgezeichnet.",
    "Qualitäts-Score":   "Gesamtbewertung basierend auf Marge, ROIC, Wachstum, FCF Yield und Bewertungskennzahlen. 0–100.",
    "P/E (trailing)":    "Kurs-Gewinn-Verhältnis (trailing) — Aktueller Kurs / Gewinn der letzten 12 Monate. Vergleich: S&P-500-Median ~22x.",
    "P/E (forward)":     "Kurs-Gewinn-Verhältnis (forward) — Aktueller Kurs / Gewinnschätzung nächstes Jahr. Niedriger als trailing = Gewinnwachstum erwartet.",
    "EV/EBITDA":         "Enterprise Value / EBITDA — Bewertungsmultiple unabhängig von Kapitalstruktur. <10x = günstig, >20x = teuer.",
    "Debt/Equity":       "Verschuldungsgrad — Fremdkapital / Eigenkapital. <1 = konservativ, >3 = hohes Risiko. Sektorabhängig.",
    "Beta":              "Markt-Sensitivität — Beta 1.0 = bewegt sich wie der Markt. >1 = volatiler, <1 = defensiver. Negativ = gegenläufig.",
    "Div. Yield":        "Dividendenrendite — Jährliche Dividende / Aktueller Kurs. >3% = attraktiv für Einkommensinvestoren.",
    "Dividend Yield":    "Dividendenrendite — Jährliche Dividende / Aktueller Kurs. >3% = attraktiv für Einkommensinvestoren.",
    "Payout Ratio":      "Ausschüttungsquote — Anteil des Gewinns, der als Dividende ausgezahlt wird. <60% = nachhaltig, >90% = potenziell gefährdet.",
    "Market Cap":        "Marktkapitalisierung — Aktienkurs × Anzahl Aktien. Micro <300M$, Small <2B$, Mid <10B$, Large <200B$, Mega >200B$.",
    "Short Float":       "Leerverkaufsquote — Anteil der verfügbaren Aktien, die aktuell leerverkauft sind. >20% = hohe Skepsis im Markt.",
    "52W Position":      "Position im 52-Wochen-Korridor — 0% = am Jahrestief, 100% = am Jahreshoch. Zeigt relativen Kursstand.",
    "Price/FCF":         "Kurs / Free Cashflow per Aktie. Niedriger als P/E ist ein gutes Zeichen (echte Cashgenerierung). <20x = fair.",
    "EPS Growth":        "Gewinn je Aktie Wachstum (YoY) — Zeigt, ob das Unternehmen profitabler wird. >15% = stark.",
    "Net Cash/Share":    "Netto-Cash je Aktie — (Cash - Schulden) / Aktienanzahl. Positiv = Netto-Gläubiger. Sicherheitspuffer bei Abschwüngen.",
}

def mini_card(label, value, good, ok, fmt=".1f", suffix="", inverse=False, tooltip=None):
    b = badge(value, good, ok, fmt, inverse)
    val_str = f"{value:{fmt}}{suffix}" if value is not None else "N/A"
    tip = tooltip or _METRIC_TOOLTIPS.get(label, "")
    tip_html = ""
    if tip:
        # Escape all HTML special chars to avoid breaking the card structure
        tip_safe = tip.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        tip_html = (
            f'<div class="mcard-tip-wrap">'
            f'<span class="mcard-tip-icon" tabindex="0">?</span>'
            f'<div class="mcard-tip-bubble">{tip_safe}</div>'
            f'</div>'
        )
    # Single-line HTML — no blank lines inside divs (avoids Streamlit markdown parser switching modes)
    return (
        f'<div class="metric-card" style="position:relative;">'
        f'{tip_html}'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{val_str}</div>'
        f'<div style="margin-top:6px;">{b}</div>'
        f'</div>'
    )

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

# ==================== WATCHLIST VERGLEICH ====================
if st.session_state.get("show_wl_compare") and len(st.session_state.get("watchlist", [])) >= 2:
    _wl_tickers = [w["ticker"] for w in st.session_state["watchlist"]]
    st.markdown("<div class='wl-compare-box'>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#00e5ff; font-size:1.0rem; font-weight:700; margin-bottom:14px;'>📊 Watchlist-Vergleich — {' · '.join(_wl_tickers)}</div>", unsafe_allow_html=True)

    with st.spinner("Lade Vergleichsdaten..."):
        _wl_data = {t: load_watchlist_metrics(t) for t in _wl_tickers}

    # ── Vergleichstabelle ──
    _cmp_rows = []
    for _t, _d in _wl_data.items():
        _cmp_rows.append({
            "Ticker":       _t,
            "Name":         _d.get("name", _t)[:22],
            "Kurs":         f"${_d['price']:.2f}" if _d.get("price") else "—",
            "Mkt Cap":      fmt_large(_d.get("mkt_cap")),
            "KGV":          f"{_d['pe']:.1f}x" if _d.get("pe") else "—",
            "Bruttomarge":  f"{_d['gm']:.1f}%",
            "Op. Marge":    f"{_d['op_mg']:.1f}%",
            "Nettomarge":   f"{_d['net_mg']:.1f}%",
            "Umsatzwachst.":f"{_d['rev_gr']:.1f}%",
            "FCF Yield":    f"{_d['fcf_y']:.1f}%",
            "ROE":          f"{_d['roe']:.1f}%",
        })
    st.dataframe(pd.DataFrame(_cmp_rows).set_index("Ticker"), use_container_width=True)

    # ── Vergleichs-Chart (5 Kernkennzahlen) ──
    _cmp_metrics = ["Bruttomarge", "Op. Marge", "Nettomarge", "Umsatzwachst.", "FCF Yield"]
    _cmp_keys    = ["gm",          "op_mg",     "net_mg",     "rev_gr",        "fcf_y"]
    _cmp_colors  = ["#00e5ff", "#a78bfa", "#00e676", "#ffd600", "#ff9100",
                    "#ff5252", "#64b5f6", "#69f0ae", "#ff80ab"]
    _fig_wl = go.Figure()
    for _i, (_t, _d) in enumerate(_wl_data.items()):
        _fig_wl.add_trace(go.Bar(
            name=_t,
            x=_cmp_metrics,
            y=[_d.get(k, 0) or 0 for k in _cmp_keys],
            marker_color=_cmp_colors[_i % len(_cmp_colors)],
            text=[f"{_d.get(k,0):.1f}%" for k in _cmp_keys],
            textposition="outside",
            textfont=dict(size=10),
        ))
    _fig_wl.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,21,38,0.8)",
        height=320,
        margin=dict(l=0, r=0, t=10, b=0),
        barmode="group",
        bargap=0.2,
        bargroupgap=0.06,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(showgrid=False, tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#1e2d45", ticksuffix="%", tickfont=dict(size=10)),
    )
    st.plotly_chart(_fig_wl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== KI-ANALYSE (GROK) ====================
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# Wenn Ticker wechselt, Analyse + Chat löschen
if st.session_state.get("grok_ticker") != ticker:
    st.session_state["grok_analysis"] = ""
    st.session_state["grok_ticker"] = ticker
    st.session_state["grok_provider"] = ""
    st.session_state["grok_chat"] = []
    st.session_state["grok_chat_ctx"] = ""

st.markdown('<div class="ki-cta-wrap">', unsafe_allow_html=True)
_col_btn, _col_hint = st.columns([2, 3])
with _col_btn:
    _run_grok = st.button("🤖  KI-Analyse starten", key="btn_grok",
                          use_container_width=True,
                          help="KI analysiert alle Kennzahlen und liefert Bull/Bear-Case, Investment-These und Risiko-Flags")
with _col_hint:
    if not GEMINI_API_KEY:
        st.caption("⚠️ Kein KI-Key gesetzt — GEMINI_API_KEY (Google AI Studio) in Railway-Umgebungsvariablen eintragen.")
    else:
        st.caption("Powered by Gemini (Google) · Analyse dauert ca. 5–15 Sekunden")
st.markdown('</div>', unsafe_allow_html=True)

if _run_grok:
    _dcf_for_grok = dcf_valuation(fcf, shares_outstanding,
                                   min(max(rev_growth or 3, 3), 30), 2.5, 10, 10)
    _piotroski_data = load_piotroski(ticker)
    with st.spinner("KI analysiert…"):
        _sys, _usr = build_grok_prompt(
            company_name=company_name, ticker=ticker,
            sector=sector, industry=industry,
            price=price, market_cap=market_cap,
            quality_score=quality_score,
            rev_growth=rev_growth, gross_margin=gross_margin,
            roic_val=roic_val, fcf_yield=fcf_yield,
            profit_margin=profit_margin, operating_margin=operating_margin,
            peg_ratio=peg_ratio, rule_of_40=rule_of_40,
            show_rule_of_40=show_rule_of_40,
            net_cash_per_share=net_cash_per_share,
            price_to_fcf=price_to_fcf,
            short_pct_float=short_pct_float,
            total_shareholder_yield=total_shareholder_yield,
            dilution_pct=dilution_pct,
            moat=moat, piotroski=_piotroski_data,
            dcf_fair_val=_dcf_for_grok,
            insider_ownership=pct_held_insider,
            institutional_ownership=pct_held_institutions,
        )
        _ki_text, _ki_provider = call_ki_api(_sys, _usr, GEMINI_API_KEY)
        st.session_state["grok_analysis"] = _ki_text
        st.session_state["grok_provider"] = _ki_provider
        st.session_state["grok_chat"] = []
        st.session_state["grok_chat_ctx"] = _usr

# Analyse anzeigen (bleibt bis Ticker-Wechsel)
if st.session_state.get("grok_analysis"):
    _raw = st.session_state["grok_analysis"]
    if _raw.startswith("⚠️"):
        # API-Fehler direkt als Warnung anzeigen
        st.warning(_raw)
    else:
        _sections = {
            "BULL CASE":        ("🟢", "#00e676"),
            "BEAR CASE":        ("🔴", "#ff5252"),
            "INVESTMENT THESE": ("💡", "#ffd600"),
            "BEWERTUNG":        ("⚖️", "#64b5f6"),
            "KI-EINFLUSS":      ("🤖", "#ce93d8"),
            "ROT-FLAGS":        ("⚠️", "#ff8f00"),
            "SEGMENTE":         ("🥧", "#4db6ac"),
        }
        _provider_label = st.session_state.get("grok_provider") or "KI"
        _html_parts = [
            f"<div class='grok-box'>"
            f"<div style='display:flex;align-items:center;gap:10px;margin-bottom:14px;'>"
            f"<span style='font-size:1.4rem;'>🤖</span>"
            f"<div><div style='color:#a78bfa;font-size:1.0rem;font-weight:700;'>KI-Analyse · {company_name}</div>"
            f"<div style='color:#546e7a;font-size:0.75rem;'>Powered by {_provider_label}</div>"
            f"</div></div>"
        ]
        _current_section = None
        _current_lines = []
        def _flush_section(sec, lines, parts, sections):
            if sec and lines:
                icon, color = sections.get(sec, ("📌", "#64b5f6"))
                parts.append(f"<div class='grok-section-title'>{icon} {sec}</div>")
                text = "\n".join(lines).strip()
                if text.startswith("-"):
                    bullet_items = [l.lstrip("- ").strip() for l in text.splitlines() if l.strip().startswith("-")]
                    parts.append("<ul>" + "".join(f"<li>{i}</li>" for i in bullet_items if i) + "</ul>")
                else:
                    parts.append(f"<p>{text}</p>")
        for _line in _raw.splitlines():
            _stripped = _line.strip()
            # Normalise: Gemini sometimes wraps headers in **bold** or adds ":"
            _normalised = _stripped.strip("*#: ").upper()
            # Check exact match first, then normalised
            _matched_sec = None
            if _stripped in _sections:
                _matched_sec = _stripped
            else:
                for _sk in _sections:
                    if _normalised == _sk.upper():
                        _matched_sec = _sk
                        break
            if _matched_sec:
                _flush_section(_current_section, _current_lines, _html_parts, _sections)
                _current_section = _matched_sec
                _current_lines = []
            elif _stripped:
                _current_lines.append(_stripped)
        _flush_section(_current_section, _current_lines, _html_parts, _sections)
        _html_parts.append("</div>")
        st.markdown("".join(_html_parts), unsafe_allow_html=True)

        # ── Chat-Modus (nur bei erfolgreicher Analyse) ────────────────
        st.markdown("""
        <div style='display:flex; align-items:center; gap:10px; margin:18px 0 6px 0;'>
            <div style='color:#a78bfa; font-size:0.95rem; font-weight:700;'>💬 Folgefragen an KI</div>
            <div style='color:#37474f; font-size:0.75rem;'>Stelle eigene Fragen zu {cn}</div>
        </div>
        """.replace("{cn}", company_name), unsafe_allow_html=True)

        # Chatverlauf rendern
        _chat_hist = st.session_state.get("grok_chat", [])
        if _chat_hist:
            _chat_html = ["<div class='chat-wrap'>"]
            for _msg in _chat_hist:
                if _msg["role"] == "user":
                    _chat_html.append(
                        f"<div class='chat-user-msg'><div class='chat-user-bubble'>{_msg['content']}</div></div>")
                else:
                    _chat_html.append(
                        f"<div class='chat-ai-msg'><div class='chat-ai-bubble'>{_msg['content']}</div></div>")
            _chat_html.append("</div>")
            st.markdown("".join(_chat_html), unsafe_allow_html=True)

        # Eingabe-Formular
        _peer_hint = peers[0] if peers else "Wettbewerber"
        with st.form("grok_chat_form", clear_on_submit=True):
            _fc1, _fc2, _fc3 = st.columns([5, 1, 1])
            with _fc1:
                _chat_q = st.text_input(
                    "", placeholder=f"z.B. 'Wie stark ist das Moat wirklich?' oder 'Vergleich mit {_peer_hint}'",
                    label_visibility="collapsed")
            with _fc2:
                _chat_send = st.form_submit_button("Senden →", use_container_width=True)
            with _fc3:
                _chat_clear = st.form_submit_button("Löschen", use_container_width=True)

        if _chat_clear:
            st.session_state["grok_chat"] = []
            st.rerun()

        if _chat_send and _chat_q.strip():
            _hist = st.session_state.get("grok_chat", [])
            _hist.append({"role": "user", "content": _chat_q.strip()})
            # Limit context to avoid oversized prompts (max 1500 chars)
            _ctx_raw = st.session_state.get("grok_chat_ctx", "")
            _ctx_trimmed = _ctx_raw[:1500] + ("…" if len(_ctx_raw) > 1500 else "")
            _chat_sys = (
                f"Du bist ein erfahrener Aktienanalyst und beantwortest Fragen zu {company_name} ({ticker}) auf Deutsch. "
                f"Antworte präzise, direkt und ohne Floskeln. Keine langen Einleitungen.\n\n"
                f"UNTERNEHMENSKONTEXT:\n{_ctx_trimmed}"
            )
            with st.spinner("KI denkt..."):
                _answer = call_ki_chat(_chat_sys, _hist[-6:], GEMINI_API_KEY)
            _hist.append({"role": "assistant", "content": _answer})
            st.session_state["grok_chat"] = _hist
            st.rerun()

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

# ── Chart-Detailansicht (Inline) ───────────────────────────────────────────
def _render_expanded_chart(tkr: str, metric: str, title: str,
                           color_pos: str, color_neg: str):
    """Kombinierter Chart: Balken = Absolutwerte, Linie = YoY-Wachstum %."""
    with st.spinner("Lade Daten…"):
        _ex_rev, _ex_net, _ex_eps, _ex_fcf, _ex_sh, _ex_price, _ex_ebitda = load_extended_financials(tkr, FMP_API_KEY)

    _map = {
        "revenue":        (_ex_rev,    lambda v: fmt_large(v), ""),
        "revenue_growth": (_ex_rev,    lambda v: fmt_large(v), ""),
        "net":            (_ex_net,    lambda v: fmt_large(v), ""),
        "net_growth":     (_ex_net,    lambda v: fmt_large(v), ""),
        "eps":            (_ex_eps,    lambda v: f"${v:.2f}",  ""),
        "fcf":            (_ex_fcf,    lambda v: fmt_large(v), ""),
        "fcf_growth":     (_ex_fcf,    lambda v: fmt_large(v), ""),
        "ebitda":         (_ex_ebitda, lambda v: fmt_large(v), ""),
        "ebitda_growth":  (_ex_ebitda, lambda v: fmt_large(v), ""),
        "shares":         (_ex_sh,     lambda v: f"{v/1e9:.2f}B", ""),
        "price":          (_ex_price,  None,                   "%"),
    }
    series, abs_fmt, _ = _map.get(metric, (_ex_rev, lambda v: fmt_large(v), ""))

    if series is None or series.empty or len(series) < 2:
        st.warning("Nicht genug Daten verfügbar.")
        return

    s = series.dropna()
    labels_abs = [str(d.year) if hasattr(d, "year") else str(d)[:4] for d in s.index]
    growth = s.pct_change() * 100
    growth_clean = growth.dropna()
    labels_g = [str(d.year) if hasattr(d, "year") else str(d)[:4] for d in growth_clean.index]
    bar_colors = [color_pos if v >= 0 else color_neg for v in s.values]
    line_colors = ["#00e676" if v >= 0 else "#ff5252" for v in growth_clean.values]

    _note = f" · {len(labels_abs)} Jahre" + ("" if FMP_API_KEY else " (ohne FMP_API_KEY: max. 4–5 Jahre)")
    st.caption(f"**{title}** — {tkr}{_note}")

    if metric == "price":
        fig = go.Figure(go.Bar(
            x=labels_abs, y=s.values,
            marker_color=["#00e676" if v >= 0 else "#ff5252" for v in s.values],
            text=[f"{v:+.1f}%" for v in s.values],
            textposition="outside", textfont=dict(size=12, color="#90a4ae"),
        ))
        fig.add_hline(y=0, line_color="#1e3a5f", line_width=1)
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)", height=420,
            margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
            yaxis=dict(ticksuffix="%", showgrid=True, gridcolor="#1e2d45"),
            xaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    abs_texts = [abs_fmt(v) for v in s.values] if abs_fmt else [str(v) for v in s.values]
    fig.add_trace(go.Bar(
        x=labels_abs, y=s.values, name=title, marker_color=bar_colors,
        text=abs_texts, textposition="outside",
        textfont=dict(size=11, color="#90a4ae"), opacity=0.85,
    ), secondary_y=False)
    if len(growth_clean) >= 1:
        fig.add_trace(go.Scatter(
            x=labels_g, y=growth_clean.values, name="YoY Wachstum %",
            mode="lines+markers+text", line=dict(color="#ffd600", width=2.5),
            marker=dict(size=8, color=line_colors, line=dict(color="#ffd600", width=1.5)),
            text=[f"{v:+.1f}%" for v in growth_clean.values],
            textposition="top center", textfont=dict(size=10, color="#ffd600"),
        ), secondary_y=True)
    fig.add_hline(y=0, line_color="#1e3a5f", line_width=1, secondary_y=False)
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,21,38,0.8)", height=460,
        margin=dict(l=10, r=60, t=30, b=10),
        legend=dict(orientation="h", y=1.08, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False),
    )
    fig.update_yaxes(showgrid=True, gridcolor="#1e2d45", secondary_y=False)
    fig.update_yaxes(ticksuffix="%", showgrid=False, title_text="YoY Wachstum %",
                     title_font=dict(color="#ffd600"), tickfont=dict(color="#ffd600"),
                     secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)


# ==================== NAVIGATION ====================
# Session-state-basierte Navigation (immun gegen st.rerun() und WebSocket-Reconnects)
_TABS = [
    "📊 Kennzahlen", "📈 Wachstum", "📋 Fundamental", "⚖️ Bewertung",
    "🔬 Piotroski", "🏰 Burggraben", "📉 Chart", "🔍 Insider", "📰 News",
]
_at = st.session_state.get("active_tab", 0)
_nav_cols = st.columns(len(_TABS))
for _ni, (_nc, _nl) in enumerate(zip(_nav_cols, _TABS)):
    if _nc.button(_nl, key=f"_nav_{_ni}", use_container_width=True,
                  type="primary" if _at == _ni else "secondary"):
        st.session_state["active_tab"] = _ni
        _at = _ni
st.markdown("<div style='border-top:2px solid #1e3a5f;margin:-6px 0 12px 0;'></div>",
            unsafe_allow_html=True)

if _at == 0:
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
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(mini_card("Profit Margin", profit_margin, 15, 5, ".1f", "%"), unsafe_allow_html=True)
    with c2:
        st.markdown(mini_card("Op. Margin", operating_margin, 20, 10, ".1f", "%"), unsafe_allow_html=True)
    with c3:
        st.markdown(mini_card("EBITDA Margin", ebitda_margin, 25, 12, ".1f", "%",
                              tooltip="EBITDA-Marge = EBITDA / Umsatz. Zeigt operative Profitabilität vor Zinsen, Steuern, Abschreibungen. >25% stark, >12% solide."), unsafe_allow_html=True)
    with c4:
        _ebitda_str = fmt_large(ebitda) if ebitda else "N/A"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">EBITDA</div>'
            f'<div class="metric-value">{_ebitda_str}</div>'
            f'<div style="margin-top:6px;"><span class="metric-badge-gray">absolut</span></div>'
            f'</div>',
            unsafe_allow_html=True)
    with c5:
        st.markdown(mini_card("EV/EBITDA", ev_ebitda, 0, 15, ".1f", "x", inverse=True,
                              tooltip="Enterprise Value / EBITDA — Bewertungsmultiple unabhängig von Kapitalstruktur & Steuern. <10x günstig, 10–20x fair, >20x teuer."), unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    _dy_c1, _dy_c2 = st.columns([1, 4])
    with _dy_c1:
        _dy_label = "Dividend Yield ⚠️" if _div_yield_suspicious else "Dividend Yield"
        _dy_tooltip = "Wert >15 % — bitte manuell prüfen (möglicher Datenfehler)" if _div_yield_suspicious else None
        st.markdown(mini_card(_dy_label, dividend_yield, 3, 1, ".2f", "%", tooltip=_dy_tooltip), unsafe_allow_html=True)

    # ── Branchenvergleich ──────────────────────────────────────────────
    st.markdown("<div class='section-header'>🌍 Branchenvergleich</div>", unsafe_allow_html=True)
    _bench = SECTOR_BENCHMARKS.get(sector)
    if _bench:
        _stock_vals = {
            "Bruttomarge":    gross_margin,
            "Op. Marge":      operating_margin,
            "Gewinnmarge":    profit_margin,
            "ROIC":           roic_val,
            "Umsatzwachstum": rev_growth,
            "FCF Yield":      fcf_yield,
        }
        _mnames  = list(_bench.keys())
        _svals   = [_stock_vals.get(m) for m in _mnames]
        _bvals   = [_bench[m] for m in _mnames]
        _colors  = []
        for _sv, _bv in zip(_svals, _bvals):
            if _sv is None:
                _colors.append("rgba(100,100,100,0.5)")
            elif _sv >= _bv * 1.1:
                _colors.append("#00e676")
            elif _sv >= _bv * 0.85:
                _colors.append("#ffd600")
            else:
                _colors.append("#ff5252")

        _fig_b = go.Figure()
        _fig_b.add_trace(go.Bar(
            name=ticker,
            y=_mnames,
            x=[v if v is not None else 0 for v in _svals],
            orientation="h",
            marker_color=_colors,
            text=[f"{v:.1f}%" if v is not None else "N/A" for v in _svals],
            textposition="outside",
            textfont=dict(size=11),
        ))
        _fig_b.add_trace(go.Bar(
            name=f"{sector} ∅",
            y=_mnames,
            x=_bvals,
            orientation="h",
            marker_color="rgba(100,181,246,0.2)",
            marker_line=dict(color="#64b5f6", width=1),
            text=[f"{v:.1f}%" for v in _bvals],
            textposition="outside",
            textfont=dict(size=11, color="#64b5f6"),
        ))
        _fig_b.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)",
            height=340,
            margin=dict(l=0, r=90, t=10, b=0),
            barmode="group",
            bargap=0.25,
            bargroupgap=0.08,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                        font=dict(size=11)),
            xaxis=dict(showgrid=True, gridcolor="#1e2d45", ticksuffix="%", tickfont=dict(size=10)),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        )
        st.plotly_chart(_fig_b, use_container_width=True)

        _above = [m for m, sv, bv in zip(_mnames, _svals, _bvals) if sv is not None and sv >= bv * 1.1]
        _below = [m for m, sv, bv in zip(_mnames, _svals, _bvals) if sv is not None and sv < bv * 0.85]
        if _above:
            st.markdown(f'<div class="insight-box">✅ <strong>Über Sektordurchschnitt ({sector}):</strong> {", ".join(_above)}</div>', unsafe_allow_html=True)
        if _below:
            st.markdown(f'<div class="insight-box">⚠️ <strong>Unter Sektordurchschnitt ({sector}):</strong> {", ".join(_below)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="insight-box">ℹ️ Keine Branchenbenchmarks für <strong>{sector or "unbekannter Sektor"}</strong> hinterlegt.</div>', unsafe_allow_html=True)

elif _at == 1:
    st.markdown("<div class='section-header'>Wachstum</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(mini_card("Revenue Growth", rev_growth, 15, 5, ".1f", "%"), unsafe_allow_html=True)
    with c2:
        st.markdown(mini_card("Earnings Growth", earnings_growth, 15, 5, ".1f", "%"), unsafe_allow_html=True)
    with c3:
        st.markdown(mini_card("FCF Yield", fcf_yield, 5, 2, ".1f", "%"), unsafe_allow_html=True)

    # ── Inline-Detailansicht (nach den Charts gerendert via Anchor) ──────────
    _exp = st.session_state.get("wachstum_expanded")

    def _show_chart(fig, metric_key, title, cp, cn, fallback_msg=None):
        """Zeigt Chart + Detailansicht-Button."""
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            if st.button("📊 Detailansicht", key=f"exp_{metric_key}",
                         use_container_width=True):
                st.session_state["wachstum_expanded"] = (metric_key, ticker, title, cp, cn)
        elif fallback_msg:
            st.markdown(f'<div class="insight-box" style="color:#546e7a;">{fallback_msg}</div>',
                        unsafe_allow_html=True)

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
            if st.button("📊 Detailansicht", key="exp_price", use_container_width=False):
                st.session_state["wachstum_expanded"] = ("price", ticker, "Jährliche Kursperformance", "#00e676", "#ff5252")

    # ── Jährliches Umsatz- & Gewinnwachstum ────────────────────────────
    st.markdown("<div class='section-header'>📊 Jährliches Fundamentalwachstum (5 Jahre)</div>",
                unsafe_allow_html=True)

    def _bar_chart(series: pd.Series, title: str, color_pos: str, color_neg: str,
                   is_growth: bool = True, value_fmt=None):
        if series.empty or len(series) < 2:
            return None
        s = series.tail(5)
        vals = s.pct_change().dropna() * 100 if is_growth else s
        suffix = "%" if is_growth else ""
        if vals.empty:
            return None
        labels = [str(d.year) if hasattr(d, "year") else str(d)[:4] for d in vals.index]
        colors = [color_pos if v >= 0 else color_neg for v in vals.values]
        text_vals = (
            [f"{v:+.1f}{suffix}" for v in vals.values] if is_growth
            else ([value_fmt(v) for v in vals.values] if value_fmt else [f"{v:.2f}" for v in vals.values])
        )
        fig = go.Figure(go.Bar(
            x=labels, y=vals.values,
            marker_color=colors,
            text=text_vals,
            textposition="outside",
            textfont=dict(size=11, color="#90a4ae"),
        ))
        fig.add_hline(y=0, line_color="#1e3a5f", line_width=1)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)",
            height=240,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False,
                       ticksuffix=suffix if is_growth else ""),
            xaxis=dict(showgrid=False),
            title=dict(text=title, font=dict(color="#64b5f6", size=13)),
        )
        return fig

    _gc1, _gc2 = st.columns(2)
    with _gc1:
        _show_chart(_bar_chart(a_rev, "Umsatzwachstum YoY", "#00e676", "#ff5252"),
                    "revenue_growth", "Umsatzwachstum YoY", "#00e676", "#ff5252",
                    "Keine Jahres-Umsatzdaten verfügbar.")
    with _gc2:
        _show_chart(_bar_chart(a_net, "Nettogewinnwachstum YoY", "#00e676", "#ff5252"),
                    "net_growth", "Nettogewinnwachstum YoY", "#00e676", "#ff5252",
                    "Keine Jahres-Gewinndaten verfügbar.")

    _gc3, _gc4 = st.columns(2)
    with _gc3:
        _show_chart(_bar_chart(a_rev, "Umsatz absolut", "#1565c0", "#1565c0",
                               is_growth=False, value_fmt=lambda v: fmt_large(v)),
                    "revenue", "Umsatz absolut", "#1565c0", "#1565c0")
    with _gc4:
        if not a_eps.empty and len(a_eps) >= 2:
            _show_chart(_bar_chart(a_eps, "EPS (Diluted) — Trend", "#00e5ff", "#ff5252",
                                   is_growth=False, value_fmt=lambda v: f"${v:.2f}"),
                        "eps", "EPS (Diluted)", "#00e5ff", "#ff5252")
        elif not a_net.empty:
            _show_chart(_bar_chart(a_net, "Nettogewinn absolut", "#64b5f6", "#ff5252",
                                   is_growth=False, value_fmt=lambda v: fmt_large(v)),
                        "net", "Nettogewinn absolut", "#64b5f6", "#ff5252")

    _gc5, _gc6 = st.columns(2)
    with _gc5:
        _show_chart(_bar_chart(a_fcf, "Free Cash Flow absolut", "#26a69a", "#ef5350",
                               is_growth=False, value_fmt=lambda v: fmt_large(v)),
                    "fcf", "Free Cash Flow absolut", "#26a69a", "#ef5350",
                    "Keine FCF-Daten verfügbar.")
    with _gc6:
        _show_chart(_bar_chart(a_fcf, "Free Cash Flow Wachstum YoY", "#00e676", "#ff5252"),
                    "fcf_growth", "FCF Wachstum YoY", "#00e676", "#ff5252")

    # EBITDA-Zeile
    _gc7, _gc8 = st.columns(2)
    with _gc7:
        _show_chart(_bar_chart(a_ebitda, "EBITDA absolut", "#7986cb", "#ef5350",
                               is_growth=False, value_fmt=lambda v: fmt_large(v)),
                    "ebitda", "EBITDA absolut", "#7986cb", "#ef5350",
                    "Keine EBITDA-Daten verfügbar.")
    with _gc8:
        _show_chart(_bar_chart(a_ebitda, "EBITDA Wachstum YoY", "#00e676", "#ff5252"),
                    "ebitda_growth", "EBITDA Wachstum YoY", "#00e676", "#ff5252")

    # ── Detailansicht (nach Charts, damit Scroll-Position passt) ──────────
    if _exp:
        _exp_metric, _exp_ticker, _exp_title, _exp_cp, _exp_cn = _exp
        # JS-Scroll zum Detail-Anker
        components.html(
            '<script>setTimeout(()=>{'
            'const el=window.parent.document.getElementById("wachstum-detail");'
            'if(el)el.scrollIntoView({behavior:"smooth",block:"start"});'
            '},150);</script>', height=0)
        st.markdown('<div id="wachstum-detail"></div>', unsafe_allow_html=True)
        st.markdown("---")
        _cl, _tl = st.columns([1, 7])
        with _cl:
            if st.button("✕ Schließen", key="close_wachstum_expanded"):
                st.session_state["wachstum_expanded"] = None
                st.rerun()
        with _tl:
            st.markdown(
                f"<h4 style='color:#64b5f6;margin:4px 0;'>📊 {_exp_title} — Detailansicht</h4>",
                unsafe_allow_html=True)
        _render_expanded_chart(_exp_ticker, _exp_metric, _exp_title, _exp_cp, _exp_cn)
        st.markdown("---")

    # ── Segment-Aufschlüsselung ────────────────────────────────────────
    st.markdown("<div class='section-header'>🥧 Umsatz nach Segment</div>", unsafe_allow_html=True)
    _seg_colors = ["#00e5ff","#a78bfa","#00e676","#ffd600","#ff5252",
                   "#f59e0b","#64b5f6","#f48fb1","#69f0ae","#ce93d8",
                   "#4db6ac","#ef9a9a","#80cbc4","#ffcc80","#90a4ae"]

    def _seg_charts(entries: list, sublabel: str, expanded: bool = False):
        """Zeigt Donut (letztes Jahr) + gestapeltes Balkendiagramm (Zeitreihe)."""
        if not entries:
            return
        latest = entries[-1]
        segs = {k: v for k, v in latest["segments"].items() if v > 0}
        if not segs:
            return
        # Merge segment names consistent across all years (use latest as reference)
        all_names = list(segs.keys())
        total = sum(segs.values())
        clrs  = _seg_colors[:len(all_names)]
        yrs_label = f"{entries[0]['date']}–{entries[-1]['date']}" if len(entries) > 1 else entries[-1]["date"]
        st.caption(f"**{sublabel}** — Letztes Jahr: {latest['date']} · {len(entries)} Jahre verfügbar")
        chart_h = 380 if expanded else 300

        _sc1, _sc2 = st.columns([1, 2] if expanded else [1, 1])
        with _sc1:
            fig_donut = go.Figure(go.Pie(
                labels=all_names, values=[segs[n] for n in all_names], hole=0.52,
                marker=dict(colors=clrs, line=dict(color="#0a1628", width=2)),
                textinfo="label+percent", textfont=dict(size=11 if expanded else 10),
                hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
                customdata=[fmt_large(segs[n]) for n in all_names],
            ))
            fig_donut.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                height=chart_h, margin=dict(l=0, r=0, t=10, b=0),
                showlegend=True, legend=dict(font=dict(size=10), bgcolor="rgba(0,0,0,0)"),
                annotations=[dict(text=fmt_large(total), x=0.5, y=0.5,
                                  font=dict(size=14, color="#b0bec5"), showarrow=False)],
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        with _sc2:
            if len(entries) >= 2:
                years = [e["date"] for e in entries]
                fig_stk = go.Figure()
                for i, seg_name in enumerate(all_names):
                    fig_stk.add_trace(go.Bar(
                        name=seg_name, x=years,
                        y=[e["segments"].get(seg_name, 0) for e in entries],
                        marker_color=_seg_colors[i % len(_seg_colors)],
                        hovertemplate=f"<b>{seg_name}</b><br>%{{y:,.0f}}<extra></extra>",
                    ))
                fig_stk.update_layout(
                    barmode="stack", template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,21,38,0.8)",
                    height=chart_h, margin=dict(l=0, r=0, t=10, b=10),
                    legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)",
                                orientation="h", yanchor="bottom", y=1.02),
                    yaxis=dict(showgrid=True, gridcolor="#1e2d45"),
                    xaxis=dict(showgrid=False),
                    title=dict(text=yrs_label if expanded else "",
                               font=dict(color="#64b5f6", size=11)),
                )
                st.plotly_chart(fig_stk, use_container_width=True)
            else:
                st.caption("Nur 1 Jahr — kein Trend darstellbar.")

    # ── Inline-Segment-Detailansicht ─────────────────────────────────────
    _seg_exp = st.session_state.get("seg_expanded")
    if _seg_exp:
        _seg_type, _seg_label = _seg_exp
        _seg_all = seg_data.get(_seg_type, [])
        if _seg_all:
            st.markdown("---")
            _slc, _stl = st.columns([1, 7])
            with _slc:
                if st.button("✕ Schließen", key="close_seg_exp"):
                    st.session_state["seg_expanded"] = None
            with _stl:
                st.markdown(
                    f"<h4 style='color:#64b5f6;margin:4px 0;'>🥧 {_seg_label} — alle {len(_seg_all)} Jahre</h4>",
                    unsafe_allow_html=True,
                )
            _seg_charts(_seg_all, _seg_label, expanded=True)
            st.markdown("---")

    _has_seg = seg_data.get("product") or seg_data.get("geo")
    _src_label = "sec-api.io" if SEC_API_KEY else ("FMP" if FMP_API_KEY else "")
    if _has_seg:
        if seg_data.get("product"):
            _prod_all = seg_data["product"]
            _prod_show = _prod_all[-5:]  # Normal-Ansicht: letzte 5 Jahre
            _seg_charts(_prod_show, "Produkt / Geschäftsbereich")
            if len(_prod_all) > 5:
                if st.button(f"📊 Alle {len(_prod_all)} Jahre anzeigen", key="exp_seg_prod"):
                    st.session_state["seg_expanded"] = ("product", "Produkt / Geschäftsbereich")
        if seg_data.get("geo"):
            _geo_all = seg_data["geo"]
            _geo_show = _geo_all[-5:]
            _seg_charts(_geo_show, "Geografie")
            if len(_geo_all) > 5:
                if st.button(f"📊 Alle {len(_geo_all)} Jahre anzeigen", key="exp_seg_geo"):
                    st.session_state["seg_expanded"] = ("geo", "Geografie")
        if _src_label:
            st.caption(f"Quelle: {_src_label}")
    elif SEC_API_KEY:
        st.markdown('<div class="insight-box" style="color:#546e7a;">ℹ️ Keine Segmentdaten gefunden — das Unternehmen rapportiert möglicherweise keine separaten Segmente in seinen XBRL-Filings.</div>', unsafe_allow_html=True)
    elif FMP_API_KEY:
        st.markdown('<div class="insight-box" style="color:#546e7a;">ℹ️ FMP Segmentdaten nicht verfügbar — FMP Paid Plan oder SEC_API_KEY benötigt.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="insight-box" style="color:#546e7a;">ℹ️ Segmentdaten: SEC_API_KEY in Railway-Umgebungsvariablen setzen (sec-api.io).</div>', unsafe_allow_html=True)

elif _at == 2:
    st.markdown("<div class='section-header'>Fundamental</div>", unsafe_allow_html=True)
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

    # Share count history — Balkendiagramm aus Jahresabschluss (split-bereinigt)
    if not a_shares.empty and len(a_shares) >= 2:
        try:
            _sh_ann = a_shares.sort_index()
            _sh_years = [pd.Timestamp(d).strftime("%Y") for d in _sh_ann.index]
            _sh_vals  = (_sh_ann.values / 1e9).tolist()
            _sh_delta = [0.0] + [(_sh_vals[i] - _sh_vals[i-1]) / abs(_sh_vals[i-1]) * 100 if _sh_vals[i-1] else 0 for i in range(1, len(_sh_vals))]
            _sh_colors = ["#ff5252" if d > 0.5 else "#00e676" if d < -0.5 else "#ffd600" for d in _sh_delta]
            fig_sh = go.Figure(go.Bar(
                x=_sh_years, y=_sh_vals,
                marker_color=_sh_colors,
                text=[f"{v:.2f}B" for v in _sh_vals],
                textposition="outside",
                textfont=dict(size=10, color="#90a4ae"),
            ))
            fig_sh.update_layout(
                title=dict(text="Aktienanzahl (Diluted) — Jahresverlauf", font=dict(size=12, color="#90a4ae"), x=0),
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,21,38,0.8)",
                height=220,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False, title="Mrd. Aktien"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(fig_sh, use_container_width=True)
            if st.button("📊 Detailansicht", key="exp_shares", use_container_width=False):
                st.session_state["wachstum_expanded"] = ("shares", ticker, "Aktienanzahl (Diluted)", "#26a69a", "#ef5350")
                st.session_state["active_tab"] = 1  # Wechsel zu Wachstum wo Detailansicht gerendert wird
            if dilution_pct is not None:
                dil_warn = "⚠️ Starke Verwässerung" if dilution_pct > 10 else "🟡 Moderate Verwässerung" if dilution_pct > 3 else "✅ Geringe Verwässerung / Rückkäufe (Buybacks)"
                st.markdown(f'<div class="insight-box"><strong>Aktienanzahl Trend:</strong> {dil_warn} ({dil_str} über {len(_sh_years)} Jahre). Rückgang = Buybacks = positiv für Aktionäre.</div>', unsafe_allow_html=True)
        except Exception:
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

    # ── Earnings Surprises ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>🎯 Earnings Surprises (EPS Beat / Miss)</div>", unsafe_allow_html=True)
    if earnings_surprises:
        _beat_streak = 0
        for _es in earnings_surprises:
            if _es["verdict"] == "Beat":
                _beat_streak += 1
            else:
                break

        # Streak badge
        if _beat_streak >= 2:
            _streak_html = (f"<span style='background:rgba(0,230,118,0.15);color:#00e676;"
                            f"border-radius:8px;padding:3px 12px;font-size:0.82rem;"
                            f"font-weight:700;margin-left:10px;'>"
                            f"🔥 {_beat_streak}× Beat-Streak</span>")
        else:
            _streak_html = ""
        st.markdown(f"<div style='margin-bottom:10px;color:#78909c;font-size:0.8rem;'>"
                    f"Letzte {len(earnings_surprises)} Quartale{_streak_html}</div>",
                    unsafe_allow_html=True)

        # Cards row
        _es_cols = st.columns(min(len(earnings_surprises), 4))
        for _i, _es in enumerate(earnings_surprises[:4]):
            _col = _es_cols[_i]
            _v   = _es["verdict"]
            _clr = "#00e676" if _v == "Beat" else "#ff5252" if _v == "Miss" else "#ffd600"
            _bg  = "rgba(0,230,118,0.08)" if _v == "Beat" else "rgba(255,82,82,0.08)" if _v == "Miss" else "rgba(255,214,0,0.08)"
            _icon = "✅" if _v == "Beat" else "❌" if _v == "Miss" else "➖"
            _surp_str = f"{_es['surp_pct']:+.1f}%"
            _col.markdown(f"""
            <div style='background:{_bg};border:1px solid {_clr}33;border-top:3px solid {_clr};
                 border-radius:12px;padding:12px 14px;text-align:center;'>
              <div style='color:#546e7a;font-size:0.72rem;margin-bottom:4px;'>{_es["date"]}</div>
              <div style='color:{_clr};font-size:1.1rem;font-weight:800;'>{_icon} {_v}</div>
              <div style='color:#eceff1;font-size:0.88rem;font-weight:700;margin:4px 0;'>{_surp_str}</div>
              <div style='color:#546e7a;font-size:0.7rem;'>
                {'Est: $' + f"{_es['estimate']:.2f} · " if _es['estimate'] is not None else ''}Act: ${_es["actual"]:.2f}
              </div>
            </div>""", unsafe_allow_html=True)

        # Surprise % bar chart (all 8 quarters)
        if len(earnings_surprises) > 1:
            _dates  = [e["date"]     for e in reversed(earnings_surprises)]
            _surps  = [e["surp_pct"] for e in reversed(earnings_surprises)]
            _colors = ["#00e676" if s > 2 else "#ff5252" if s < -2 else "#ffd600" for s in _surps]
            _fig_es = go.Figure(go.Bar(
                x=_dates, y=_surps,
                marker_color=_colors,
                text=[f"{s:+.1f}%" for s in _surps],
                textposition="outside",
                textfont=dict(size=10, color="#90a4ae"),
            ))
            _fig_es.add_hline(y=0, line_color="#1e3a5f", line_width=1)
            _fig_es.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,21,38,0.8)",
                height=200,
                margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False,
                           ticksuffix="%", title="Überraschung %"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(_fig_es, use_container_width=True)
    else:
        _fwd_eps = yf_info.get("forwardEps")
        _trail_eps = yf_info.get("trailingEps")
        _eps_hint = ""
        if _trail_eps:
            _eps_hint += f"&nbsp;·&nbsp;Trailing EPS: <strong>${_trail_eps:.2f}</strong>"
        if _fwd_eps:
            _eps_hint += f"&nbsp;·&nbsp;Forward EPS (Schätzung): <strong>${_fwd_eps:.2f}</strong>"
        _no_fmp_hint = " &nbsp;·&nbsp; <em>Tipp: FMP_API_KEY in Railway setzen für zuverlässige Daten.</em>" if not FMP_API_KEY else ""
        st.markdown(
            f'<div class="insight-box" style="color:#78909c;">'
            f'📭 Historische EPS-Überraschungen für <strong>{ticker}</strong> nicht verfügbar '
            f'(keine Datenquelle liefert Beat/Miss-Daten für diesen Titel).'
            f'{_no_fmp_hint}{_eps_hint}</div>',
            unsafe_allow_html=True)

    # ── Quartalsergebnisse ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Quartalsergebnisse</div>", unsafe_allow_html=True)
    if not q_rev.empty or not q_net.empty:
        _qfig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Umsatz (Quartale)", "Nettogewinn (Quartale)"],
            horizontal_spacing=0.08,
        )
        def _qfmt(v):
            if abs(v) >= 1e9: return f"${v/1e9:.1f}B"
            if abs(v) >= 1e6: return f"${v/1e6:.0f}M"
            return f"${v:.0f}"
        if not q_rev.empty:
            _labels = [d.strftime("Q%q '%y") if hasattr(d, 'strftime') else str(d)[:7]
                       for d in q_rev.index]
            _rev_b  = [v/1e9 for v in q_rev.values]
            _rev_cl = ["#00e676" if i == 0 or v >= _rev_b[i-1] else "#ff5252"
                       for i, v in enumerate(_rev_b)]
            _qfig.add_trace(go.Bar(
                x=_labels, y=_rev_b,
                marker_color=_rev_cl, name="Umsatz",
                text=[f"${v:.1f}B" for v in _rev_b],
                textposition="outside", textfont=dict(size=9, color="#90a4ae"),
            ), row=1, col=1)
        if not q_net.empty:
            _labels2 = [d.strftime("Q%q '%y") if hasattr(d, 'strftime') else str(d)[:7]
                        for d in q_net.index]
            _net_b   = [v/1e9 for v in q_net.values]
            _net_cl  = ["#00e676" if v >= 0 else "#ff5252" for v in _net_b]
            _qfig.add_trace(go.Bar(
                x=_labels2, y=_net_b,
                marker_color=_net_cl, name="Nettogewinn",
                text=[f"${v:.2f}B" for v in _net_b],
                textposition="outside", textfont=dict(size=9, color="#90a4ae"),
            ), row=1, col=2)
        _qfig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)",
            height=300,
            showlegend=False,
            margin=dict(l=0, r=0, t=36, b=0),
            font=dict(color="#90a4ae", size=10),
        )
        _qfig.update_yaxes(showgrid=True, gridcolor="#1e2d45", zeroline=True,
                           zerolinecolor="#1e3a5f", ticksuffix="B")
        st.plotly_chart(_qfig, use_container_width=True)
    else:
        st.markdown('<div class="metric-card" style="color:#546e7a;text-align:center;">'
                    'Quartalsdaten nicht verfügbar</div>', unsafe_allow_html=True)

    # ── CapEx & Goodwill ───────────────────────────────────────────────
    st.markdown("<div class='section-header'>🏗️ CapEx & Goodwill</div>", unsafe_allow_html=True)
    _cx1, _cx2 = st.columns(2)

    def _simple_bar(series: pd.Series, title: str, color: str,
                    fmt_fn=None, note: str = ""):
        if series.empty or len(series) < 2:
            return None
        s = series.tail(6)
        labels = [str(d.year) if hasattr(d, "year") else str(d)[:4] for d in s.index]
        texts = [fmt_fn(v) if fmt_fn else fmt_large(v) for v in s.values]
        fig = go.Figure(go.Bar(
            x=labels, y=s.values,
            marker_color=color,
            text=texts, textposition="outside",
            textfont=dict(size=10, color="#90a4ae"),
        ))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)", height=260,
            margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
            yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
            xaxis=dict(showgrid=False),
            title=dict(text=f"{title}{(' · ' + note) if note else ''}",
                       font=dict(color="#64b5f6", size=13)),
        )
        return fig

    with _cx1:
        _capex_note = "hohe CapEx = hohe Investitionen (Hyperscaler, Industrie)"
        _fig_capex = _simple_bar(a_capex, "CapEx absolut", "#ef5350",
                                 fmt_fn=fmt_large, note="")
        if _fig_capex:
            st.plotly_chart(_fig_capex, use_container_width=True)
            st.markdown(
                '<div style="font-size:0.68rem;color:#546e7a;margin-top:-8px;">'
                '⬆ Hohe CapEx = starke Investitionen (Hyperscaler, Industrie) · '
                'Als % des Umsatzes oder FCF einordnen</div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box" style="color:#546e7a;">Keine CapEx-Daten verfügbar</div>',
                        unsafe_allow_html=True)

    with _cx2:
        _fig_gw = _simple_bar(a_goodwill, "Goodwill", "#7986cb", fmt_fn=fmt_large)
        if _fig_gw:
            st.plotly_chart(_fig_gw, use_container_width=True)
            st.markdown(
                '<div style="font-size:0.68rem;color:#546e7a;margin-top:-8px;">'
                '⚠ Stark steigender Goodwill = viele Akquisitionen · '
                'Abschreibungsrisiko (Impairment) beachten</div>',
                unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box" style="color:#546e7a;">Keine Goodwill-Daten verfügbar</div>',
                        unsafe_allow_html=True)

    # CapEx als % des Umsatzes (nützlich für Hyperscaler-Vergleich)
    if not a_capex.empty and not a_rev.empty:
        _common_idx = a_capex.index.intersection(a_rev.index)
        if len(_common_idx) >= 2:
            _capex_pct = (a_capex[_common_idx] / a_rev[_common_idx] * 100).dropna()
            if not _capex_pct.empty:
                _labels_cp = [str(d.year) if hasattr(d, "year") else str(d)[:4]
                              for d in _capex_pct.index]
                _fig_cp = go.Figure(go.Bar(
                    x=_labels_cp, y=_capex_pct.values,
                    marker_color=["#ff8f00" if v > 15 else "#ffd600" if v > 8 else "#64b5f6"
                                  for v in _capex_pct.values],
                    text=[f"{v:.1f}%" for v in _capex_pct.values],
                    textposition="outside", textfont=dict(size=10, color="#90a4ae"),
                ))
                _fig_cp.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(13,21,38,0.8)", height=220,
                    margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
                    yaxis=dict(showgrid=True, gridcolor="#1e2d45", ticksuffix="%"),
                    xaxis=dict(showgrid=False),
                    title=dict(text="CapEx als % des Umsatzes",
                               font=dict(color="#64b5f6", size=13)),
                )
                st.plotly_chart(_fig_cp, use_container_width=True)
                st.markdown(
                    '<div style="font-size:0.68rem;color:#546e7a;margin-top:-8px;">'
                    'Benchmark: Hyperscaler (AWS/Azure/GCP) >10% · Industrie 5–10% · '
                    'Software/Asset-light &lt;3%</div>',
                    unsafe_allow_html=True)

elif _at == 3:
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
        _dy_label2 = "Dividend Yield ⚠️" if _div_yield_suspicious else "Dividend Yield"
        _dy_tooltip2 = "Wert >15 % — bitte manuell prüfen (möglicher Datenfehler)" if _div_yield_suspicious else None
        st.markdown(mini_card(_dy_label2, dividend_yield, 3, 1, ".2f", "%", tooltip=_dy_tooltip2), unsafe_allow_html=True)
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
        st.markdown("<div class='section-header'>💰 DCF Szenarien — Bull / Base / Bear</div>", unsafe_allow_html=True)

        # ── Szenario-Annahmen (basierend auf Rev. Growth) ──────────────
        _rg = rev_growth or 5
        _scenarios = {
            "🐻 Bear": {
                "growth": max(2.0,  round(_rg * 0.35, 1)),
                "terminal": 1.5, "discount": 11.0,
                "accent": "#ff5252", "bg": "rgba(255,82,82,0.07)",
                "label": "Konservativ",
            },
            "⚖️ Base": {
                "growth": max(5.0,  round(min(_rg * 0.65, 20), 1)),
                "terminal": 2.5, "discount": 10.0,
                "accent": "#64b5f6", "bg": "rgba(100,181,246,0.07)",
                "label": "Realistisch",
            },
            "🐂 Bull": {
                "growth": max(10.0, round(min(_rg * 0.90, 35), 1)),
                "terminal": 3.5, "discount":  9.0,
                "accent": "#00e676", "bg": "rgba(0,230,118,0.07)",
                "label": "Optimistisch",
            },
        }

        _sc_cols = st.columns(3)
        _sc_vals = {}
        for (_name, _sc), _col in zip(_scenarios.items(), _sc_cols):
            _fv = dcf_valuation(fcf, shares_outstanding,
                                _sc["growth"], _sc["terminal"], _sc["discount"], 10)
            _sc_vals[_name] = _fv
            if _fv:
                _mg = (_fv - price) / price * 100
                _mg_label = f"{'▲' if _mg > 0 else '▼'} {abs(_mg):.1f}% {'Upside' if _mg > 0 else 'Downside'}"
                _mg_clr   = _sc["accent"] if _mg > 0 else "#ff5252"
            else:
                _mg_label, _mg_clr = "N/A", "#546e7a"
            _col.markdown(f"""
            <div style='background:{_sc["bg"]};border:1px solid {_sc["accent"]}33;
                 border-top:3px solid {_sc["accent"]};border-radius:14px;
                 padding:18px 14px;text-align:center;'>
              <div style='color:{_sc["accent"]};font-size:0.78rem;font-weight:700;
                   text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;'>
                {_name}</div>
              <div style='color:#78909c;font-size:0.7rem;margin-bottom:10px;'>{_sc["label"]}</div>
              <div style='color:#eceff1;font-size:1.9rem;font-weight:800;'>
                {"${:,.0f}".format(_fv) if _fv else "N/A"}</div>
              <div style='color:{_mg_clr};font-size:0.85rem;font-weight:600;margin:6px 0;'>
                {_mg_label}</div>
              <div style='color:#37474f;font-size:0.68rem;line-height:1.6;margin-top:8px;
                   border-top:1px solid #1e2d45;padding-top:8px;text-align:left;'>
                Wachstum: {_sc["growth"]}%<br>
                Terminal: {_sc["terminal"]}%<br>
                Diskont:  {_sc["discount"]}%
              </div>
            </div>""", unsafe_allow_html=True)

        # ── Vergleichsbalken ───────────────────────────────────────────
        _fv_values = [v for v in _sc_vals.values() if v]
        if _fv_values and price:
            _bar_labels = list(_sc_vals.keys()) + ["📍 Kurs"]
            _bar_vals   = [v if v else 0 for v in _sc_vals.values()] + [price]
            _bar_clrs   = [_scenarios[n]["accent"] for n in _sc_vals] + ["#ffd600"]
            _fig_dcf = go.Figure(go.Bar(
                x=_bar_labels, y=_bar_vals,
                marker_color=_bar_clrs,
                text=[f"${v:,.0f}" for v in _bar_vals],
                textposition="outside",
                textfont=dict(size=11, color="#90a4ae"),
            ))
            _fig_dcf.add_hline(y=price, line_dash="dot", line_color="#ffd600",
                               line_width=1.5,
                               annotation_text=f"Kurs ${price:.0f}",
                               annotation_font_color="#ffd600")
            _fig_dcf.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,21,38,0.8)",
                height=260, showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0),
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False,
                           tickprefix="$"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(_fig_dcf, use_container_width=True)

        # ── Manueller Rechner (aufklappbar) ────────────────────────────
        with st.expander("⚙️ Eigenes Szenario berechnen", expanded=False):
            st.markdown(f"""
            <div class="insight-box" style="margin-bottom:12px;">
                <strong>ℹ️ DCF Hinweis:</strong> Der Wert reagiert stark auf Eingaben.
                Konservative Wachstumsrate (10–20%) und höherer Diskontsatz (10–12%)
                vermeiden Euphorie-Prämien. Akt. Rev. Growth: <strong>{rev_growth:.1f}%</strong>.
            </div>""", unsafe_allow_html=True)
            default_growth = min(max(int(_rg), 5), 30)
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
                <div style="background:linear-gradient(135deg,#0d2137,#0a1a2e);border:1px solid #1e3a5f;
                     border-radius:16px;padding:22px;margin-top:10px;text-align:center;">
                    <div style="color:#78909c;font-size:0.8rem;text-transform:uppercase;
                         letter-spacing:1px;margin-bottom:8px;">Eigenes Szenario</div>
                    <div style="color:#eceff1;font-size:2.5rem;font-weight:800;">${fair_val:.2f}</div>
                    <div style="color:{m_color};font-size:1rem;margin-top:6px;font-weight:600;">
                        {'▲' if margin > 0 else '▼'} {abs(margin):.1f}% {m_label}
                    </div>
                    <div style="color:#546e7a;font-size:0.78rem;margin-top:6px;">
                        Kurs: ${price:.2f} | FCF: {fmt_large(fcf)}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Nicht genug Daten für DCF-Berechnung (FCF oder Shares fehlen).")

# ==================== TAB 5: CHART ANALYSE ====================
elif _at == 6:
    st.markdown("<div class='section-header'>📉 Technische Chart-Analyse</div>", unsafe_allow_html=True)

    # ── Controls row ──────────────────────────────────────────────────
    _c1, _c2, _c3 = st.columns([2, 2, 2])
    with _c1:
        chart_mode = st.radio("Zeitrahmen", ["Täglich (5J)", "Wöchentlich (2J)", "Monatlich (5J)"],
                              horizontal=True, key="chart_mode")
    with _c2:
        chart_type = st.radio("Chart-Typ", ["Candlestick", "Linie"], horizontal=True, key="ctype")
    with _c3:
        _lcol, _rcol = st.columns(2)
        with _lcol:
            show_sp500 = st.checkbox("S&P 500 Vergleich", value=False, key="show_sp500")
        with _rcol:
            show_log = st.checkbox("Log. Skala", value=False, key="log_scale")

    _ic1, _ic2 = st.columns([3, 2])
    with _ic1:
        ema_options = st.multiselect("EMAs", ["EMA 20", "EMA 50", "EMA 100", "EMA 200"],
                                     default=["EMA 50", "EMA 200"], key="ema_sel")
    with _ic2:
        indicator_options = st.multiselect("Indikatoren",
                                           ["RSI (14)", "MACD", "Bollinger Bänder", "Fibonacci"],
                                           default=["RSI (14)"], key="ind_sel")

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
        show_rsi  = "RSI (14)"          in indicator_options
        show_macd = "MACD"              in indicator_options
        show_fib  = "Fibonacci"         in indicator_options
        show_bb   = "Bollinger Bänder"  in indicator_options

        # Dynamic subplot layout
        n_rows = 1 + (1 if show_rsi else 0) + (1 if show_macd else 0)
        row_h = [0.55 if (show_rsi or show_macd) else 0.75, 0.15]
        if show_rsi:   row_h.append(0.15)
        if show_macd:  row_h.append(0.15)
        # Always add volume row
        subplot_titles = ["", "Volumen"]
        if show_rsi:   subplot_titles.append("RSI (14)")
        if show_macd:  subplot_titles.append("MACD")

        fig_ta = make_subplots(
            rows=1 + 1 + (1 if show_rsi else 0) + (1 if show_macd else 0),
            cols=1,
            shared_xaxes=True,
            row_heights=[0.55 if (show_rsi or show_macd) else 0.72,
                         0.12,
                         *([0.16] if show_rsi else []),
                         *([0.16] if show_macd else [])],
            vertical_spacing=0.02,
            subplot_titles=["", "Volumen",
                            *( ["RSI (14)"] if show_rsi else []),
                            *( ["MACD"]     if show_macd else [])],
        )
        vol_row  = 2
        rsi_row  = 3 if show_rsi else None
        macd_row = (3 + (1 if show_rsi else 0)) if show_macd else None

        close = chart_data["Close"]

        # ── Price ──────────────────────────────────────────────────────
        ema_periods = {"EMA 20": 20, "EMA 50": 50, "EMA 100": 100, "EMA 200": 200}
        ema_colors  = {"EMA 20": "#ffd600", "EMA 50": "#00e5ff", "EMA 100": "#ff9100", "EMA 200": "#ef5350"}

        if chart_type == "Candlestick":
            fig_ta.add_trace(go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"], high=chart_data["High"],
                low=chart_data["Low"],  close=close,
                name=ticker,
                increasing_line_color="#00e676", decreasing_line_color="#ff5252",
                increasing_fillcolor="#00e676",  decreasing_fillcolor="#ff5252",
            ), row=1, col=1)
        else:
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=close, name=ticker,
                line=dict(color="#00e5ff", width=2),
                fill="tozeroy", fillcolor="rgba(0,229,255,0.04)",
            ), row=1, col=1)

        # ── S&P 500 comparison (scaled to stock's start price) ─────────
        if show_sp500:
            if chart_type == "Candlestick":
                st.caption("ℹ️ S&P 500 Vergleich nur im Linie-Modus verfügbar")
            else:
                try:
                    _sp_days = 2*365+10 if "Wöchentlich" in chart_mode else 5*365+10
                    _sp_start = (_dt.date.today() - _dt.timedelta(days=_sp_days)).strftime("%Y-%m-%d")
                    _sp_end = _dt.date.today().strftime("%Y-%m-%d")
                    _sp_hist = yf.Ticker("^GSPC").history(
                        start=_sp_start, end=_sp_end,
                        interval="1wk" if "Wöchentlich" in chart_mode else
                                 "1mo" if "Monatlich"   in chart_mode else "1d"
                    )
                    if not _sp_hist.empty:
                        # Normalize both series to date-only to avoid tz mismatch
                        _sp_close = _sp_hist["Close"].copy()
                        _sp_close.index = pd.to_datetime(_sp_close.index).normalize().tz_localize(None)
                        _cd_index_norm  = pd.to_datetime(chart_data.index).normalize().tz_localize(None)
                        _sp_reindexed   = _sp_close.reindex(_cd_index_norm, method="ffill").dropna()
                        if not _sp_reindexed.empty and not close.empty:
                            # Scale S&P so it starts at the same price as the stock
                            _stock_start = float(close.iloc[0])
                            _sp_start    = float(_sp_reindexed.iloc[0])
                            _sp_scaled   = _sp_reindexed * (_stock_start / _sp_start)
                            # Re-attach original chart_data dates for x-axis
                            _valid_mask  = _cd_index_norm.isin(_sp_reindexed.index)
                            _x_dates     = chart_data.index[_valid_mask]
                            fig_ta.add_trace(go.Scatter(
                                x=_x_dates, y=_sp_scaled.values,
                                name="S&P 500 (relativ)",
                                line=dict(color="#78909c", width=1.5, dash="dot"),
                            ), row=1, col=1)
                except Exception:
                    pass

        # ── EMAs ──────────────────────────────────────────────────────
        for ema_name in ema_options:
            period = ema_periods[ema_name]
            if len(chart_data) >= period:
                fig_ta.add_trace(go.Scatter(
                    x=chart_data.index, y=compute_ema(close, period),
                    name=ema_name, line=dict(color=ema_colors[ema_name], width=1.4),
                ), row=1, col=1)

        # ── Bollinger Bands (20, 2σ) ────────────────────────────────────
        if show_bb and len(close) >= 20:
            _bb_mid   = close.rolling(20).mean()
            _bb_std   = close.rolling(20).std()
            _bb_upper = _bb_mid + 2 * _bb_std
            _bb_lower = _bb_mid - 2 * _bb_std
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=_bb_upper, name="BB Oben",
                line=dict(color="rgba(100,181,246,0.6)", width=1, dash="dot"),
                showlegend=True,
            ), row=1, col=1)
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=_bb_lower, name="BB Unten",
                line=dict(color="rgba(100,181,246,0.6)", width=1, dash="dot"),
                fill="tonexty", fillcolor="rgba(100,181,246,0.04)",
                showlegend=True,
            ), row=1, col=1)
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=_bb_mid, name="BB Mitte (SMA 20)",
                line=dict(color="rgba(100,181,246,0.35)", width=1),
                showlegend=False,
            ), row=1, col=1)

        # ── Fibonacci ──────────────────────────────────────────────────
        if show_fib:
            _fib_high = float(chart_data["High"].max())
            _fib_low  = float(chart_data["Low"].min())
            _fib_levels = compute_fibonacci(_fib_high, _fib_low)
            _fib_colors = {
                "0.0 %":   "rgba(255,255,255,0.25)",
                "23.6 %":  "rgba(255,214,0,0.55)",
                "38.2 %":  "rgba(0,230,118,0.65)",
                "50.0 %":  "rgba(0,229,255,0.65)",
                "61.8 %":  "rgba(0,230,118,0.65)",
                "78.6 %":  "rgba(255,145,0,0.65)",
                "100.0 %": "rgba(255,255,255,0.25)",
            }
            for label, lvl in _fib_levels.items():
                fig_ta.add_hline(
                    y=lvl, line_dash="dot",
                    line_color=_fib_colors.get(label, "rgba(100,181,246,0.4)"),
                    line_width=1,
                    annotation_text=f"Fib {label}  ${lvl:.2f}",
                    annotation_font_color=_fib_colors.get(label, "#64b5f6"),
                    annotation_font_size=9,
                    row=1, col=1,
                )

        # ── Analyst target ──────────────────────────────────────────────
        if target_mean:
            fig_ta.add_hline(y=target_mean, line_dash="dot", line_color="#ffd600", line_width=1.5,
                             annotation_text=f"Analyst Ziel ${target_mean:.0f}",
                             annotation_font_color="#ffd600", row=1, col=1)

        # ── Volume ──────────────────────────────────────────────────────
        vol_colors = ["#00e676" if c >= o else "#ff5252"
                      for c, o in zip(close, chart_data["Open"])]
        fig_ta.add_trace(go.Bar(
            x=chart_data.index, y=chart_data["Volume"],
            name="Volumen", marker_color=vol_colors, opacity=0.55, showlegend=False,
        ), row=vol_row, col=1)

        # ── RSI ─────────────────────────────────────────────────────────
        if show_rsi and rsi_row:
            rsi_vals = compute_rsi(close)
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=rsi_vals,
                name="RSI", line=dict(color="#a78bfa", width=1.5), showlegend=False,
            ), row=rsi_row, col=1)
            for lvl, clr in [(70, "rgba(255,82,82,0.35)"), (30, "rgba(0,230,118,0.35)")]:
                fig_ta.add_hline(y=lvl, line_dash="dash", line_color=clr, line_width=1,
                                 row=rsi_row, col=1)
            fig_ta.update_yaxes(range=[0, 100], row=rsi_row, col=1)

        # ── MACD ────────────────────────────────────────────────────────
        if show_macd and macd_row:
            macd_line, signal_line, macd_hist = compute_macd(close)
            hist_colors = ["#00e676" if v >= 0 else "#ff5252" for v in macd_hist]
            fig_ta.add_trace(go.Bar(
                x=chart_data.index, y=macd_hist,
                name="MACD Hist", marker_color=hist_colors, opacity=0.6, showlegend=False,
            ), row=macd_row, col=1)
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=macd_line,
                name="MACD", line=dict(color="#00e5ff", width=1.5), showlegend=False,
            ), row=macd_row, col=1)
            fig_ta.add_trace(go.Scatter(
                x=chart_data.index, y=signal_line,
                name="Signal", line=dict(color="#ffd600", width=1.2), showlegend=False,
            ), row=macd_row, col=1)

        # ── Layout ──────────────────────────────────────────────────────
        _total_rows = 1 + 1 + (1 if show_rsi else 0) + (1 if show_macd else 0)
        _height = 560 + 120 * (_total_rows - 2)

        # Default view: last 1 year (fixes the "chart only visible until Jan/Feb" issue)
        _today      = pd.Timestamp.today().normalize()
        _range_end  = _today.strftime("%Y-%m-%d")
        _range_start = (_today - pd.DateOffset(years=1)).strftime("%Y-%m-%d")

        # 52-week high/low reference lines
        if len(chart_data) >= 50:
            _lookback = min(252, len(chart_data))
            _52w_high = float(chart_data["High"].iloc[-_lookback:].max())
            _52w_low  = float(chart_data["Low"].iloc[-_lookback:].min())
            fig_ta.add_hline(y=_52w_high, line_dash="dot",
                             line_color="rgba(0,230,118,0.4)", line_width=1,
                             annotation_text=f"52W Hoch ${_52w_high:.2f}",
                             annotation_font_color="rgba(0,230,118,0.7)",
                             annotation_font_size=9, row=1, col=1)
            fig_ta.add_hline(y=_52w_low, line_dash="dot",
                             line_color="rgba(255,82,82,0.4)", line_width=1,
                             annotation_text=f"52W Tief ${_52w_low:.2f}",
                             annotation_font_color="rgba(255,82,82,0.7)",
                             annotation_font_size=9, row=1, col=1)

        # Wochenend-Lücken nur im Tages-Chart (muss VOR update_layout definiert werden,
        # damit range= nicht durch späteres update_xaxes überschrieben wird)
        _rangebreaks = [dict(bounds=["sat", "mon"])] if chart_mode == "Täglich (5J)" else []

        fig_ta.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,21,38,0.8)",
            height=_height,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                        bgcolor="rgba(13,21,38,0.8)", bordercolor="#1e3a5f", borderwidth=1,
                        font=dict(size=10)),
            margin=dict(l=0, r=60, t=40, b=0),
            xaxis=dict(
                showgrid=False, zeroline=False,
                rangeslider=dict(visible=False),
                range=[_range_start, _range_end],
                rangebreaks=_rangebreaks,
                rangeselector=dict(
                    bgcolor="#0d1526",
                    activecolor="#1565c0",
                    bordercolor="#1e3a5f",
                    borderwidth=1,
                    font=dict(color="#90a4ae", size=10),
                    buttons=[
                        dict(count=1,  label="1M",  step="month", stepmode="backward"),
                        dict(count=3,  label="3M",  step="month", stepmode="backward"),
                        dict(count=6,  label="6M",  step="month", stepmode="backward"),
                        dict(count=1,  label="YTD", step="year",  stepmode="todate"),
                        dict(count=1,  label="1J",  step="year",  stepmode="backward"),
                        dict(count=2,  label="2J",  step="year",  stepmode="backward"),
                        dict(count=5,  label="5J",  step="year",  stepmode="backward"),
                        dict(step="all", label="MAX"),
                    ],
                ),
            ),
            yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False,
                       type="log" if show_log else "linear"),
            hovermode="x unified",
            title=dict(text=f"{company_name} — {title_suffix}", font=dict(color="#64b5f6", size=14)),
        )

        for r in range(2, _total_rows + 1):
            fig_ta.update_xaxes(showgrid=False, rangebreaks=_rangebreaks, row=r, col=1)
            fig_ta.update_yaxes(showgrid=True, gridcolor="#1e2d45", zeroline=False, row=r, col=1)

        st.plotly_chart(fig_ta, use_container_width=True)

        # ── EMA + RSI insight box ────────────────────────────────────────
        _insights = []
        current_price_c = close.iloc[-1]
        for ema_name in ema_options:
            period = ema_periods[ema_name]
            if len(chart_data) >= period:
                ema_now = compute_ema(close, period).iloc[-1]
                pct_diff = (current_price_c - ema_now) / ema_now * 100
                status = "oberhalb ✅" if pct_diff > 0 else "unterhalb ⚠️"
                _insights.append(f"{ema_name}: {status} ({pct_diff:+.1f}%)")
        if show_rsi:
            rsi_now = compute_rsi(close).iloc[-1]
            rsi_status = "Überkauft 🔴" if rsi_now > 70 else "Überverkauft 🟢" if rsi_now < 30 else "Neutral ⚪"
            _insights.append(f"RSI: {rsi_now:.1f} — {rsi_status}")
        if show_macd:
            _ml, _sl, _ = compute_macd(close)
            _cross = "Bullish ✅ (MACD > Signal)" if _ml.iloc[-1] > _sl.iloc[-1] else "Bearish ⚠️ (MACD < Signal)"
            _insights.append(f"MACD: {_cross}")
        if show_bb and len(close) >= 20:
            _bb_m = close.rolling(20).mean().iloc[-1]
            _bb_s = close.rolling(20).std().iloc[-1]
            _bb_u, _bb_l = _bb_m + 2 * _bb_s, _bb_m - 2 * _bb_s
            _cp = float(close.iloc[-1])
            _bw = (_bb_u - _bb_l) / _bb_m * 100  # Bandwidth %
            if _cp > _bb_u:
                _bb_status = "Über BB Oben 🔴 (überkauft)"
            elif _cp < _bb_l:
                _bb_status = "Unter BB Unten 🟢 (überverkauft)"
            else:
                _bb_status = f"Innerhalb ({(_cp - _bb_l) / (_bb_u - _bb_l) * 100:.0f}% vom Tief)"
            _insights.append(f"BB: {_bb_status} · Breite {_bw:.1f}%")
        if _insights:
            st.markdown(f"""
            <div class="insight-box">
                <strong>📊 Indikator-Analyse ({title_suffix}):</strong><br>
                {'&nbsp;&nbsp;|&nbsp;&nbsp;'.join(_insights)}
            </div>""", unsafe_allow_html=True)

        if show_fib:
            _fib_high_v = float(chart_data["High"].max())
            _fib_low_v  = float(chart_data["Low"].min())
            _curr_p     = float(close.iloc[-1])
            _fib_lvls_e = compute_fibonacci(_fib_high_v, _fib_low_v)
            _nearest    = min(_fib_lvls_e.items(), key=lambda kv: abs(kv[1] - _curr_p))
            st.markdown(f"""
            <div class="insight-box" style="margin-top:8px;">
                <strong>📐 Fibonacci Retracement — Erklärung</strong><br>
                Die Fibonacci-Levels markieren potenzielle <strong>Unterstützungs- und Widerstandszonen</strong>
                basierend auf mathematischen Verhältnissen der Fibonacci-Folge.
                Berechnet vom <strong>Hoch (${_fib_high_v:.2f})</strong> bis zum
                <strong>Tief (${_fib_low_v:.2f})</strong> des dargestellten Zeitraums.<br><br>
                <span style="color:#ffd600;">▸ 23.6 %</span> — Schwache Korrektur, typisch bei starken Trends<br>
                <span style="color:#00e676;">▸ 38.2 %</span> — Klassische erste Unterstützung nach Aufwärtstrend<br>
                <span style="color:#00e5ff;">▸ 50.0 %</span> — Psychologisch wichtige Halbierungszone<br>
                <span style="color:#00e676;">▸ 61.8 %</span> — Das <em>goldene Verhältnis</em> — stärkste Unterstützungszone<br>
                <span style="color:#ff9100;">▸ 78.6 %</span> — Tiefe Korrektur; Unterschreitung deutet auf Trendumkehr<br><br>
                Aktueller Kurs <strong>${_curr_p:.2f}</strong> liegt am nächsten zu
                <strong>Fib {_nearest[0]} (${_nearest[1]:.2f})</strong>.
            </div>""", unsafe_allow_html=True)

# ==================== TAB 6: INSIDER & PEERS ====================
elif _at == 7:
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
                    _fcf_p  = pi.get("freeCashflow")
                    _mc_p   = pi.get("marketCap")
                    _fcy_p  = (_fcf_p / _mc_p * 100) if _fcf_p and _mc_p else None
                    _roe_p  = pi.get("returnOnEquity")
                    peer_data.append({
                        "Ticker":     pt,
                        "Kurs":       pi.get("currentPrice") or pi.get("regularMarketPrice"),
                        "Mkt Cap":    _mc_p,
                        "P/E":        pi.get("trailingPE"),
                        "Gross Mg%":  (pi.get("grossMargins") or 0) * 100,
                        "Op. Mg%":    (pi.get("operatingMargins") or 0) * 100,
                        "Rev Gr%":    (pi.get("revenueGrowth") or 0) * 100,
                        "FCF Yield%": _fcy_p,
                        "ROE%":       (_roe_p * 100) if _roe_p else None,
                    })
                except:
                    pass

            if peer_data:
                pdf = pd.DataFrame(peer_data).set_index("Ticker")
                # Sector benchmark row
                _bench_p = SECTOR_BENCHMARKS.get(sector, {})
                if _bench_p:
                    pdf.loc[f"∅ {sector[:14]}"] = {
                        "Kurs":       None,
                        "Mkt Cap":    None,
                        "P/E":        None,
                        "Gross Mg%":  _bench_p.get("Bruttomarge"),
                        "Op. Mg%":    _bench_p.get("Op. Marge"),
                        "Rev Gr%":    _bench_p.get("Umsatzwachstum"),
                        "FCF Yield%": _bench_p.get("FCF Yield"),
                        "ROE%":       None,
                    }
                # Format columns
                def _pct(v):
                    return f"{v:.1f}%" if isinstance(v, float) and not pd.isna(v) else "—"
                def _pr(v):
                    return f"${v:.2f}" if isinstance(v, float) and not pd.isna(v) else "—"
                pdf["Kurs"]       = pdf["Kurs"].apply(_pr)
                pdf["Mkt Cap"]    = pdf["Mkt Cap"].apply(lambda v: fmt_large(v) if isinstance(v, float) and not pd.isna(v) else "—")
                pdf["P/E"]        = pdf["P/E"].apply(lambda v: f"{v:.1f}x" if isinstance(v, float) and not pd.isna(v) else "—")
                pdf["Gross Mg%"]  = pdf["Gross Mg%"].apply(_pct)
                pdf["Op. Mg%"]    = pdf["Op. Mg%"].apply(_pct)
                pdf["Rev Gr%"]    = pdf["Rev Gr%"].apply(_pct)
                pdf["FCF Yield%"] = pdf["FCF Yield%"].apply(_pct)
                pdf["ROE%"]       = pdf["ROE%"].apply(_pct)
                st.dataframe(pdf, use_container_width=True)
        elif not FMP_API_KEY:
            st.markdown('<div class="insight-box">FMP API Key erforderlich für Peer-Daten.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="insight-box">Keine Peers gefunden.</div>', unsafe_allow_html=True)

    # ── Management ────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>👔 Management & Ownership</div>", unsafe_allow_html=True)
    _officers = yf_info.get("companyOfficers") or []
    _ins_pct   = yf_info.get("heldPercentInsiders")
    _inst_pct  = yf_info.get("heldPercentInstitutions")

    _om1, _om2, _om3, _om4 = st.columns(4)
    with _om1:
        _ins_str = f"{_ins_pct*100:.1f}%" if _ins_pct else "N/A"
        _ins_clr = "#00e676" if _ins_pct and _ins_pct > 0.05 else "#ffd600" if _ins_pct else "#546e7a"
        st.markdown(f"""<div class="metric-card" style="text-align:center;">
            <div class="metric-label">Insider-Ownership</div>
            <div class="metric-value" style="color:{_ins_clr};">{_ins_str}</div>
            <div class="metric-sub">CEO/CFO/Board halten</div>
        </div>""", unsafe_allow_html=True)
    with _om2:
        _inst_str = f"{_inst_pct*100:.1f}%" if _inst_pct else "N/A"
        st.markdown(f"""<div class="metric-card" style="text-align:center;">
            <div class="metric-label">Institutionell</div>
            <div class="metric-value">{_inst_str}</div>
            <div class="metric-sub">Fonds / ETFs</div>
        </div>""", unsafe_allow_html=True)
    with _om3:
        _roic_clr = "#00e676" if roic_val and roic_val > 15 else "#ffd600" if roic_val and roic_val > 8 else "#ff5252" if roic_val else "#546e7a"
        st.markdown(f"""<div class="metric-card" style="text-align:center;">
            <div class="metric-label">ROIC</div>
            <div class="metric-value" style="color:{_roic_clr};">{f"{roic_val:.1f}%" if roic_val else "N/A"}</div>
            <div class="metric-sub">Kapitalallokation</div>
        </div>""", unsafe_allow_html=True)
    with _om4:
        _dil_str = f"{dilution_pct:+.1f}%" if dilution_pct is not None else "N/A"
        _dil_clr = "#00e676" if dilution_pct is not None and dilution_pct < 0 else \
                   "#ffd600" if dilution_pct is not None and dilution_pct < 3 else \
                   "#ff5252" if dilution_pct is not None else "#546e7a"
        st.markdown(f"""<div class="metric-card" style="text-align:center;">
            <div class="metric-label">Verwässerung (5J)</div>
            <div class="metric-value" style="color:{_dil_clr};">{_dil_str}</div>
            <div class="metric-sub">Share count Δ</div>
        </div>""", unsafe_allow_html=True)

    if _officers:
        _mgmt_rows = []
        for o in _officers[:6]:
            _name  = o.get("name", "–")
            _title = o.get("title", "–")
            _age   = o.get("age")
            _pay   = o.get("totalPay")
            _age_s = str(_age) if _age else "–"
            _pay_s = f"${_pay/1e6:.1f}M" if _pay else "–"
            _mgmt_rows.append((_name, _title, _age_s, _pay_s))

        _mc_cols = st.columns([3, 4, 1, 2])
        for hdr, col in zip(["Name", "Funktion", "Alter", "Vergütung"], _mc_cols):
            col.markdown(f"<div style='color:#546e7a; font-size:0.72rem; font-weight:600; padding:4px 0;'>{hdr}</div>",
                         unsafe_allow_html=True)
        for _name, _title, _age_s, _pay_s in _mgmt_rows:
            c1, c2, c3, c4 = st.columns([3, 4, 1, 2])
            c1.markdown(f"<div style='color:#eceff1; font-size:0.82rem; padding:3px 0;'>{_name}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='color:#90a4ae; font-size:0.78rem; padding:3px 0;'>{_title}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='color:#546e7a; font-size:0.78rem; padding:3px 0;'>{_age_s}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='color:#64b5f6; font-size:0.78rem; padding:3px 0;'>{_pay_s}</div>", unsafe_allow_html=True)

    st.markdown("""<div style='color:#37474f; font-size:0.72rem; margin-top:10px;'>
        ℹ️ Managementqualität lässt sich nicht allein aus Zahlen ableiten — Insider-Ownership >5% und
        sinkende Aktienanzahl sind starke positive Signale. Für eine vollständige Einschätzung: Shareholder Letters,
        Glassdoor-Bewertungen und Track Record bei Kapitalallokation prüfen.
    </div>""", unsafe_allow_html=True)

# ==================== TAB 7: NEWS ====================
elif _at == 8:
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
            from datetime import datetime, timezone
            stock_obj = yf.Ticker(ticker)
            news_items = stock_obj.news or []

            parsed = []
            for item in news_items[:10]:
                # Neues yfinance-Format (>=0.2.52): Felder in item["content"]
                content = item.get("content") or {}
                if content:
                    title     = content.get("title", "")
                    publisher = (content.get("provider") or {}).get("displayName", "") or \
                                item.get("publisher", "")
                    link      = (content.get("canonicalUrl") or {}).get("url", "") or \
                                (content.get("clickThroughUrl") or {}).get("url", "#")
                    pub_raw   = content.get("pubDate", "")
                    try:
                        pub_str = pub_raw[:10] if pub_raw else ""
                    except Exception:
                        pub_str = ""
                    summary = content.get("summary", "")
                else:
                    # Altes Format
                    title     = item.get("title", "")
                    publisher = item.get("publisher", "")
                    link      = item.get("link", "#")
                    pub_time  = item.get("providerPublishTime", 0)
                    pub_str   = datetime.fromtimestamp(pub_time, tz=timezone.utc).strftime("%Y-%m-%d") if pub_time else ""
                    summary   = item.get("summary", "")

                if title:
                    parsed.append({"title": title, "publisher": publisher,
                                   "link": link, "pub_str": pub_str, "summary": summary})

            if parsed:
                for p in parsed:
                    desc_html = f'<div style="color:#78909c; font-size:0.78rem; margin-top:6px; line-height:1.4;">{p["summary"][:180]}{"…" if len(p["summary"]) > 180 else ""}</div>' if p["summary"] else ""
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                            <span style="color:#64b5f6; font-size:0.75rem; font-weight:600;">{p['publisher']}</span>
                            <span style="color:#546e7a; font-size:0.72rem;">{p['pub_str']}</span>
                        </div>
                        <a href="{p['link']}" target="_blank" style="color:#eceff1; font-size:0.9rem; font-weight:600; text-decoration:none; line-height:1.4;">
                            {p['title']}
                        </a>
                        {desc_html}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keine News über yFinance verfügbar. Für mehr News: NEWS_API_KEY setzen.")
        except Exception as ex:
            st.info(f"News konnten nicht geladen werden: {ex}")

# ==================== TAB 8: BURGGRABEN ====================
elif _at == 5:
    # ── Header: Moat-Breite ────────────────────────────────────────────
    st.markdown("<div class='section-header'>🏰 Burggraben-Einschätzung</div>", unsafe_allow_html=True)
    mc1, mc2, mc3 = st.columns([1, 1, 2])
    with mc1:
        st.markdown(f"""
        <div class="score-section">
            <div class="score-title">Moat Score</div>
            <div class="score-num" style="color:{moat['moat_color']};">{moat['moat_score']}</div>
            <div class="score-label">{moat['moat_icon']} {moat['moat_width']}</div>
        </div>""", unsafe_allow_html=True)
    with mc2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:28px 16px;">
            <div class="metric-label">Marktstruktur</div>
            <div style="font-size:1.3rem; font-weight:700; color:{moat['market_color']}; margin:10px 0;">
                {moat['market_structure']}
            </div>
            <div class="metric-sub">{sector} · {industry}</div>
        </div>""", unsafe_allow_html=True)
    with mc3:
        st.markdown(f"""
        <div class="insight-box" style="height:100%; display:flex; align-items:center;">
            <div>
                <strong style="color:{moat['moat_color']};">{moat['moat_icon']} {moat['moat_width']}</strong><br>
                <span style="color:#b0bec5; font-size:0.9rem; line-height:1.6;">{moat['moat_desc']}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Unternehmensübersicht ──────────────────────────────────────────
    st.markdown("<div class='section-header'>🏢 Unternehmensübersicht</div>", unsafe_allow_html=True)
    _summary = yf_info.get("longBusinessSummary", "")
    _employees = yf_info.get("fullTimeEmployees")
    _founded = yf_info.get("founded") or yf_info.get("incorporationDate", "")
    _country = yf_info.get("country", "")
    _city = yf_info.get("city", "")
    _website = yf_info.get("website", "")

    oc1, oc2, oc3, oc4 = st.columns(4)
    with oc1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Land / Sitz</div>
            <div class="metric-value" style="font-size:1.1rem;">{_country}</div>
            <div class="metric-sub">{_city}</div>
        </div>""", unsafe_allow_html=True)
    with oc2:
        emp_str = f"{_employees:,}".replace(",", ".") if _employees else "N/A"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Mitarbeiter</div>
            <div class="metric-value" style="font-size:1.1rem;">{emp_str}</div>
            <div class="metric-sub">Vollzeitstellen</div>
        </div>""", unsafe_allow_html=True)
    with oc3:
        mc_str = fmt_large(market_cap) if market_cap else "N/A"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Marktkapitalisierung</div>
            <div class="metric-value" style="font-size:1.1rem;">{mc_str}</div>
            <div class="metric-sub">Market Cap</div>
        </div>""", unsafe_allow_html=True)
    with oc4:
        rev_str = fmt_large(yf_info.get("totalRevenue")) if yf_info.get("totalRevenue") else "N/A"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Umsatz (TTM)</div>
            <div class="metric-value" style="font-size:1.1rem;">{rev_str}</div>
            <div class="metric-sub">Total Revenue</div>
        </div>""", unsafe_allow_html=True)

    if _summary:
        # Kürze auf ~4 Sätze
        _sentences = _summary.replace("  ", " ").split(". ")
        _short = ". ".join(_sentences[:4]) + ("." if len(_sentences) > 4 else "")
        st.markdown(f"""
        <div class="insight-box" style="line-height:1.7; color:#b0bec5; font-size:0.92rem;">
            {_short}
            {'<details style="margin-top:8px;"><summary style="color:#64b5f6;cursor:pointer;font-size:0.82rem;">Vollständige Beschreibung</summary><div style="margin-top:8px;">' + _summary + '</div></details>' if len(_sentences) > 4 else ''}
        </div>""", unsafe_allow_html=True)

    # ── Moat-Treiber ──────────────────────────────────────────────────
    if moat["moat_types"]:
        st.markdown("<div class='section-header'>⚙️ Erkannte Moat-Treiber</div>", unsafe_allow_html=True)
        tcols = st.columns(min(len(moat["moat_types"]), 3))
        for col, (title, desc) in zip(tcols, moat["moat_types"]):
            col.markdown(f"""
            <div class="metric-card" style="height:100%;">
                <div style="font-size:1.1rem; font-weight:700; color:#00e5ff; margin-bottom:10px;">{title}</div>
                <div style="color:#90a4ae; font-size:0.83rem; line-height:1.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)
        # Wenn mehr als 3 Treiber
        if len(moat["moat_types"]) > 3:
            tcols2 = st.columns(len(moat["moat_types"]) - 3)
            for col, (title, desc) in zip(tcols2, moat["moat_types"][3:]):
                col.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:1.1rem; font-weight:700; color:#00e5ff; margin-bottom:10px;">{title}</div>
                    <div style="color:#90a4ae; font-size:0.83rem; line-height:1.6;">{desc}</div>
                </div>""", unsafe_allow_html=True)

    # ── Qualitative Indikatoren ────────────────────────────────────────
    st.markdown("<div class='section-header'>📐 Finanzielle Moat-Indikatoren</div>", unsafe_allow_html=True)
    qc1, qc2, qc3, qc4, qc5 = st.columns(5)
    _moat_metrics = [
        (qc1, "Bruttomargen", gross_margin, "%", 60, 40, False,
         "Pricing Power — >60% deutet auf Burggraben hin"),
        (qc2, "ROIC", roic_val, "%", 20, 10, False,
         "Kapitalrendite — Bester Einzelindikator für nachhaltigen Moat"),
        (qc3, "Operativmargen", operating_margin, "%", 25, 15, False,
         "Operative Effizienz — zeigt Skalierbarkeit des Geschäftsmodells"),
        (qc4, "Profitmargen", profit_margin, "%", 15, 5, False,
         "Gesamtprofitabilität — nach Steuern und Zinsen"),
        (qc5, "Umsatzwachstum", rev_growth, "%", 10, 3, False,
         "Nachfragedominanz — konsistentes Wachstum trotz Konkurrenz"),
    ]
    for col, lbl, val, suf, good, ok, inv, hint in _moat_metrics:
        v_str = f"{val:.1f}{suf}" if val is not None else "N/A"
        b_cls = "green" if (val is not None and val >= good) else \
                "yellow" if (val is not None and val >= ok) else \
                "red" if val is not None else "gray"
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value">{v_str}</div>
            <div style="margin-top:6px;">
                <span class="metric-badge-{b_cls}">{v_str}</span>
            </div>
            <div class="metric-sub" style="margin-top:8px; font-size:0.7rem;">{hint}</div>
        </div>""", unsafe_allow_html=True)

    # ── Zusammenfassung ────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📋 Fazit</div>", unsafe_allow_html=True)
    _moat_bullets = []
    if gross_margin and gross_margin > 60:
        _moat_bullets.append(f"✅ <strong>Bruttomargen {gross_margin:.1f}%</strong> — starke Preissetzungsmacht, Kunden zahlen Premium.")
    elif gross_margin and gross_margin < 30:
        _moat_bullets.append(f"⚠️ <strong>Bruttomargen {gross_margin:.1f}%</strong> — niedrig, Commodity-ähnliches Geschäft.")
    if roic_val and roic_val > 20:
        _moat_bullets.append(f"✅ <strong>ROIC {roic_val:.1f}%</strong> — exzellente Kapitalallokation, klassischer Buffett-Indikator für Wide Moat.")
    elif roic_val and roic_val < 10:
        _moat_bullets.append(f"⚠️ <strong>ROIC {roic_val:.1f}%</strong> — unter Kapitalkosten, kein struktureller Vorteil erkennbar.")
    if moat["moat_types"]:
        _types_str = ", ".join(t[0] for t in moat["moat_types"])
        _moat_bullets.append(f"🔍 <strong>Erkannte Moat-Treiber:</strong> {_types_str}")
    if moat["market_structure"] in ("Monopol / Reguliert", "Duopol", "Oligopol"):
        _moat_bullets.append(f"🏛️ <strong>Marktstruktur {moat['market_structure']}:</strong> strukturell begrenzte Konkurrenz schützt Margen.")
    if not _moat_bullets:
        _moat_bullets.append("ℹ️ Für eine tiefere Moat-Analyse empfehlen sich Geschäftsberichte, Patentdatenbanken und Branchenanalysen.")

    st.markdown(f"""
    <div class="insight-box">
        <strong style="color:{moat['moat_color']};">{moat['moat_icon']} {moat['moat_width']} — Score {moat['moat_score']}/100</strong><br><br>
        {"<br>".join(_moat_bullets)}
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="color:#37474f; font-size:0.75rem; margin-top:16px; padding:12px 16px;
                background:#0a1628; border-radius:8px; border-left:3px solid #1e3a5f;">
        ⚠️ <em>Hinweis: Diese Einschätzung basiert auf quantitativen Finanzkennzahlen und Branchenheuristiken.
        Eine vollständige Moat-Analyse erfordert qualitative Recherche (Geschäftsberichte, Patente,
        Kundenbindung, Managementqualität). Keine Anlageberatung.</em>
    </div>""", unsafe_allow_html=True)

# ==================== TAB 9: PIOTROSKI F-SCORE ====================
elif _at == 4:
    with st.spinner("Lade Jahresabschlüsse für F-Score…"):
        piotroski = load_piotroski(ticker)

    if piotroski is None:
        st.warning("Jahresabschlussdaten konnten nicht geladen werden.")
    else:
        fs   = piotroski["score"]
        fa   = piotroski["available"]
        fy_t = piotroski["fy_t"]
        fy_t1= piotroski["fy_t1"]

        # ── Score + Interpretation ──────────────────────────────────────
        if fs >= 8:
            fs_color = "#00e676"; fs_label = "Starke Bilanzqualität 🏆"
            fs_text  = "Hohe operative Qualität und finanzielle Substanz. Die Fundamentaldaten stützen das Investment-Narrativ. Klassischer Buffett/Piotroski-Favorit."
        elif fs >= 6:
            fs_color = "#69f0ae"; fs_label = "Solide Substanz ✅"
            fs_text  = "Gute finanzielle Gesundheit mit einzelnen Schwächen. Unternehmen zeigt mehrheitlich positive Bilanzsignale."
        elif fs >= 4:
            fs_color = "#ffd600"; fs_label = "Gemischte Signale ⚠️"
            fs_text  = "Mehrere Kriterien nicht erfüllt. Sorgfältige Prüfung der Schwachstellen empfohlen bevor eine Investitionsentscheidung getroffen wird."
        elif fs >= 2:
            fs_color = "#ff9100"; fs_label = "Schwache Bilanzqualität 🔴"
            fs_text  = "Deutliche Warnsignale in Rentabilität oder Kapitalstruktur. Narrativ möglicherweise nicht durch Bilanzzahlen gedeckt."
        else:
            fs_color = "#ff1744"; fs_label = "Kritisch — Finger weg ⛔"
            fs_text  = "Fundamentale Bilanzprobleme. Marketing-Narrative ohne reale Substanz. Hohe Short-Selling-Anfälligkeit."

        sc1, sc2 = st.columns([1, 2])
        with sc1:
            st.markdown(f"""
            <div class="score-section">
                <div class="score-title">Piotroski F-Score</div>
                <div class="score-num" style="color:{fs_color};">{fs}<span style="font-size:1.5rem; color:#546e7a;">/{fa}</span></div>
                <div class="score-label">{fs_label}</div>
                <div style="color:#546e7a; font-size:0.75rem; margin-top:8px;">
                    Basis: GJ {fy_t} vs {fy_t1}
                </div>
            </div>""", unsafe_allow_html=True)
        with sc2:
            # Score-Balken
            bar_segments = ""
            for i in range(1, 10):
                if i <= fs:
                    seg_color = fs_color
                else:
                    seg_color = "#1e2d45"
                bar_segments += f'<div style="flex:1; height:28px; background:{seg_color}; border-radius:4px; margin:0 2px; display:flex; align-items:center; justify-content:center; font-size:0.72rem; font-weight:700; color:#000a;">{i}</div>'
            st.markdown(f"""
            <div style="display:flex; margin-bottom:16px; padding:8px 0;">{bar_segments}</div>
            <div class="insight-box" style="font-size:0.88rem; line-height:1.6; color:#b0bec5;">{fs_text}</div>
            """, unsafe_allow_html=True)

        # ── 3 Gruppen ──────────────────────────────────────────────────
        groups = {}
        for c in piotroski["criteria"]:
            groups.setdefault(c["group"], []).append(c)

        group_icons = {
            "Rentabilität":       "💰",
            "Kapitalstruktur":    "🏗️",
            "Operative Effizienz":"⚙️",
        }

        for grp_name, items in groups.items():
            grp_pts = sum(1 for c in items if c["passed"] is True)
            grp_max = sum(1 for c in items if c["passed"] is not None)
            icon = group_icons.get(grp_name, "")
            st.markdown(
                f"<div class='section-header'>{icon} {grp_name} — {grp_pts}/{grp_max}</div>",
                unsafe_allow_html=True)

            cols = st.columns(len(items))
            for col, c in zip(cols, items):
                if c["passed"] is True:
                    dot   = "✅"
                    bdr   = "#00e676"
                    badge = '<span class="metric-badge-green">✓ Erfüllt</span>'
                elif c["passed"] is False:
                    dot   = "❌"
                    bdr   = "#ff5252"
                    badge = '<span class="metric-badge-red">✗ Nicht erfüllt</span>'
                else:
                    dot   = "⬜"
                    bdr   = "#37474f"
                    badge = '<span class="metric-badge-gray">N/A</span>'

                col.markdown(f"""
                <div class="metric-card" style="border-left:3px solid {bdr};">
                    <div class="metric-label">{c['name']}</div>
                    <div style="font-size:1.15rem; font-weight:700; color:#eceff1; margin:8px 0;">{c['value']}</div>
                    <div>{badge}</div>
                    <div class="metric-sub" style="margin-top:8px; font-size:0.71rem; line-height:1.4;">{c['hint']}</div>
                </div>""", unsafe_allow_html=True)

        # ── Vigilance-Fazit ────────────────────────────────────────────
        st.markdown("<div class='section-header'>🔍 Vigilance-Check</div>", unsafe_allow_html=True)
        vigilance = []
        for c in piotroski["criteria"]:
            if c["passed"] is False:
                vigilance.append(f"⚠️ <strong>{c['name']}:</strong> {c['hint']}")
        if not vigilance:
            vigilance.append("✅ Alle verfügbaren Kriterien erfüllt — keine Warnsignale in den Bilanzdaten.")
        st.markdown(f"""
        <div class="insight-box">
            <strong>F-Score {fs}/{fa} — {fs_label}</strong><br><br>
            {"<br>".join(vigilance)}
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="color:#37474f; font-size:0.73rem; margin-top:12px; padding:10px 14px;
                    background:#0a1628; border-radius:8px; border-left:3px solid #1e3a5f;">
            ℹ️ <em>Der Piotroski F-Score wurde 2000 von Joseph Piotroski (Stanford) entwickelt.
            Er eignet sich besonders als Screening-Filter für Value-Investoren.
            Score 8–9: hohe Substanz · 4–7: gemischt · 0–3: Warnsignal.
            Datenquelle: Jahresabschlüsse via yFinance. Keine Anlageberatung.</em>
        </div>""", unsafe_allow_html=True)

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

st.markdown("""
<div style="margin-top:60px; border-top:1px solid #1e2d45; padding:28px 0 16px 0;">
    <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-start; gap:16px; margin-bottom:16px;">
        <div>
            <div style="color:#64b5f6; font-size:1.0rem; font-weight:700; margin-bottom:4px;">📈 StocksMB</div>
            <div style="color:#37474f; font-size:0.75rem;">Aktienanalyse Tool · v7</div>
        </div>
        <div style="color:#37474f; font-size:0.75rem; line-height:1.6; max-width:480px; text-align:right;">
            Datenquellen: <span style="color:#546e7a;">Yahoo Finance (yFinance) · Financial Modeling Prep (FMP)</span>
        </div>
    </div>
    <div style="background:#0d1526; border:1px solid #1e2d45; border-radius:10px; padding:14px 18px;">
        <div style="color:#ff8f00; font-size:0.75rem; font-weight:700; margin-bottom:6px; text-transform:uppercase; letter-spacing:1px;">⚠️ Disclaimer — Keine Anlageberatung</div>
        <div style="color:#546e7a; font-size:0.75rem; line-height:1.6;">
            Alle Inhalte auf StocksMB dienen ausschließlich zu Informations- und Bildungszwecken. Die dargestellten Kennzahlen, Analysen, KI-Einschätzungen und Bewertungsmodelle stellen <strong style="color:#78909c;">keine Anlageberatung, Kaufempfehlung oder Aufforderung zum Handel</strong> dar.
            Investitionen in Wertpapiere sind mit Risiken verbunden — der Wert einer Anlage kann steigen oder fallen. Vergangene Wertentwicklungen sind kein verlässlicher Indikator für zukünftige Ergebnisse.
            Bitte konsultiere einen zugelassenen Finanzberater, bevor du Anlageentscheidungen triffst. Alle Daten werden ohne Gewähr bereitgestellt.
        </div>
    </div>
    <div style="text-align:center; color:#263238; font-size:0.7rem; margin-top:14px;">
        © 2025 StocksMB · Erstellt mit Streamlit · Daten von yFinance &amp; FMP
    </div>
</div>
""", unsafe_allow_html=True)
