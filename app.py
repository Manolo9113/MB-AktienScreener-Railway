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
import io

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

    /* Kein horizontales Scrollen auf Mobile */
    html, body {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    .stApp, section[data-testid="stMain"], .main {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    .main .block-container {
        overflow-x: hidden !important;
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        /* Tabellen und breite Elemente scrollbar, aber Container bleibt */
        .stDataFrame, [data-testid="stTable"] {
            overflow-x: auto !important;
            max-width: 100% !important;
        }
        /* Plotly Charts */
        .js-plotly-plot, .plotly {
            max-width: 100% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== LIGHT MODE CSS ====================
if st.session_state.get("light_mode"):
    st.markdown("""<style>
    /* ═══════════════════════════════════════════════════════
       SCHRITT 1: Streamlit CSS-Variablen
    ═══════════════════════════════════════════════════════ */
    :root, [data-theme], .stApp {
        --background-color:           #f5ede2 !important;
        --secondary-background-color: #ede4d8 !important;
        --text-color:                 #1a1208 !important;
        --primary-color:              #1a56db !important;
        --font:                       sans-serif;
    }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 2: Kern-Hintergründe (warmes Crème-Beige)
    ═══════════════════════════════════════════════════════ */
    .stApp, body, html,
    div[data-testid="stAppViewContainer"],
    section[data-testid="stMain"],
    .main, .main .block-container,
    div[data-testid="stVerticalBlock"] {
        background-color: #f5ede2 !important;
        background: #f5ede2 !important;
    }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 3: Sidebar (warmes Leinen)
    ═══════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background: #ece4d8 !important;
        border-right: 1px solid #d4c4b0 !important;
        box-shadow: 2px 0 20px rgba(120,80,30,0.10) !important;
    }
    section[data-testid="stSidebar"] * { color: #1a1208 !important; }
    section[data-testid="stSidebar"] .section-header {
        color: #1a56db !important; border-bottom-color: #d4c4b0 !important; }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 4: Alle Buttons — korrekte Streamlit-Selektoren
       Spezifität muss (0,2,2) erreichen um Global-CSS zu schlagen
    ═══════════════════════════════════════════════════════ */

    /* Reguläre Buttons: Merken, Aktualisieren, Entsperren etc. */
    div[data-testid="stButton"] > button[data-testid="stBaseButton-secondary"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #1e40af !important;
        border: 1.5px solid #bfdbfe !important;
        box-shadow: 0 1px 4px rgba(37,99,235,0.10) !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] > button[data-testid="stBaseButton-secondary"]:hover {
        background: #eff6ff !important;
        background-color: #eff6ff !important;
        border-color: #93c5fd !important;
        color: #1d4ed8 !important;
    }
    div[data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(37,99,235,0.35) !important;
    }

    /* Horizontal-Tab-Buttons (Kennzahlen / Wachstum / Chart etc.) */
    div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"] {
        background: #f1f5f9 !important;
        background-color: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
        color: #64748b !important;
        border-radius: 6px 6px 0 0 !important;
    }
    div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"]:hover {
        background: #e2e8f0 !important;
        background-color: #e2e8f0 !important;
        color: #334155 !important;
        border-color: #c7d2fe !important;
    }
    div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-primary"] {
        background: #2563eb !important;
        background-color: #2563eb !important;
        border: 1px solid #2563eb !important;
        color: #ffffff !important;
        border-radius: 6px 6px 0 0 !important;
        font-weight: 700 !important;
    }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 5: Expander
    ═══════════════════════════════════════════════════════ */
    .streamlit-expanderHeader,
    details summary,
    div[data-testid="stExpander"] details summary {
        background: #eef2ff !important;
        background-color: #eef2ff !important;
        color: #1d4ed8 !important;
        border-radius: 10px !important;
        border: 1px solid #c7d2fe !important;
    }
    details[open] summary { border-radius: 10px 10px 0 0 !important; }
    .streamlit-expanderContent,
    details > div,
    div[data-testid="stExpander"] details > div {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 6: CSS-Klassen (eigene Karten) — Creme-Palette
    ═══════════════════════════════════════════════════════ */
    .header-wrap {
        background: linear-gradient(135deg, #fdf6ee, #f5e8d4) !important;
        border-color: #d4c4b0 !important;
        box-shadow: 0 4px 24px rgba(120,80,30,0.10) !important;
    }
    .metric-card {
        background: #fff8f0 !important;
        border-color: #d8cbbe !important;
        box-shadow: 0 2px 8px rgba(120,80,30,0.08), 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    .score-section {
        background: linear-gradient(135deg, #fff8f0, #f5e8d4) !important;
        border-color: #d4c4b0 !important;
        box-shadow: 0 6px 28px rgba(120,80,30,0.12) !important;
    }
    .header-title { color: #1a1208 !important; }
    .header-sub   { color: #1a56db !important; }
    .metric-label { color: #6b5c4a !important; }
    .metric-value { color: #1a1208 !important; }
    .metric-sub   { color: #8a7868 !important; }
    .score-title  { color: #1a56db !important; }
    .section-header { color: #1a1208 !important; border-bottom-color: #d4c4b0 !important;
                      font-weight: 700 !important; letter-spacing: 2px !important; }
    .insight-box  { background: #eff4ff !important; border-left-color: #1a56db !important; color: #1e3a5f !important; }
    .grok-box     { background: #fdf8ff !important; border-color: #d8b4fe !important; }
    .grok-box h4  { color: #7c3aed !important; }
    .grok-box p, .grok-box ul, .grok-box li { color: #2d2318 !important; }
    .grok-section-title { color: #1a56db !important; border-bottom-color: #d4c4b0 !important; }
    .insider-buy  { color: #15803d !important; }
    .insider-sell { color: #b91c1c !important; }
    .metric-badge-green  { background: rgba(21,128,61,0.12) !important; color: #15803d !important; }
    .metric-badge-yellow { background: rgba(180,83,9,0.12) !important;  color: #b45309 !important; }
    .metric-badge-red    { background: rgba(185,28,28,0.12) !important; color: #b91c1c !important; }
    .metric-badge-gray   { background: rgba(107,114,128,0.12) !important; color: #6b5c4a !important; }

    /* ═══════════════════════════════════════════════════════
       TABELLEN
    ═══════════════════════════════════════════════════════ */
    table, .stDataFrame table,
    div[data-testid="stDataFrame"] table {
        background: #fff8f0 !important;
        border-color: #d4c4b0 !important;
    }
    th, thead th {
        background: #ede4d8 !important;
        color: #1a1208 !important;
        border-color: #d4c4b0 !important;
        font-weight: 700 !important;
    }
    td, tbody td {
        background: #fff8f0 !important;
        color: #1a1208 !important;
        border-color: #ddd2c2 !important;
    }
    tr:nth-child(even) td { background: #f5ede2 !important; }
    tr:hover td { background: #ede4d8 !important; }
    tbody[style*="color:#eceff1"] { color: #1a1208 !important; }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 7: Inline dunkle Hintergründe → Warmes Creme
    ═══════════════════════════════════════════════════════ */
    div[style*="#0d1f35"], div[style*="#0d1f3c"], div[style*="#0a1628"],
    div[style*="#080f1e"], div[style*="#0d1526"], div[style*="#071020"],
    div[style*="#001a2e"], div[style*="#0d2035"], div[style*="#0d1a2e"],
    div[style*="#1a2740"], div[style*="#132040"], div[style*="#080d18"],
    div[style*="#0a1421"], div[style*="#0d2340"], div[style*="#0d1f38"],
    div[style*="#1a2744"], div[style*="#1e2d45"], div[style*="#1a3a5c"],
    div[style*="#0a1a35"], div[style*="#0d2040"], div[style*="#0a1732"],
    div[style*="#0e1c36"], div[style*="#162032"], div[style*="#1e3a5f"],
    div[style*="#152035"], div[style*="#1a304a"], div[style*="#060e1e"] {
        background: #fff8f0 !important;
        border-color: #d4c4b0 !important;
    }
    span[style*="#0d1f3c"], span[style*="#0a1628"], span[style*="#1a2744"] {
        background: #ede4d8 !important; color: #1a56db !important;
    }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 8: Text & Farben
    ═══════════════════════════════════════════════════════ */
    p, span, div, label, li { color: #1a1208; }
    div[data-testid="stMarkdownContainer"] p { color: #2d2318 !important; }
    div[data-testid="stMetricValue"]  { color: #1a1208 !important; }
    div[data-testid="stMetricLabel"]  { color: #6b5c4a !important; }
    .stCaption, small, .caption-text  { color: #6b5c4a !important; }
    hr { border-color: #d4c4b0 !important; }
    a  { color: #1a56db !important; }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 9: Eingabefelder & Selects
    ═══════════════════════════════════════════════════════ */
    input, textarea,
    .stTextInput input,
    .stTextInput > div > div > input {
        background: #fff8f0 !important;
        background-color: #fff8f0 !important;
        border-color: #c4b4a0 !important;
        color: #1a1208 !important;
        box-shadow: 0 1px 4px rgba(120,80,30,0.08) !important;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="popover"] {
        background: #fff8f0 !important;
        color: #1a1208 !important;
        border-color: #d4c4b0 !important;
    }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 10: Tabs
    ═══════════════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        background: #ede4d8 !important; border-color: #d4c4b0 !important; }
    .stTabs [data-baseweb="tab"]    { color: #6b5c4a !important; background: transparent !important; }
    .stTabs [aria-selected="true"]  { background: #1a56db !important; color: #fff !important; }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 11: Fortschritt & Toggle
    ═══════════════════════════════════════════════════════ */
    div[data-testid="stProgressBar"] > div { background-color: #bfdbfe !important; }
    label[data-testid="stWidgetLabel"] p { color: #2d2318 !important; }

    /* ═══════════════════════════════════════════════════════
       SCHRITT 12: Tooltips anpassen
    ═══════════════════════════════════════════════════════ */
    .tt .tt-box {
        background: #1e293b !important; color: #f1f5f9 !important;
        border-color: #334155 !important;
    }
    </style>""", unsafe_allow_html=True)


# ── Farbpalette (Light/Dark) ──────────────────────────────────────────
_lm = st.session_state.get("light_mode", False)
_C_TEXT_PRIMARY = "#1a1208" if _lm else "#eceff1"
_C_TEXT_SEC     = "#2d2318" if _lm else "#b0bec5"
_C_TEXT_MUTED   = "#6b5c4a" if _lm else "#546e7a"
_C_TEXT_MUTED2  = "#8a7868" if _lm else "#90a4ae"
_C_ACCENT       = "#1a56db" if _lm else "#64b5f6"
_C_POSITIVE     = "#15803d" if _lm else "#00e676"
_C_POSITIVE_SFT = "#16a34a" if _lm else "#69f0ae"
_C_NEGATIVE     = "#b91c1c" if _lm else "#ff5252"
_C_NEUTRAL      = "#b45309" if _lm else "#ffd600"
_C_CARD_BG      = "#fff8f0" if _lm else "#0d1f35"
_C_SURFACE      = "#ede4d8" if _lm else "#0d1526"
_C_BORDER       = "#d4c4b0" if _lm else "#1a2744"
_C_CHART_THEME  = "plotly_white" if _lm else "plotly_dark"
_C_CHART_BG     = "#ffffff"      if _lm else "#0a1628"
_C_CHART_PAPER  = "#f5ede2"      if _lm else "rgba(0,0,0,0)"
_C_CHART_PLOT   = "rgba(255,252,248,0.95)" if _lm else "rgba(13,21,38,0.8)"
# ==================== QUOTES ====================
_QUOTES = [
    ("Der Preis ist, was du bezahlst. Wert ist, was du bekommst.", "Warren Buffett"),
    ("Es ist weit besser, ein wunderbares Unternehmen zu einem fairen Preis zu kaufen, als ein faires Unternehmen zu einem wunderbaren Preis.", "Warren Buffett"),
    ("Sei ängstlich, wenn andere gierig sind, und gierig, wenn andere ängstlich sind.", "Warren Buffett"),
    ("Unsere Lieblingshaltezeit ist für immer.", "Warren Buffett"),
    ("Regel Nummer eins: Verliere niemals Geld. Regel Nummer zwei: Vergiss niemals Regel Nummer eins.", "Warren Buffett"),
    ("Risiko entsteht, wenn man nicht weiß, was man tut.", "Warren Buffett"),
    ("Jemand sitzt heute im Schatten, weil jemand anderes vor langer Zeit einen Baum gepflanzt hat.", "Warren Buffett"),
    ("Es dauert 20 Jahre, einen guten Ruf aufzubauen, und fünf Minuten, ihn zu ruinieren.", "Warren Buffett"),
    ("Der Aktienmarkt ist ein Mechanismus zur Übertragung von Geld vom Ungeduldigen zum Geduldigen.", "Warren Buffett"),
    ("In der Welt des Geschäfts sind die gefährlichsten Menschen jene, die nur eine Idee kennen.", "Charlie Munger"),
    ("Invertiere, immer invertiere.", "Charlie Munger"),
    ("Alle intelligenten Investitionen sind Wertinvestitionen — mehr wert zu bekommen, als man zahlt.", "Charlie Munger"),
    ("Zeige mir den Anreiz und ich zeige dir das Ergebnis.", "Charlie Munger"),
    ("Um ein gutes Leben zu führen, braucht man nicht viele Dinge. Man muss vor allem wissen, was man vermeiden muss.", "Charlie Munger"),
    ("Ich habe nichts Neues zu sagen — aber das Alte ist immer noch wahr.", "Charlie Munger"),
    ("Die Börse ist keine Lotterie — sie ist ein Ort, an dem man Unternehmensanteile kauft.", "Peter Lynch"),
    ("Kaufe, was du kennst.", "Peter Lynch"),
    ("Wer keine Zeit hat, seine Aktien zu recherchieren, sollte lieber in Indexfonds investieren.", "Peter Lynch"),
    ("Hinter jeder Aktie steckt ein Unternehmen. Finde heraus, was es macht.", "Peter Lynch"),
    ("Investieren ohne zu forschen ist wie Poker spielen, ohne auf die Karten zu schauen.", "Peter Lynch"),
    ("Der intelligente Investor ist ein Realist, der an Optimisten verkauft und von Pessimisten kauft.", "Benjamin Graham"),
    ("Der Markt ist kurzfristig eine Abstimmungsmaschine, langfristig jedoch eine Waage.", "Benjamin Graham"),
    ("Margin of Safety — das sind die drei wichtigsten Worte beim Investieren.", "Benjamin Graham"),
    ("Der schlimmste Feind des Investors ist wahrscheinlich er selbst.", "Benjamin Graham"),
    ("Ein Unternehmen ist es wert, was ein rationaler Käufer dafür zahlen würde.", "Benjamin Graham"),
    ("Der Markt kann länger irrational bleiben, als man solvent bleiben kann.", "John Maynard Keynes"),
    ("Langfristig sind wir alle tot.", "John Maynard Keynes"),
    ("Wenn die Fakten sich ändern, ändere ich meine Meinung. Was tun Sie?", "John Maynard Keynes"),
    ("Schwierig ist es, neue Ideen zu verbreiten — nicht weil alte Ideen falsch sind, sondern weil sie so tief verwurzelt sind.", "John Maynard Keynes"),
    ("Die Wirtschaft ist eine Wissenschaft der Auswahlmöglichkeiten unter Knappheit.", "John Maynard Keynes"),
    ("Der Unterschied zwischen Glücksspiel und Spekulation ist oft nur eine Frage der Zeiträume.", "Nassim Taleb"),
    ("Sei nicht besorgt, ob du recht hast oder nicht. Sei besorgt, wie viel du verlierst, wenn du falsch liegst.", "Nassim Taleb"),
    ("Überlebe zuerst; reich werden kommt danach.", "Nassim Taleb"),
    ("Schwarze Schwäne dominieren die Geschichte — seltene Ereignisse bewegen die Welt.", "Nassim Taleb"),
    ("Komplexität verbirgt Fragilität.", "Nassim Taleb"),
    ("Geld sucht sich seinen eigenen Weg — man muss nur da sein, wenn es ankommt.", "Jesse Livermore"),
    ("Ein Spekulant muss sich selbst kennen und seine Grenzen akzeptieren.", "Jesse Livermore"),
    ("Nie verliere den Faden. Die Basistrends des Marktes sind das Wichtigste.", "Jesse Livermore"),
    ("Märkte sind niemals falsch — nur Meinungen sind es.", "Jesse Livermore"),
    ("Geduld ist eine Tugend beim Investieren — und das Warten auf den richtigen Moment das Schwierigste.", "Jesse Livermore"),
    ("Märkte sind nicht effizient — sie werden von Reflexivität gesteuert.", "George Soros"),
    ("Es spielt keine Rolle, ob ich recht habe oder falsch liege. Wichtig ist, wie viel ich verdiene, wenn ich richtig liege, und wie viel ich verliere, wenn ich falsch liege.", "George Soros"),
    ("Der beste Weg, einen Fehler zu erkennen, ist, bereit zu sein, ihn zuzugeben.", "George Soros"),
    ("Finanzmärkte sind im Allgemeinen unberechenbar.", "George Soros"),
    ("Investiere in außergewöhnliche Menschen, bevor du in außergewöhnliche Unternehmen investierst.", "Philip Fisher"),
    ("Die Zeit eines Investors ist am besten genutzt, um nach dem Wenigen Ausschau zu halten, das wirklich außergewöhnlich ist.", "Philip Fisher"),
    ("Die meisten Anlagen schlagen den Markt nicht — es sei denn, der Investor hat einen echten Informationsvorsprung.", "Philip Fisher"),
    ("Kaufe in Zeiten der Pessimismus und verkaufe in Zeiten des Optimismus.", "John Templeton"),
    ("Die vier gefährlichsten Worte beim Investieren sind: Diesmal ist es anders.", "John Templeton"),
    ("Bull-Märkte werden im Pessimismus geboren, wachsen in der Skepsis, reifen im Optimismus und sterben in der Euphorie.", "John Templeton"),
    ("Der einfachste Weg zu Reichtum ist, bescheidener zu sein als dein Einkommen.", "John Templeton"),
    ("Der wichtigste Schlüssel zum Anlageerfolg ist das Verständnis des Konjunkturzyklus.", "Ray Dalio"),
    ("Schmerz plus Reflexion gleich Fortschritt.", "Ray Dalio"),
    ("Seien Sie offen für die Möglichkeit, dass Sie falsch liegen.", "Ray Dalio"),
    ("Die größte Gefahr für einen Investor ist nicht das Risiko — es ist die Risikovermeidung.", "Howard Marks"),
    ("Gute Zeiten bringen schlechte Entscheidungen hervor.", "Howard Marks"),
    ("Das Risiko liegt nicht im Verlust — es liegt in der Unwissenheit.", "Howard Marks"),
    ("Der Markt belohnt Geduld und bestraft Ungeduld.", "Carl Icahn"),
    ("In der Investmentwelt haben die Geduldigen mehr als die Aktiven.", "Seth Klarman"),
    ("Sicherheitsmarge ist der zentrale Begriff des Investierens.", "Seth Klarman"),
    ("Der Markt ist für kurze Zeit eine Popularitätsmaschine, aber auf lange Sicht eine Waage.", "Joel Greenblatt"),
    ("Kaufe gute Unternehmen zu günstigen Preisen — das ist die ganze Investmentstrategie.", "Joel Greenblatt"),
    ("Folge dem Trend, bis er sich ändert.", "William O'Neil"),
    ("Diversifikation ist der einzige kostenlose Mittagstisch beim Investieren.", "John Bogle"),
    ("Einfachheit ist die höchste Form der Eleganz — auch beim Investieren.", "John Bogle"),
    ("An der Börse ist der Patient der Lehrmeister des Ungeduldigen.", "André Kostolany"),
    ("Kaufen, wenn die Kanonen donnern, verkaufen, wenn die Violinen spielen.", "André Kostolany"),
    ("Wer die Börse versteht, macht Geld; wer sie nicht versteht, auch — aber viel langsamer.", "André Kostolany"),
    ("Geld allein macht nicht glücklich — aber es beruhigt die Nerven.", "André Kostolany"),
    ("Der Wohlstand der Nationen entspringt der Arbeitsteilung und dem freien Handel.", "Adam Smith"),
    ("Nicht vom Wohlwollen des Bäckers, des Metzgers oder des Brauers erwarten wir unser Mittagessen, sondern von ihrem Eigeninteresse.", "Adam Smith"),
    ("Die Preissignale des Marktes sind die effizienteste Form der Informationsübertragung.", "Friedrich Hayek"),
    ("Freiwilliger Austausch zwischen Individuen ist die Grundlage einer freien Gesellschaft.", "Milton Friedman"),
    ("Inflation ist überall und immer ein monetäres Phänomen.", "Milton Friedman"),
    ("Im Zweifel kultiviere deinen eigenen Garten.", "Voltaire"),
    ("Das Beste ist der Feind des Guten.", "Voltaire"),
    ("Wir sind, was wir wiederholt tun. Vortrefflichkeit ist daher keine Handlung, sondern eine Gewohnheit.", "Aristoteles"),
    ("Glück ist die Tätigkeit der Seele in Übereinstimmung mit der Tugend.", "Aristoteles"),
    ("Beschränke dich auf das Wesentliche, das heißt: auf das, was Vernunft und Natur erfordern.", "Marcus Aurelius"),
    ("Beherrsche deine Gedanken — sonst beherrschen sie dich.", "Marcus Aurelius"),
    ("Nicht die Dinge selbst beunruhigen die Menschen, sondern die Meinungen über die Dinge.", "Epiktet"),
    ("Es ist nicht arm, wer wenig hat, sondern wer mehr begehrt.", "Seneca"),
    ("Nutze die Zeit, bevor die Zeit vergeht.", "Seneca"),
    ("Das Leben ist lang genug, wenn man es richtig nutzt.", "Seneca"),
]

# ==================== API KEY ====================
import os

FMP_API_KEY    = os.getenv("FMP_API_KEY", "")
NEWS_API_KEY   = os.getenv("NEWS_API_KEY", "")
XAI_API_KEY    = os.getenv("XAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SEC_API_KEY    = os.getenv("SEC_API_KEY", "")   # sec-api.io (Segment Revenue + XBRL)
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY", "")
PORTFOLIO_PASSWORD = os.getenv("PORTFOLIO_PASSWORD", "")  # leer = kein Schutz

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

def _wl_load_file() -> list[dict]:
    import json as _json
    _path = "/data/watchlist.json" if os.path.isdir("/data") else "/tmp/watchlist.json"
    try:
        with open(_path) as _f:
            return _json.load(_f)
    except Exception:
        return []

def _wl_save_file(watchlist: list[dict]) -> None:
    import json as _json
    _path = "/data/watchlist.json" if os.path.isdir("/data") else "/tmp/watchlist.json"
    try:
        with open(_path, "w") as _f:
            _json.dump(watchlist, _f)
    except Exception:
        pass

def _portfolio_file_path() -> str:
    """Gibt den Pfad zur gespeicherten Portfolio-CSV zurück.
    Railway Volume: /data (persistent). Fallback: /tmp (nur für lokale Entwicklung)."""
    import os
    data_dir = "/data" if os.path.isdir("/data") else "/tmp"
    return os.path.join(data_dir, "portfolio_default.csv")

def _sb_save_portfolio(csv_bytes: bytes) -> bool:
    """Portfolio-CSV auf Railway Volume (/data) oder /tmp speichern."""
    try:
        import os
        path = _portfolio_file_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(csv_bytes)
        return True
    except Exception:
        return False

def _sb_load_portfolio() -> tuple:
    """Portfolio-CSV vom Railway Volume laden. Gibt (bytes, Datum-str) oder (None, None) zurück."""
    try:
        import os, datetime as _dt
        path = _portfolio_file_path()
        if os.path.exists(path):
            with open(path, "rb") as f:
                raw = f.read()
            mtime = os.path.getmtime(path)
            date_str = _dt.datetime.fromtimestamp(mtime).strftime("%d.%m.%Y")
            return raw, date_str
    except Exception:
        pass
    return None, None

def _save_portfolio_settings(excluded_isins: list, manual_prices: dict, manual_shares: dict = None) -> bool:
    """Speichert Portfolio-Korrekturen (Ausschlüsse + manuelle Kurse + manuelle Anteile) auf Railway Volume /data."""
    try:
        import os, json
        data_dir = "/data" if os.path.isdir("/data") else "/tmp"
        path = os.path.join(data_dir, "portfolio_settings.json")
        with open(path, "w") as f:
            json.dump({
                "excluded_isins": excluded_isins,
                "manual_prices": manual_prices,
                "manual_shares": manual_shares or {},
            }, f)
        return True
    except Exception:
        return False

def _load_portfolio_settings() -> dict:
    """Lädt Portfolio-Korrekturen vom Railway Volume. Gibt {'excluded_isins': [], 'manual_prices': {}, 'manual_shares': {}} zurück."""
    try:
        import os, json
        data_dir = "/data" if os.path.isdir("/data") else "/tmp"
        path = os.path.join(data_dir, "portfolio_settings.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _load_isin_sector_cache() -> dict:
    """ISIN → {quote_type, sector, recommendation} aus Railway Volume. Überlebt Deploys."""
    try:
        import os, json
        path = os.path.join("/data" if os.path.isdir("/data") else "/tmp", "isin_sector_cache.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def _save_isin_sector_cache(cache: dict) -> None:
    """Speichert ISIN-Sektor-Cache auf Railway Volume."""
    try:
        import os, json
        path = os.path.join("/data" if os.path.isdir("/data") else "/tmp", "isin_sector_cache.json")
        with open(path, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass

def _pf_disk_save(cache_name: str, data) -> None:
    """Speichert berechnete Portfolio-Daten auf Railway Volume /data (überlebt Deploys)."""
    try:
        import os, pickle
        path = os.path.join("/data" if os.path.isdir("/data") else "/tmp", f"pf_{cache_name}.pkl")
        with open(path, "wb") as f:
            pickle.dump(data, f)
    except Exception:
        pass

def _pf_disk_load(cache_name: str, max_age_hours: float = 0):
    """Lädt gecachte Portfolio-Daten von Railway Volume /data. Gibt None zurück wenn nicht vorhanden oder zu alt."""
    try:
        import os, pickle, time
        path = os.path.join("/data" if os.path.isdir("/data") else "/tmp", f"pf_{cache_name}.pkl")
        if os.path.exists(path):
            if max_age_hours > 0 and (time.time() - os.path.getmtime(path)) / 3600 >= max_age_hours:
                return None
            with open(path, "rb") as f:
                return pickle.load(f)
    except Exception:
        pass
    return None


# ==================== CACHE ====================
@st.cache_data(ttl=3600)
def _patch_info_from_statements(stock: "yf.Ticker", info: dict) -> dict:
    """
    Für japanische / nicht-US Aktien liefert yfinance.info oft 0/None für Margen,
    Wachstum und FCF. Fallback: direkt aus GuV, Cashflow und Bilanz berechnen.
    FCF-Patch läuft IMMER. Fuzzy row-matching deckt JP/EU Labelabweichungen ab.
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
        """Exact match first, then case-insensitive substring match."""
        idx_lower = {str(i).lower(): i for i in df.index}
        for n in names:
            if n in df.index:
                return df.loc[n]
        for n in names:
            hit = idx_lower.get(n.lower())
            if hit is not None:
                return df.loc[hit]
        # Substring fallback: find first index entry containing any keyword
        for n in names:
            key = n.lower().replace(" ", "")
            for orig in df.index:
                if key in str(orig).lower().replace(" ", ""):
                    return df.loc[orig]
        return None

    # ── FCF immer patchen wenn 0/None (häufig bei JP/EU) ─────────────────
    def _safe_num(series_row, col_idx=0):
        """Liest Wert aus einer DataFrame-Zeile; gibt 0 zurück bei NaN/None."""
        try:
            f = float(series_row.iloc[col_idx])
            return f if f == f else 0.0   # f!=f ↔ NaN
        except Exception:
            return 0.0

    if not info.get("freeCashflow"):
        ocf_info = info.get("operatingCashflow")
        if ocf_info:
            capex_info = info.get("capitalExpenditures") or 0
            info["freeCashflow"] = int(ocf_info - abs(capex_info))
        else:
            cf = _get_df("cash_flow", "cashflow")
            if cf is not None and len(cf.columns) >= 1:
                fcf_r = _row(cf, "Free Cash Flow", "FreeCashFlow", "Freecashflow",
                             "Free Cashflow", "Net Free Cash Flow")
                ocf_r = _row(cf,
                             "Operating Cash Flow", "OperatingCashFlow",
                             "Total Cash From Operating Activities",
                             "Cash From Operations", "CashFlowFromOperations",
                             "Net Cash From Operating Activities",
                             "Net Cash Provided By Operating Activities",
                             "Cash Flows From Operating Activities")
                cap_r = _row(cf,
                             "Capital Expenditure", "CapitalExpenditure",
                             "Capital Expenditures", "Capex",
                             "Purchase Of Property Plant And Equipment",
                             "Purchases of PPE", "PurchaseOfPPE",
                             "Acquisition Of PPE", "Purchase Of Fixed Assets",
                             "Capital Spending")
                if fcf_r is not None:
                    v = _safe_num(fcf_r)
                    if v: info["freeCashflow"] = int(v)
                elif ocf_r is not None:
                    ocf = _safe_num(ocf_r)
                    cap = _safe_num(cap_r) if cap_r is not None else 0.0
                    if ocf: info["freeCashflow"] = int(ocf + cap)  # cap is negative in statements

    # ── Margen + Wachstum + earningsGrowth: patchen wenn alle fehlen ─────
    needs_margin_patch = not any([
        info.get("grossMargins"), info.get("operatingMargins"),
        info.get("profitMargins"), info.get("revenueGrowth"),
    ])
    fs = _get_df("income_stmt", "financials") if needs_margin_patch or not info.get("earningsGrowth") else None
    if fs is not None and len(fs.columns) >= 2:
        rev = _row(fs, "Total Revenue", "TotalRevenue", "Revenue", "Net Revenue")
        gp  = _row(fs, "Gross Profit", "GrossProfit")
        op  = _row(fs, "Operating Income", "OperatingIncome", "EBIT",
                   "Operating Profit", "OperatingProfit")
        ni  = _row(fs, "Net Income", "NetIncome",
                   "Net Income Common Stockholders",
                   "Net Income Applicable To Common Shares",
                   "Net Profit", "Profit After Tax")

        if needs_margin_patch and rev is not None:
            r0 = _safe_num(rev, 0)
            r1 = _safe_num(rev, 1)
            if r0 and r1:
                info["revenueGrowth"] = (r0 / r1) - 1
            if r0:
                info["totalRevenue"] = int(r0)
                if gp is not None: info["grossMargins"]     = _safe_num(gp) / r0
                if op is not None: info["operatingMargins"] = _safe_num(op) / r0
                if ni is not None: info["profitMargins"]    = _safe_num(ni) / r0

        # earningsGrowth: always compute from net income YoY if not in info
        if not info.get("earningsGrowth") and ni is not None and len(ni) >= 2:
            ni0 = _safe_num(ni, 0)
            ni1 = _safe_num(ni, 1)
            if ni1 and ni1 > 0:
                info["earningsGrowth"] = (ni0 / ni1) - 1

    # ── marketCap Fallback (häufig None bei JP/EU Aktien → FCF Yield = 0) ─
    if not info.get("marketCap"):
        _price = (info.get("currentPrice") or info.get("regularMarketPrice")
                  or info.get("previousClose") or info.get("open") or 0)
        _shares = (info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
                   or info.get("floatShares") or 0)
        if _price and _shares:
            info["marketCap"] = int(_price * _shares)

    return info


@st.cache_data(ttl=300)   # 5 min — kurze TTL damit Kurs + Earnings-Reaktionen aktuell sind
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
    """Jahresabschluss: Umsatz, Nettogewinn, EPS, FCF, EBITDA, CapEx, Goodwill, Debt, Cash (5 Jahre)."""
    stock = yf.Ticker(ticker)
    rev = pd.Series(dtype=float)
    net = pd.Series(dtype=float)
    eps = pd.Series(dtype=float)
    fcf = pd.Series(dtype=float)
    ebitda_s = pd.Series(dtype=float)
    shares_ann = pd.Series(dtype=float)
    capex_s = pd.Series(dtype=float)
    goodwill_s = pd.Series(dtype=float)
    debt_s = pd.Series(dtype=float)
    cash_s = pd.Series(dtype=float)
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
            for row in ["Capital Expenditure", "Purchase Of Property Plant And Equipment"]:
                if row in cf.index:
                    raw = cf.loc[row].dropna().sort_index()
                    capex_s = raw.abs()
                    break
    except Exception:
        pass
    try:
        bs = stock.balance_sheet
        if bs is not None and not bs.empty:
            for row in ["Goodwill", "Goodwill And Other Intangible Assets"]:
                if row in bs.index:
                    goodwill_s = bs.loc[row].dropna().sort_index(); break
            for row in ["Total Debt", "Long Term Debt And Capital Lease Obligation",
                        "Long Term Debt", "Net Debt"]:
                if row in bs.index:
                    debt_s = bs.loc[row].dropna().sort_index().abs(); break
            for row in ["Cash And Cash Equivalents",
                        "Cash Cash Equivalents And Short Term Investments",
                        "Cash And Short Term Investments"]:
                if row in bs.index:
                    cash_s = bs.loc[row].dropna().sort_index(); break
    except Exception:
        pass
    return rev, net, eps, fcf, shares_ann, ebitda_s, capex_s, goodwill_s, debt_s, cash_s

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


@st.cache_data(ttl=3600, show_spinner=False)
def load_analyst_estimates(ticker: str) -> dict:
    """Analyst EPS + Revenue forward estimates. FMP primary, yfinance fallback."""
    out = {"eps": [], "rev": []}

    # FMP earnings estimates
    if FMP_API_KEY:
        try:
            r = requests.get(
                f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}",
                params={"apikey": FMP_API_KEY, "period": "annual", "limit": 4},
                timeout=10,
            )
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list):
                    for item in data:
                        yr = str(item.get("date", ""))[:4]
                        eps_est = item.get("estimatedEpsAvg")
                        rev_est = item.get("estimatedRevenueAvg")
                        n_an = item.get("numberAnalystEstimatedEps") or item.get("numberAnalystEstimatedRevenue")
                        if eps_est:
                            out["eps"].append({"year": yr, "estimate": float(eps_est), "analysts": n_an})
                        if rev_est:
                            out["rev"].append({"year": yr, "estimate": float(rev_est), "analysts": n_an})
        except Exception:
            pass

    # yfinance fallback for EPS estimates
    if not out["eps"]:
        try:
            stock = yf.Ticker(ticker)
            try:
                ee = stock.get_earnings_estimate()
            except Exception:
                ee = getattr(stock, "earnings_estimate", None)
            if ee is not None and not ee.empty:
                for period, row in ee.iterrows():
                    avg = row.get("avg") or row.get("Avg Estimate")
                    n = row.get("numberOfAnalysts") or row.get("No. of Analysts")
                    if avg is not None and pd.notna(avg):
                        out["eps"].append({"year": str(period), "estimate": float(avg), "analysts": int(n) if n and pd.notna(n) else None})
        except Exception:
            pass

    # yfinance fallback for revenue estimates
    if not out["rev"]:
        try:
            stock = yf.Ticker(ticker)
            try:
                re_df = stock.get_revenue_estimate()
            except Exception:
                re_df = getattr(stock, "revenue_estimate", None)
            if re_df is not None and not re_df.empty:
                for period, row in re_df.iterrows():
                    avg = row.get("avg") or row.get("Avg Estimate")
                    n = row.get("numberOfAnalysts") or row.get("No. of Analysts")
                    if avg is not None and pd.notna(avg):
                        out["rev"].append({"year": str(period), "estimate": float(avg), "analysts": int(n) if n and pd.notna(n) else None})
        except Exception:
            pass

    return out


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

def fmt_large(value, sym=""):
    if value is None:
        return "N/A"
    abs_v = abs(value)
    sign  = "-" if value < 0 else ""
    if abs_v >= 1e12:
        return f"{sign}{sym}{abs_v/1e12:.2f}T"
    elif abs_v >= 1e9:
        return f"{sign}{sym}{abs_v/1e9:.1f}B"
    elif abs_v >= 1e6:
        return f"{sign}{sym}{abs_v/1e6:.1f}M"
    return f"{sign}{sym}{abs_v:,.0f}"

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
        return _C_POSITIVE
    elif s >= 50:
        return _C_NEUTRAL
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
        market_color = _C_NEUTRAL
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
        moat_color = _C_POSITIVE
        moat_icon  = "🏰"
        moat_desc  = "Breiter, nachhaltiger Wettbewerbsvorteil. Das Unternehmen kann voraussichtlich über 20+ Jahre überdurchschnittliche Renditen erwirtschaften."
    elif moat_score >= 35:
        moat_width = "Narrow Moat"
        moat_color = _C_NEUTRAL
        moat_icon  = "🛡️"
        moat_desc  = "Schmaler Wettbewerbsvorteil. Vorteil vorhanden, aber Risiko der Erosion durch Technologie- oder Marktveränderungen."
    else:
        moat_width = "No Moat"
        moat_color = _C_NEGATIVE
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

    # Kerninflation (Core CPI ex. Food & Energy, YoY)
    core_cpi = _fred_last("CPILFESL", 13)
    if len(core_cpi) >= 13:
        core_yoy = round((core_cpi[0] / core_cpi[12] - 1) * 100, 1)
        out["macro"]["🇺🇸 Kerninflation"] = {"value": core_yoy, "unit": "%"}
        out["core_cpi"] = core_yoy

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
    # HICP ist ein Indexwert (Basisjahr 2015=100), daher YoY selbst berechnen
    ez_cpi = _fred_last("CP0000EZ19M086NEST", 13)
    if len(ez_cpi) >= 13:
        ez_yoy = (ez_cpi[0] / ez_cpi[12] - 1) * 100
        out["macro"]["🇪🇺 Inflation"] = {"value": round(ez_yoy, 1), "unit": "%"}

    # EZB Einlagesatz
    ecb = _fred_last("ECBDFR")
    if ecb:
        out["macro"]["🇪🇺 EZB Rate"] = {"value": ecb[0], "unit": "%"}

    # ── Japan / China (einfache Proxies) ──────────────────────────────
    jp_cpi = _fred_last("JPNCPIALLMINMEI", 13)
    if len(jp_cpi) >= 13:
        jp_yoy = (jp_cpi[0] / jp_cpi[12] - 1) * 100
        out["macro"]["🇯🇵 Inflation"] = {"value": round(jp_yoy, 1), "unit": "%"}

    # ── BIP-Wachstum YoY — parallel fetch ───────────────────────────────
    out["gdp"] = {}
    _gdp_specs = [
        ("🇺🇸 USA",         "GDPC1",              None),
        ("🇪🇺 Eurozone",    "CLVMEURSCAB1GQEA19", "NAEXKP01EZQ189S"),
        ("🇩🇪 Deutschland", "CLVMDEAM195S",        "NAEXKP01DEQ189S"),
        ("🇨🇳 China",       "CHNGDPNQDSMEI",       None),
        ("🇯🇵 Japan",       "CLVMJPAM195S",        "NAEXKP01JPQ189S"),
        ("🇬🇧 UK",          "CLVMGBAM195S",        "NAEXKP01GBQ189S"),
        ("🇮🇳 Indien",      "INDGDPNQDSMEI",       None),
    ]

    def _fetch_gdp_yoy(spec):
        gname, gsid, gsid2 = spec
        try:
            gv = _fred_last(gsid, 13)
            if not gv and gsid2:
                gv = _fred_last(gsid2, 13)
            if len(gv) >= 13 and gv[12]:
                return gname, round((gv[0] / gv[12] - 1) * 100, 1)
            if len(gv) >= 5 and gv[4]:
                return gname, round((gv[0] / gv[4] - 1) * 100, 1)
        except Exception:
            pass
        return gname, None

    try:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4) as _gdp_ex:
            for _gname, _gval in _gdp_ex.map(_fetch_gdp_yoy, _gdp_specs):
                if _gval is not None:
                    out["gdp"][_gname] = _gval
    except Exception:
        for _spec in _gdp_specs:
            _gname, _gval = _fetch_gdp_yoy(_spec)
            if _gval is not None:
                out["gdp"][_gname] = _gval

    # ── Misery Index (Arbeitslosigkeit + Inflation) ──────────────────────
    out["misery"] = {}
    _us_unemp_v = out["macro"].get("🇺🇸 Arbeitslosigkeit", {}).get("value")
    _us_infl_v  = out["macro"].get("🇺🇸 Inflation",        {}).get("value")
    if _us_unemp_v is not None and _us_infl_v is not None:
        out["misery"]["🇺🇸 USA"] = round(_us_unemp_v + _us_infl_v, 1)

    _ez_unemp_raw = _fred_last("LRHUTTTTEZM156S")
    if _ez_unemp_raw:
        out["ez_unemployment"] = round(_ez_unemp_raw[0], 1)
        _ez_infl_v = out["macro"].get("🇪🇺 Inflation", {}).get("value")
        if _ez_infl_v is not None:
            out["misery"]["🇪🇺 Eurozone"] = round(_ez_unemp_raw[0] + _ez_infl_v, 1)

    # ── Konjunkturindikatoren ────────────────────────────────────────────
    _umcs = _fred_last("UMCSENT")
    if _umcs:
        out["consumer_sentiment"] = round(_umcs[0], 1)

    _t10y2y = _fred_last("T10Y2Y")
    if _t10y2y is not None and len(_t10y2y):
        out["yield_curve"] = round(_t10y2y[0], 2)

    # ── Buffett-Indikator: Wilshire 5000 / US GDP ────────────────────
    # Wilshire 5000 Full Cap Index-Level ≈ Gesamtmarktkapitalisierung USA in Mrd. USD
    # GDP (FRED) ebenfalls in Mrd. USD → direkt vergleichbar
    _w5000_val: float = 0.0
    try:
        _w5000_h = yf.Ticker("^W5000").history(period="5d")
        _gdp = _fred_last("GDP")
        if not _w5000_h.empty and _gdp and _gdp[0]:
            _w5000_val = float(_w5000_h["Close"].iloc[-1])
            _bi = round(_w5000_val / _gdp[0] * 100, 1)
            out["buffett"] = _bi
    except Exception:
        pass

    # ── Shiller CAPE (P/E 10, zyklisch adjustiert) ────────────────────
    def _multpl_current(url: str) -> "float | None":
        """Scrape current-value von multpl.com. Sucht Zahl im 400-Zeichen-Fenster."""
        try:
            r = requests.get(url, timeout=8,
                             headers={"User-Agent": "Mozilla/5.0 (compatible; StocksMB/1.0)"})
            if not r.ok:
                return None
            txt = r.text
            for marker in ('id="current-value"', "id='current-value'"):
                idx = txt.find(marker)
                if idx >= 0:
                    window = txt[idx: idx + 400]
                    m = re.search(r'(\d+\.\d+)', window)
                    if m:
                        return float(m.group(1))
            return None
        except Exception:
            return None

    _cape_val = _multpl_current("https://www.multpl.com/shiller-pe")
    if _cape_val:
        out["shiller_cape"] = _cape_val

    # ── Market Cap / GNP ──────────────────────────────────────────────
    try:
        _gnp = _fred_last("GNP") or _fred_last("GDP")
        if _w5000_val and _gnp and _gnp[0]:
            out["mcap_gnp"] = round(_w5000_val / _gnp[0] * 100, 1)
    except Exception:
        pass

    # ── Tobin's Q Proxy (S&P 500 Price/Book, multpl.com) ─────────────
    _pb_val = _multpl_current("https://www.multpl.com/s-p-500-price-to-book-value")
    if _pb_val:
        out["tobins_q"] = _pb_val

    # ── Unternehmensgewinnmarge (Hussman-Basis) ────────────────────────
    try:
        _cprofit = _fred_last("CP", 1)
        _gdp_now = _fred_last("GDP", 1)
        if _cprofit and _gdp_now and _gdp_now[0]:
            out["corp_margin"] = round(_cprofit[0] / _gdp_now[0] * 100, 1)
    except Exception:
        pass

    # ── S&P 500 PEG Ratio (kombiniert: yfinance + multpl.com) ────────────
    try:
        _spy = yf.Ticker("SPY")
        _spy_info = _spy.info
        _sp_pe = _spy_info.get("trailingPE")
        _sp_eg_a = None   # Option A: yfinance
        _sp_eg_b = None   # Option B: multpl.com

        # ── Option A-1: earningsGrowth direkt aus yfinance ──
        _sp_eg_yf = (_spy_info.get("earningsGrowth") or 0) * 100
        if 1 < _sp_eg_yf < 50:
            _sp_eg_a = round(_sp_eg_yf, 1)

        # ── Option A-2: aus forwardEps / trailingEps berechnen ──
        if not _sp_eg_a:
            _t_eps = _spy_info.get("trailingEps") or 0
            _f_eps = _spy_info.get("forwardEps") or 0
            if _t_eps > 0 and _f_eps > 0:
                _computed = (_f_eps / _t_eps - 1) * 100
                if 1 < _computed < 50:
                    _sp_eg_a = round(_computed, 1)

        # ── Option B: multpl.com S&P 500 EPS-Tabelle scrapen ──
        try:
            _mr = requests.get(
                "https://www.multpl.com/s-p-500-eps/table/by-month",
                timeout=6,
                headers={"User-Agent": "Mozilla/5.0 (compatible; StocksMB/1.0)"},
            )
            if _mr.ok:
                # Tabelle: <td>Apr 1, 2025</td><td>230.00</td>
                _eps_rows = re.findall(
                    r"<td[^>]*>([A-Z][a-z]{2}\s+\d+,\s+\d{4})</td>\s*<td[^>]*>([\d.]+)</td>",
                    _mr.text,
                )
                if len(_eps_rows) >= 13:
                    _eps_now = float(_eps_rows[0][1])
                    _eps_1y  = float(_eps_rows[12][1])
                    if _eps_1y > 0:
                        _b_growth = round((_eps_now / _eps_1y - 1) * 100, 1)
                        if 0 < _b_growth < 60:
                            _sp_eg_b = _b_growth
        except Exception:
            pass

        # ── Quellen kombinieren ──────────────────────────────
        if _sp_eg_a and _sp_eg_b:
            if abs(_sp_eg_a - _sp_eg_b) <= 8:
                _sp_eg_final = round((_sp_eg_a + _sp_eg_b) / 2, 1)
                _peg_src = f"Ø yfinance {_sp_eg_a:.1f}% + multpl.com {_sp_eg_b:.1f}%"
            else:
                _sp_eg_final = _sp_eg_b  # bei Divergenz: externe Quelle bevorzugen
                _peg_src = f"multpl.com {_sp_eg_b:.1f}% (yfinance {_sp_eg_a:.1f}% abweichend)"
        elif _sp_eg_a:
            _sp_eg_final = _sp_eg_a
            _peg_src = "yfinance forward EPS"
        elif _sp_eg_b:
            _sp_eg_final = _sp_eg_b
            _peg_src = "multpl.com"
        else:
            _sp_eg_final = None
            _peg_src = ""

        # immer trailing + forward KGV speichern
        if _sp_pe:
            out["sp500_trailing_pe"] = round(_sp_pe, 1)
        _sp_fpe = _spy_info.get("forwardPE")
        if _sp_fpe:
            out["sp500_forward_pe"] = round(_sp_fpe, 1)

        if _sp_pe and _sp_eg_final and _sp_eg_final > 0:
            out["sp500_peg"]        = round(_sp_pe / _sp_eg_final, 2)
            out["sp500_peg_source"] = _peg_src
            out["sp500_eg"]         = _sp_eg_final
        elif _sp_pe:
            out["sp500_pe"] = round(_sp_pe, 1)
    except Exception:
        pass

    # ── ERP (Equity Risk Premium) ─────────────────────────────────────
    # = Forward Earnings Yield (1/ForwardPE × 100) − 10J Treasury
    try:
        _erp_pe  = out.get("sp500_forward_pe") or out.get("sp500_trailing_pe")
        _erp_t10 = out.get("macro", {}).get("🇺🇸 10J Rendite", {}).get("value")
        if _erp_pe and _erp_pe > 0 and _erp_t10:
            out["erp"] = round(100.0 / _erp_pe - _erp_t10, 2)
    except Exception:
        pass

    # ── Margin-adjustiertes KGV (Hussman-Stil) ────────────────────────
    try:
        _ma_pe_base  = out.get("sp500_trailing_pe") or out.get("sp500_pe")
        _curr_margin = out.get("corp_margin")
        if _ma_pe_base and _curr_margin and _curr_margin > 0:
            out["margin_adj_pe"] = round(_ma_pe_base * (_curr_margin / 7.5), 1)
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


@st.cache_data(ttl=3600)
def load_extended_macro() -> dict:
    """
    Erweitertes Makro-Dashboard: 7 Module mit z-Score-Normalisierung.
    Datenquellen: FRED (CSV, kein API-Key), yfinance.
    Gibt Modul-Daten + Zeitreihen + Regime-Score zurück.
    """
    out: dict = {"modules": {}, "regime": {}}
    _today = _dt.date.today().strftime("%Y-%m-%d")
    _start2y = (_dt.date.today() - _dt.timedelta(days=730)).strftime("%Y-%m-%d")
    _start5y = (_dt.date.today() - _dt.timedelta(days=5 * 365)).strftime("%Y-%m-%d")

    def _fred_ts(sid: str, start: str = _start2y) -> pd.Series:
        """Holt FRED-Zeitreihe als pd.Series (kein API-Key nötig)."""
        try:
            r = requests.get(
                f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}",
                timeout=10,
            )
            if not r.ok:
                return pd.Series(dtype=float, name=sid)
            dates, vals = [], []
            for line in r.text.strip().split("\n")[1:]:
                p = line.split(",")
                if len(p) == 2 and p[1].strip() not in (".", ""):
                    try:
                        d = pd.to_datetime(p[0].strip())
                        if d >= pd.to_datetime(start):
                            dates.append(d)
                            vals.append(float(p[1].strip()))
                    except Exception:
                        pass
            s = pd.Series(vals, index=pd.DatetimeIndex(dates), name=sid)
            return s.sort_index()
        except Exception:
            return pd.Series(dtype=float, name=sid)

    def _zscore(s: pd.Series) -> float:
        """Z-Score des letzten Wertes vs. gesamter Zeitreihe."""
        if len(s) < 10:
            return 0.0
        mu, sigma = float(s.mean()), float(s.std())
        return 0.0 if sigma == 0 else float((s.iloc[-1] - mu) / sigma)

    def _yf_ratio(t1: str, t2: str, start: str = _start2y) -> pd.Series:
        """Verhältnis zweier yfinance-Ticker (tägliche Schlusskurse)."""
        try:
            d1 = yf.Ticker(t1).history(start=start)["Close"]
            d2 = yf.Ticker(t2).history(start=start)["Close"]
            ratio = (d1 / d2).dropna()
            ratio.name = f"{t1}/{t2}"
            return ratio
        except Exception:
            return pd.Series(dtype=float)

    def _ind(value, unit, z, series, desc, signal_dir=1, is_mock=False):
        return {"value": value, "unit": unit, "z": round(float(z), 2),
                "series": series, "description": desc,
                "signal_dir": signal_dir, "is_mock": is_mock}

    # ── Modul 1: Wachstum / Leading Indicators ────────────────────────
    m1 = {}
    t10y2y_s = _fred_ts("T10Y2Y")
    if not t10y2y_s.empty:
        m1["Zinskurve (10J–2J)"] = _ind(
            round(float(t10y2y_s.iloc[-1]), 2), "%", _zscore(t10y2y_s), t10y2y_s.tail(504),
            "10J minus 2J Treasury-Spread. Negativ = Rezessionswarnung (Inversion).", 1)

    icsa_s = _fred_ts("ICSA")
    if not icsa_s.empty:
        m1["Erstanträge Arb.-losigkeit"] = _ind(
            int(icsa_s.iloc[-1] / 1000), "k", -_zscore(icsa_s), icsa_s.tail(104),
            "US Erstanträge (wöchentl.). Invertiert: niedrig = starker Arbeitsmarkt = bullish.", -1)

    m1["ISM Mfg. PMI (Schätzung)"] = _ind(
        49.0, "", -0.3, pd.Series(dtype=float),
        "ISM Einkaufsmanagerindex (kein kostenfreier Feed — Näherungswert). >50 = Expansion.", 1, True)

    out["modules"]["Wachstum"] = m1

    # ── Modul 2: Finanzierungsbedingungen ────────────────────────────
    m2 = {}
    nfci_s = _fred_ts("NFCI")
    if not nfci_s.empty:
        m2["Chicago Fed FCI"] = _ind(
            round(float(nfci_s.iloc[-1]), 3), "", -_zscore(nfci_s), nfci_s.tail(104),
            "Nat. Financial Conditions Index. Negativ = lockere Bedingungen (bullish für Märkte).", -1)

    dfii10_s = _fred_ts("DFII10")
    if not dfii10_s.empty:
        m2["10J Realzins (TIPS)"] = _ind(
            round(float(dfii10_s.iloc[-1]), 2), "%", -_zscore(dfii10_s), dfii10_s.tail(504),
            "10J TIPS-Rendite (realer Zins nach Inflation). Hoher Realzins belastet Aktienmultiples.", -1)

    out["modules"]["Finanzierung"] = m2

    # ── Modul 3: Kreditmarkt-Risiko ───────────────────────────────────
    m3 = {}
    hy_s = _fred_ts("BAMLH0A0HYM2")
    if not hy_s.empty:
        m3["HY Spread (OAS)"] = _ind(
            int(hy_s.iloc[-1]), "bp", -_zscore(hy_s), hy_s.tail(504),
            "High-Yield Option-Adjusted Spread. >600bp = erhöhtes Kreditrisiko / Marktstress.", -1)

    ig_s = _fred_ts("BAMLC0A0CM")
    if not ig_s.empty:
        m3["IG Spread (OAS)"] = _ind(
            int(ig_s.iloc[-1]), "bp", -_zscore(ig_s), ig_s.tail(504),
            "Investment Grade Spread. Früher Stressindikator — weitet sich vor HY-Spreads aus.", -1)

    out["modules"]["Kredit"] = m3

    # ── Modul 4: Marktbreite ──────────────────────────────────────────
    m4 = {}
    rsp_spy = _yf_ratio("RSP", "SPY")
    if not rsp_spy.empty:
        m4["Marktbreite (EW/KGW)"] = _ind(
            round(float(rsp_spy.iloc[-1]), 4), "x", _zscore(rsp_spy), rsp_spy,
            "S&P Equal Weight / Cap Weight. Steigt = breite Partizipation (bullish). Fällt = Konzentration.", 1)

    try:
        _spy_h = yf.Ticker("SPY").history(start=_start2y)["Close"]
        _spy_ma200 = _spy_h.rolling(200).mean()
        if not _spy_h.empty and not _spy_ma200.empty:
            _above = 1.0 if float(_spy_h.iloc[-1]) > float(_spy_ma200.iloc[-1]) else 0.0
            # Proxy: distance to 200MA as breadth signal
            _dist = (_spy_h / _spy_ma200 - 1) * 100
            m4["S&P 500 über 200-MA"] = _ind(
                round(float(_dist.iloc[-1]), 1), "%", _zscore(_dist), _dist,
                "SPY Abstand zur 200-Tage-Linie. Über 0% = Aufwärtstrend intakt.", 1)
    except Exception:
        pass

    out["modules"]["Marktbreite"] = m4

    # ── Modul 5: Inflationserwartungen ────────────────────────────────
    m5 = {}
    for sid, label, desc in [
        ("T5YIE",  "5J Breakeven Inflation",  "5J Inflationserwartungen. Optimal 2,0–2,5%. Zu hoch = Fed-Druck, zu niedrig = Deflationsangst."),
        ("T10YIE", "10J Breakeven Inflation", "10J Inflationserwartungen. Langfristiger Fed-Anker. >3% = restriktive Geldpolitik erwartet."),
    ]:
        s = _fred_ts(sid)
        if not s.empty:
            v = float(s.iloc[-1])
            # Goldilocks-Zone 2,0–2,5%: Abweichung davon ist negativ
            _ref = 2.25
            _sigma = float(s.std()) or 0.3
            _z = -(abs(v - _ref) / _sigma)
            m5[label] = _ind(round(v, 2), "%", _z, s.tail(504), desc, 0)

    out["modules"]["Inflation"] = m5

    # ── Modul 6: Globale Liquidität ───────────────────────────────────
    m6 = {}
    walcl_s = _fred_ts("WALCL", start=_start5y)
    if not walcl_s.empty and len(walcl_s) >= 52:
        _yoy = walcl_s.pct_change(52) * 100
        _yoy = _yoy.dropna()
        if not _yoy.empty:
            _wz = min(max(float(_yoy.iloc[-1]) / 20, -2), 2)
            m6["Fed Bilanz YoY"] = _ind(
                round(float(walcl_s.iloc[-1]) / 1e6, 2), "Bio $", round(_wz, 2), walcl_s.tail(260),
                "Fed Bilanzsumme. QE-Expansion = bullish, QT-Kontraktion = bearish für Risikoassets.", 1)

    m2sl_s = _fred_ts("M2SL", start=_start5y)
    if not m2sl_s.empty and len(m2sl_s) >= 13:
        _m2yoy = (m2sl_s.pct_change(12) * 100).dropna()
        if not _m2yoy.empty:
            m6["M2 Geldmenge YoY"] = _ind(
                round(float(_m2yoy.iloc[-1]), 1), "%", _zscore(_m2yoy), _m2yoy.tail(60),
                "M2-Wachstum YoY. Positiv = expansive Liquidität. Negativ = restriktives Umfeld.", 1)

    try:
        dxy_h = yf.Ticker("DX-Y.NYB").history(start=_start2y)["Close"]
        if not dxy_h.empty:
            m6["US-Dollar (DXY)"] = _ind(
                round(float(dxy_h.iloc[-1]), 1), "", -_zscore(dxy_h), dxy_h,
                "US-Dollar-Index. Starker Dollar = globaler Liquiditätsdruck (bearish für EM + Rohstoffe).", -1)
    except Exception:
        pass

    out["modules"]["Liquidität"] = m6

    # ── Modul 7: Faktor- & Regime-Analyse ────────────────────────────
    m7 = {}
    for t1, t2, label, desc, sdir in [
        ("IVW", "IVE", "Growth vs. Value",       "MSCI Growth/Value ETF. Steigt Growth = Risk-On / expansive Phase.", 1),
        ("IWM", "SPY", "Small vs. Large Cap",     "Russell 2000 / S&P 500. Small-Cap-Stärke = Risk-On, Liquiditätszufluss breit.", 1),
        ("XLY", "XLP", "Zyklisch vs. Defensiv",  "Konsum zyklisch (XLY) / Basis (XLP). Steigt = Risk-On Regime.", 1),
    ]:
        r = _yf_ratio(t1, t2)
        if not r.empty:
            m7[label] = _ind(round(float(r.iloc[-1]), 4), "x", _zscore(r), r, desc, sdir)

    out["modules"]["Faktoren"] = m7

    # ── Composite Macro Regime Score ──────────────────────────────────
    _weights = {
        "Wachstum":   0.20, "Finanzierung": 0.20, "Kredit":    0.20,
        "Marktbreite":0.10, "Inflation":    0.10, "Liquidität":0.10,
        "Faktoren":   0.10,
    }
    _mod_scores: dict = {}
    _total, _total_w = 0.0, 0.0
    for mod_key, weight in _weights.items():
        mod = out["modules"].get(mod_key, {})
        zs = [v["z"] for v in mod.values()
              if isinstance(v.get("z"), (int, float)) and not np.isnan(v["z"])]
        if zs:
            ms = float(np.clip(np.mean(zs), -3, 3))
            _mod_scores[mod_key] = round(ms, 2)
            _total += ms * weight
            _total_w += weight

    composite = round(_total / _total_w, 2) if _total_w > 0 else 0.0
    if composite > 0.5:    reg_lbl, reg_clr = "Risk-On",  _C_POSITIVE
    elif composite > -0.5: reg_lbl, reg_clr = "Neutral",  _C_NEUTRAL
    else:                   reg_lbl, reg_clr = "Risk-Off", _C_NEGATIVE

    out["regime"] = {
        "score":   composite,
        "label":   reg_lbl,
        "color":   reg_clr,
        "modules": _mod_scores,
    }
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

# ── Mid-Cap Pool — Nischenführer mit Moat, ~1,5–20 Mrd. Mkt-Cap ──────────────
_MIDCAP_POOL = {
    "POOL":        "Pool Corp – quasi-monopolistischer US-Schwimmbad-Distributor, >20 % Nettomargen",
    "KNSL":        "Kinsale Capital – Spezialversicherung mit außergewöhnlich niedrigem Combined Ratio",
    "MEDP":        "Medpace Holdings – CRO mit hohen Margen und stabiler klinischer Auftragspipeline",
    "SAIA":        "Saia Inc – LTL-Freight-Carrier mit starker regionaler Preissetzungsmacht",
    "RBC":         "RBC Bearings – Präzisionslager für Luft-/Raumfahrt, Rüstung & Industrie",
    "NVT":         "nVent Electric – Elektrische Gehäuse mit wachsendem Rechenzentrum-Anteil",
    "TREX":        "Trex Company – Marktführer Verbundterrassen mit 40 %+ Bruttomarge, kaum Konkurrenz",
    "CSWI":        "CSW Industrials – außergewöhnlicher ROIC durch führende Nischenprodukte (HVAC, Leitungen)",
    "FTDR":        "Frontdoor – Hausgarantie-Plattform mit hohem FCF und wiederkehrenden Abonnements",
    "HRI":         "Herc Holdings – Gerätemietpark mit starkem operativen Hebel und Infrastrukturzyklus",
    "GRBK":        "Green Brick Partners – Homebuilder mit strategischen Landreserven und hohem ROE",
    "STEP":        "StepStone Group – Alternative-Asset-Manager mit schnell wachsendem AUM",
    "MGPI":        "MGP Ingredients – Whiskey-Destillerie: Lagerbestände als Burggraben, stabiler FCF",
    "CRVL":        "CorVel Corp – Workers-Comp-Kostenmanagement, nischendominierende Softwareplattform",
    # ── EU Mid-Caps (AEX + XETRA MDAX = beste yFinance-Abdeckung) ────────
    "RATIONAL.DE": "Rational AG – Kombi-Dämpfer-Quasi-Monopol für Profiküchen, 25 %+ Nettomarge (DE)",
    "BESI.AS":     "BE Semiconductor – Halbleiter-Packaging-Equipment, >40 % Nettomarge, AEX (NL)",
    "IMCD.AS":     "IMCD Group – Spezialchemie-Distribution, stabiles Wachstum, Asset-Light (NL)",
    "AALB.AS":     "Aalberts Industries – Flow-Control & Wärmetechnik für Industrie & Bau (NL)",
    "AIXA.DE":     "Aixtron SE – Depositionsanlagen für Leistungshalbleiter & LEDs, MDAX (DE)",
    "PUM.DE":      "Puma SE – Sportartikel mit globalem Vertriebsnetz, attraktive Bewertung (DE)",
    "GTT.PA":      "GTT – LNG-Containment-Quasi-Monopol, >50 % Nettomarge, Euronext Paris (FR)",
}

# ── Small-Cap Pool — profitabel, Nischenführer, positiver FCF Pflicht ─────────
_SMALLCAP_POOL = {
    "OSIS":  "OSI Systems – Sicherheitsinspektions-Systeme für Behörden & Flughäfen weltweit",
    "CASS":  "Cass Information Systems – B2B-Zahlungsverarbeitung mit 40 Jahren Profitabilität",
    "DORM":  "Dorman Products – Automotive-Aftermarket-Nischenteile, profitabel und schuldenarm",
    "HLIO":  "Helios Technologies – Hydraulik & Steuerungstechnik für Mobilmaschinen weltweit",
    "STC":   "Stewart Info Services – Titelversicherung mit stabiler Immobilienmarktposition",
    "UFPT":  "UFP Technologies – Spezialverpackung für Medizintechnik und Luft-/Raumfahrt",
    "MGRC":  "McGrath RentCorp – Modulare Raummietlösungen für Schulen und Unternehmen, FCF-stark",
    "LMAT":  "LeMaitre Vascular – Chirurgische Geräte für Gefäßchirurgie, echtes Nischenmonopol",
    "KFRC":  "Kforce Inc – Tech- & Finance-Personalvermittlung mit positiver FCF-Bilanz",
    "PRDO":  "Perdoceo Education – Online-Bildung mit hohen Margen, null Langfristschulden",
    "TBBK":  "The Bancorp – Fintech-Bank mit führender Prepaid-Karten-Infrastruktur",
    "HRMY":  "Harmony Biosciences – Neurologisches Pharma, profitabel mit wachsender Pipeline",
    "CENTA": "Central Garden & Pet – Haustier-/Gartenbedarf mit führenden Markenportfolios",
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


_DAYTRADING_POOL = [
    "TQQQ","SQQQ","UPRO","SPXU","QQQ","SPY","NVDA","TSLA","AMD","META",
    "AAPL","MSFT","AMZN","GOOGL","NFLX","SMCI","ARM","PLTR","COIN","MSTR",
    "IONQ","RIVN","LCID","SOFI","HOOD","GME","AMC","BYND","SPCE","BBBY",
]


@st.cache_data(ttl=14400, show_spinner=False)
def load_quality_highscore() -> list:
    """Top-Quality-Picks aus kuratierten Growth- und Value-Pools (Score ≥ 70)."""
    _pool = list(dict.fromkeys(list(_GROWTH_POOL.keys()) + list(_VALUE_POOL.keys())))
    results = []
    for tkr in _pool:
        try:
            info  = yf.Ticker(tkr).info
            sc    = _sc_score(info)
            if sc < 70:
                continue
            price  = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            mktcap = info.get("marketCap") or 0
            fcf    = info.get("freeCashflow") or 0
            results.append({
                "ticker":       tkr,
                "name":         info.get("shortName", tkr),
                "price":        round(price, 2),
                "score":        sc,
                "rev_growth":   round((info.get("revenueGrowth") or 0) * 100, 1),
                "gross_margin": round((info.get("grossMargins") or 0) * 100, 1),
                "fcf_yield":    round(fcf / mktcap * 100, 1) if fcf and mktcap else 0.0,
                "roe":          round((info.get("returnOnEquity") or 0) * 100, 1),
            })
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def load_daytrading_picks() -> list:
    """ATR% + relatives Volumen — top volatile tickers für Daytrader."""
    results = []
    for tkr in _DAYTRADING_POOL:
        try:
            st_obj = yf.Ticker(tkr)
            info   = st_obj.info
            hist30 = st_obj.history(period="30d")
            if hist30.empty or len(hist30) < 5:
                continue
            price = float(hist30["Close"].iloc[-1])
            if price <= 0:
                continue
            high  = hist30["High"]
            low   = hist30["Low"]
            close = hist30["Close"]
            prev  = close.shift(1)
            tr    = pd.concat([high - low, (high - prev).abs(), (low - prev).abs()], axis=1).max(axis=1)
            atr_pct = float(tr.tail(14).mean() / price * 100)
            avg_vol   = float(hist30["Volume"].iloc[:-1].mean()) or 1
            today_vol = float(hist30["Volume"].iloc[-1])
            rel_vol   = today_vol / avg_vol
            name = info.get("shortName", tkr)
            typ  = "Leveraged ETF" if any(x in name for x in ["3x","Ultra","ProShares","Direxion"]) \
                   else "ETF" if info.get("quoteType") == "ETF" \
                   else "Aktie"
            results.append({
                "ticker":  tkr,
                "name":    name,
                "price":   round(price, 2),
                "atr_pct": round(atr_pct, 1),
                "rel_vol": round(rel_vol, 2),
                "typ":     typ,
                "score":   round(atr_pct * 0.6 + rel_vol * 0.4, 2),
            })
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:15]


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


@st.cache_data(ttl=43200, show_spinner=False)
def load_small_mid_picks() -> tuple[list[dict], list[dict]]:
    """
    Lädt Mid- und Small-Cap-Kandidaten mit Live-Qualitätsfilter.
    Mid-Cap: FCF>0, Bruttomarge>35%, RevGrowth>8%, D/E<120, Kurs>5
    Small-Cap: EPS>0, FCF>0, Bruttomarge>40%, RevGrowth>10%, D/E<80, Kurs>5
    """
    mid_results, small_results = [], []

    for pool, results, gm_min, rg_min, de_max, need_eps in [
        (_MIDCAP_POOL,   mid_results,   0.35, 0.08, 120, False),
        (_SMALLCAP_POOL, small_results, 0.40, 0.10,  80, True),
    ]:
        for t, desc in pool.items():
            try:
                info = yf.Ticker(t).info
                price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
                if not price or price < 5:
                    continue
                fcf    = info.get("freeCashflow") or 0
                mktcap = info.get("marketCap") or 1
                gm     = info.get("grossMargins") or 0
                rg     = info.get("revenueGrowth") or 0
                de     = info.get("debtToEquity") or 0
                eps    = info.get("trailingEps") or 0
                # Quality gate
                if fcf <= 0:                     continue
                if gm < gm_min:                  continue
                if rg < rg_min:                  continue
                if de > de_max:                  continue
                if need_eps and eps <= 0:        continue

                fcf_yield  = fcf / mktcap * 100
                roe        = (info.get("returnOnEquity") or 0) * 100
                fwd_pe     = info.get("forwardPE")
                om         = (info.get("operatingMargins") or 0) * 100
                week52h    = info.get("fiftyTwoWeekHigh") or price
                week52l    = info.get("fiftyTwoWeekLow") or price
                w52_pos    = ((price - week52l) / (week52h - week52l) * 100) if week52h > week52l else 50
                # Value factor: PEG = fwd_PE / rev_growth_% (< 1.5 = günstig)
                rg_pct = rg * 100
                peg = (fwd_pe / rg_pct) if (fwd_pe and fwd_pe > 0 and rg_pct > 2) else None
                # P/FCF als Fallback-Value-Metrik
                pfcf = mktcap / fcf if fcf > 0 else None
                # Value-Bonus: Belohnt günstiges PEG, bestraft überteuerte Bewertung
                value_adj = 0
                if peg is not None:
                    if peg < 1.0:   value_adj = 15
                    elif peg < 1.5: value_adj = 10
                    elif peg < 2.0: value_adj =  5
                    elif peg > 4.0: value_adj = -10
                    elif peg > 3.0: value_adj =  -5
                elif pfcf is not None:
                    if pfcf < 15:   value_adj = 10
                    elif pfcf < 25: value_adj =  5
                    elif pfcf > 40: value_adj =  -5
                # Combined quality + value score
                q_score = (
                    fcf_yield * 4
                    + gm * 100 * 0.3
                    + rg * 100 * 0.5
                    + max(0, roe) * 0.2
                    + max(0, 100 - de) * 0.05
                    + value_adj
                )
                results.append({
                    "ticker": t, "name": info.get("shortName") or t, "desc": desc,
                    "price": price, "fwd_pe": fwd_pe, "fcf_yield": fcf_yield,
                    "rev_growth": rg_pct, "gross_margin": gm * 100,
                    "op_margin": om, "roe": roe, "w52_pos": w52_pos,
                    "mktcap": mktcap, "q_score": q_score,
                    "peg": peg, "pfcf": pfcf,
                })
            except Exception:
                pass

    mid_results.sort(key=lambda x: x["q_score"], reverse=True)
    small_results.sort(key=lambda x: x["q_score"], reverse=True)
    return mid_results[:8], small_results[:8]


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
            raise _TruncatedError(text)
        return text
    raise ValueError(f"Modell '{model}' in v1beta und v1 nicht gefunden")


class _TruncatedError(Exception):
    """Raised when Gemini returns MAX_TOKENS. Carries the partial text."""
    def __init__(self, partial: str):
        self.partial = partial
        super().__init__("MAX_TOKENS")


def _try_gemini(messages: list, max_tokens: int,
                temperature: float, api_key: str) -> tuple[str, str]:
    """
    Versucht alle verfügbaren Gemini-Modelle (via ListModels + Fallback-Liste).
    Gibt (text, model_name) bei Erfolg oder ("", alle_fehler) zurück.
    Bei Token-Limit: einmaliger Retry mit erhöhtem Limit (bis 8192).
    """
    models = _discover_gemini_models(api_key) or _GEMINI_MODELS
    errors = []
    for model in models:
        try:
            text = _call_gemini(api_key, model, messages, max_tokens, temperature)
            return text, model
        except _TruncatedError as trunc:
            retry_limit = min(8192, int(max_tokens * 1.8))
            if retry_limit > max_tokens:
                try:
                    text = _call_gemini(api_key, model, messages, retry_limit, temperature)
                    return text, model
                except _TruncatedError as trunc2:
                    return trunc2.partial, model
                except Exception:
                    pass
            return trunc.partial, model
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
if "show_stocks" not in st.session_state:
    st.session_state["show_stocks"] = False
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
    _wl_pw_required = bool(os.getenv("PORTFOLIO_PASSWORD", ""))
    st.session_state["watchlist"] = [] if _wl_pw_required else _wl_load_file()
if "wl_unlocked" not in st.session_state:
    st.session_state["wl_unlocked"] = not bool(os.getenv("PORTFOLIO_PASSWORD", ""))
if "show_wl_compare" not in st.session_state:
    st.session_state["show_wl_compare"] = False
if "wachstum_expanded" not in st.session_state:
    st.session_state["wachstum_expanded"] = None
if "seg_expanded" not in st.session_state:
    st.session_state["seg_expanded"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0
if "show_portfolio" not in st.session_state:
    st.session_state["show_portfolio"] = False
if "show_etf_analyzer" not in st.session_state:
    st.session_state["show_etf_analyzer"] = False
if "etf_ticker_input" not in st.session_state:
    st.session_state["etf_ticker_input"] = ""
if "portfolio_df" not in st.session_state:
    st.session_state["portfolio_df"] = None
if "portfolio_isin_map" not in st.session_state:
    st.session_state["portfolio_isin_map"] = {}
if "portfolio_csv_bytes" not in st.session_state:
    st.session_state["portfolio_csv_bytes"] = None
if "portfolio_sb_checked" not in st.session_state:
    st.session_state["portfolio_sb_checked"] = False
if "portfolio_sb_date" not in st.session_state:
    st.session_state["portfolio_sb_date"] = None
if "light_mode" not in st.session_state:
    st.session_state["light_mode"] = False
if "portfolio_settings_loaded" not in st.session_state:
    _pf_settings = _load_portfolio_settings()
    st.session_state["portfolio_excluded_isins"] = _pf_settings.get("excluded_isins", [])
    st.session_state["portfolio_manual_prices"]  = _pf_settings.get("manual_prices", {})
    st.session_state["portfolio_manual_shares"]  = _pf_settings.get("manual_shares", {})
    st.session_state["portfolio_settings_loaded"] = True

def _go_to_ticker(t):
    st.session_state["ticker"] = t
    st.session_state["show_landing"] = False
    st.session_state["show_portfolio"] = False
    st.session_state["show_etf_analyzer"] = False
    st.session_state["show_stocks"] = False
    st.session_state["search_input"] = t
    st.session_state["search_msg"] = ""
    st.session_state["active_tab"] = 0
    st.session_state["suggestions"] = []
    st.session_state["_open_sidebar"] = True

# ==================== ETF LOOK-THROUGH DATA (module level — used by Portfolio + ETF Analyzer) ==
_ETF_CW = {
    # MSCI All-World / Developed World
    'VWCE.DE': {'USA':62.5,'Japan':5.7,'UK':3.8,'Frankreich':3.1,'Kanada':2.9,
                'Schweiz':2.6,'Deutschland':2.5,'Australien':2.1,'Indien':1.8,
                'Taiwan':1.8,'Südkorea':1.6,'Niederlande':1.2,'Sonstige':7.4},
    'FWRA.DE': {'USA':62.5,'Japan':5.7,'UK':3.8,'Frankreich':3.1,'Kanada':2.9,
                'Schweiz':2.6,'Deutschland':2.5,'Australien':2.1,'Indien':1.8,
                'Taiwan':1.8,'Südkorea':1.6,'Niederlande':1.2,'Sonstige':7.4},
    'VWRL.L':  {'USA':62.5,'Japan':5.7,'UK':3.8,'Frankreich':3.1,'Kanada':2.9,
                'Schweiz':2.6,'Deutschland':2.5,'Australien':2.1,'Indien':1.8,
                'Taiwan':1.8,'Südkorea':1.6,'Niederlande':1.2,'Sonstige':7.4},
    'SXR8.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
    'XDWD.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
    'EUNL.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
    'XMWO.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
    # S&P 500 / USA
    'SXR2.DE': {'USA':100.0}, 'IUSE.DE': {'USA':100.0}, 'LCUW.DE': {'USA':100.0},
    'VUSA.L':  {'USA':100.0}, 'SPY5.DE': {'USA':100.0}, 'CSPX.L':  {'USA':100.0},
    # NASDAQ-100
    'EQQQ.DE': {'USA':97.0,'Sonstige':3.0}, 'CNDX.L': {'USA':97.0,'Sonstige':3.0},
    # EuroStoxx 50
    'EXW1.DE': {'Deutschland':17.2,'Frankreich':16.8,'Niederlande':14.2,'Spanien':9.5,
                'Italien':8.5,'Belgien':4.8,'Finnland':4.2,'Irland':3.5,'Sonstige':21.3},
    'MEUD.DE': {'Deutschland':17.2,'Frankreich':16.8,'Niederlande':14.2,'Spanien':9.5,
                'Italien':8.5,'Belgien':4.8,'Finnland':4.2,'Irland':3.5,'Sonstige':21.3},
    'LYPS.DE': {'Deutschland':17.2,'Frankreich':16.8,'Niederlande':14.2,'Spanien':9.5,
                'Italien':8.5,'Belgien':4.8,'Finnland':4.2,'Irland':3.5,'Sonstige':21.3},
    # MSCI Europe
    'IQQY.DE': {'UK':23.8,'Frankreich':17.0,'Schweiz':13.5,'Deutschland':12.8,
                'Niederlande':8.2,'Schweden':5.3,'Dänemark':4.1,'Spanien':3.5,
                'Italien':3.0,'Sonstige':8.8},
    'IEUA.DE': {'UK':23.8,'Frankreich':17.0,'Schweiz':13.5,'Deutschland':12.8,
                'Niederlande':8.2,'Schweden':5.3,'Dänemark':4.1,'Spanien':3.5,
                'Italien':3.0,'Sonstige':8.8},
    # DAX / Deutschland
    'EXS1.DE': {'Deutschland':100.0}, 'DBXD.DE': {'Deutschland':100.0},
    # Japan / Asien
    'EXV5.DE': {'Japan':100.0}, 'XDJP.DE': {'Japan':100.0},
    'IQQC.DE': {'China':100.0},
    # MSCI EM
    'IS3N.DE': {'China':26.8,'Indien':14.2,'Taiwan':17.1,'Südkorea':12.3,
                'Brasilien':5.1,'Saudi-Arabien':4.0,'Südafrika':3.5,
                'Mexiko':2.5,'Indonesien':1.6,'Sonstige':12.9},
    'IS3R.DE': {'China':26.8,'Indien':14.2,'Taiwan':17.1,'Südkorea':12.3,
                'Brasilien':5.1,'Saudi-Arabien':4.0,'Südafrika':3.5,
                'Mexiko':2.5,'Indonesien':1.6,'Sonstige':12.9},
    'XMME.DE': {'China':26.8,'Indien':14.2,'Taiwan':17.1,'Südkorea':12.3,
                'Brasilien':5.1,'Saudi-Arabien':4.0,'Südafrika':3.5,
                'Mexiko':2.5,'Indonesien':1.6,'Sonstige':12.9},
    # Dividend
    'VHYL.L':  {'USA':60.2,'UK':7.1,'Japan':6.0,'Schweiz':4.2,'Frankreich':3.5,
                'Deutschland':3.0,'Australien':2.8,'Sonstige':13.2},
    'ISPA.DE': {'USA':54.0,'Kanada':8.0,'UK':6.0,'Japan':5.5,'Schweiz':4.0,
                'Frankreich':3.5,'Deutschland':3.0,'Australien':2.5,'Sonstige':13.5},
}

# Sektor-Gewichtungen (Quelle: Fondsanbieter, ca. 2024/25; Sektornamen auf Deutsch)
_ETF_SW: dict = {
    # ── MSCI World (entwickelte Märkte) ──────────────────────────────────────
    **dict.fromkeys(['EUNL.DE','XDWD.DE','XMWO.DE','IWDA.AS','PRAW.DE','PRWA.DE',
                     'LCUP.DE','PRIW.DE','LCUQ.DE','LCU.DE','LCUA.DE','PRWG.DE'],
        {'IT & Technologie':23.5,'Finanzwesen':15.0,'Gesundheitswesen':12.0,
         'Industrie':11.0,'Nicht-Basiskonsumgüter':10.5,'Telekommunikation':8.8,
         'Basiskonsumgüter':6.8,'Energie':4.0,'Grundstoffe':3.8,
         'Immobilien':2.4,'Versorger':2.2}),
    # ── S&P 500 ───────────────────────────────────────────────────────────────
    **dict.fromkeys(['SXR8.DE','LCUW.DE','SPY5.DE','IUSE.DE','SXR2.DE',
                     'VUSA.L','CSPX.L','C500.DE','SP5C.DE'],
        {'IT & Technologie':31.8,'Finanzwesen':13.2,'Gesundheitswesen':11.8,
         'Industrie':8.5,'Nicht-Basiskonsumgüter':10.3,'Telekommunikation':8.8,
         'Basiskonsumgüter':5.8,'Energie':3.8,'Grundstoffe':2.3,
         'Immobilien':2.2,'Versorger':1.5}),
    # ── FTSE All-World / MSCI ACWI ────────────────────────────────────────────
    **dict.fromkeys(['VWCE.DE','FWRA.DE','VWRL.L'],
        {'IT & Technologie':21.5,'Finanzwesen':16.0,'Gesundheitswesen':11.5,
         'Industrie':10.5,'Nicht-Basiskonsumgüter':11.0,'Telekommunikation':8.5,
         'Basiskonsumgüter':7.0,'Energie':4.5,'Grundstoffe':4.0,
         'Immobilien':3.0,'Versorger':2.5}),
    # ── NASDAQ-100 ────────────────────────────────────────────────────────────
    **dict.fromkeys(['EQQQ.DE','CNDX.L'],
        {'IT & Technologie':51.8,'Telekommunikation':17.4,
         'Nicht-Basiskonsumgüter':14.0,'Gesundheitswesen':7.2,
         'Industrie':4.5,'Finanzwesen':2.4,'Basiskonsumgüter':1.7,'Sonstige':1.0}),
    # ── EuroStoxx 50 ─────────────────────────────────────────────────────────
    **dict.fromkeys(['EXW1.DE','MEUD.DE','LYPS.DE'],
        {'Finanzwesen':20.5,'Industrie':16.0,'Nicht-Basiskonsumgüter':14.5,
         'IT & Technologie':9.5,'Gesundheitswesen':8.0,'Versorger':8.5,
         'Telekommunikation':7.0,'Energie':6.5,'Grundstoffe':5.5,'Basiskonsumgüter':4.0}),
    # ── MSCI Europe ───────────────────────────────────────────────────────────
    **dict.fromkeys(['IQQY.DE','IEUA.DE','SPYY.DE','IQQE.DE','XESC.DE',
                     'IEMC.DE','ZPRX.DE','XEUR.DE','VGK'],
        {'Finanzwesen':17.5,'Industrie':16.0,'Gesundheitswesen':14.5,
         'Nicht-Basiskonsumgüter':11.5,'Basiskonsumgüter':10.0,'IT & Technologie':8.5,
         'Energie':7.0,'Telekommunikation':5.5,'Grundstoffe':5.0,
         'Versorger':3.0,'Immobilien':1.5}),
    # ── MSCI EM ───────────────────────────────────────────────────────────────
    **dict.fromkeys(['IS3N.DE','IS3R.DE','IMEA.DE','XMME.DE','IQQD.DE',
                     'IQQC.DE','XMIN.DE','IEMA.DE'],
        {'IT & Technologie':22.0,'Finanzwesen':19.5,'Nicht-Basiskonsumgüter':12.5,
         'Telekommunikation':10.0,'Basiskonsumgüter':6.5,'Industrie':6.5,
         'Energie':5.0,'Grundstoffe':5.2,'Gesundheitswesen':4.5,
         'Immobilien':3.0,'Versorger':1.8}),
    # ── Japan ─────────────────────────────────────────────────────────────────
    **dict.fromkeys(['EXV5.DE','XDJP.DE','IQQJ.DE'],
        {'IT & Technologie':22.0,'Industrie':21.0,'Nicht-Basiskonsumgüter':15.5,
         'Gesundheitswesen':9.5,'Finanzwesen':8.5,'Basiskonsumgüter':8.0,
         'Grundstoffe':5.5,'Energie':3.5,'Telekommunikation':3.5,
         'Versorger':2.0,'Immobilien':1.0}),
    # ── DAX ───────────────────────────────────────────────────────────────────
    **dict.fromkeys(['EXS1.DE','DBXD.DE','DAXE.DE'],
        {'IT & Technologie':18.0,'Nicht-Basiskonsumgüter':15.0,'Industrie':14.5,
         'Gesundheitswesen':12.5,'Finanzwesen':12.0,'Basiskonsumgüter':9.0,
         'Energie':7.0,'Grundstoffe':5.0,'Telekommunikation':4.5,'Versorger':2.5}),
    # ── Dividenden-ETFs ───────────────────────────────────────────────────────
    **dict.fromkeys(['ISPA.DE','QDIV.DE','XDIV.DE','IDVY.L','VHYL.L'],
        {'Finanzwesen':18.0,'IT & Technologie':14.5,'Gesundheitswesen':13.5,
         'Industrie':13.0,'Basiskonsumgüter':12.0,'Energie':10.0,
         'Nicht-Basiskonsumgüter':8.0,'Grundstoffe':6.0,'Versorger':3.0,
         'Telekommunikation':2.0}),
    # ── Sektor-ETFs (100% in einem Sektor) ───────────────────────────────────
    **dict.fromkeys(['XDWT.DE','QDVE.DE','IUIT.DE'],{'IT & Technologie':100.0}),
    **dict.fromkeys(['XDWH.DE','QDVG.DE','HEAL.DE'],{'Gesundheitswesen':100.0}),
    **dict.fromkeys(['XDWF.DE','QDVD.DE'],          {'Finanzwesen':100.0}),
    'XDWU.DE': {'Versorger':100.0},
    'SXRV.DE': {'Telekommunikation':100.0},
    # ── Small/Mid Cap (ähnlich MSCI World, mehr Industrie/Finanzwesen) ────────
    **dict.fromkeys(['IUSN.DE','ZPRV.DE'],
        {'Industrie':18.5,'Finanzwesen':17.0,'IT & Technologie':15.0,
         'Nicht-Basiskonsumgüter':11.0,'Gesundheitswesen':9.5,'Grundstoffe':8.0,
         'Basiskonsumgüter':7.5,'Energie':6.0,'Telekommunikation':4.0,
         'Versorger':2.5,'Immobilien':1.0}),
    'EXI5.DE': {'IT & Technologie':14.0,'Industrie':17.0,'Finanzwesen':16.0,
                'Gesundheitswesen':9.5,'Nicht-Basiskonsumgüter':12.5,
                'Basiskonsumgüter':8.0,'Energie':6.5,'Grundstoffe':7.0,
                'Telekommunikation':4.0,'Versorger':3.0,'Immobilien':2.5},
    # ── Korea / Taiwan / India ────────────────────────────────────────────────
    'XMKR.DE': {'IT & Technologie':40.0,'Finanzwesen':18.0,'Nicht-Basiskonsumgüter':14.0,
                'Industrie':8.0,'Basiskonsumgüter':5.0,'Telekommunikation':5.5,
                'Grundstoffe':5.5,'Energie':2.0,'Gesundheitswesen':2.0},
    'IS3W.DE': {'IT & Technologie':60.0,'Nicht-Basiskonsumgüter':14.5,
                'Finanzwesen':10.0,'Industrie':6.5,'Telekommunikation':4.0,
                'Grundstoffe':3.0,'Sonstige':2.0},
    'XMIN.DE': {'Finanzwesen':22.5,'IT & Technologie':18.0,'Nicht-Basiskonsumgüter':15.5,
                'Energie':12.0,'Grundstoffe':8.5,'Gesundheitswesen':7.0,
                'Industrie':6.5,'Telekommunikation':5.0,'Basiskonsumgüter':4.0},
    # ── Clean Energy ──────────────────────────────────────────────────────────
    'IQQH.DE': {'Energie':35.0,'Versorger':32.0,'Industrie':18.0,
                'IT & Technologie':10.0,'Grundstoffe':5.0},
}

_CONTINENT_MAP = {
    'USA':'Nordamerika','Kanada':'Nordamerika','Mexiko':'Nordamerika',
    'UK':'Europa','Deutschland':'Europa','Frankreich':'Europa','Schweiz':'Europa',
    'Niederlande':'Europa','Schweden':'Europa','Dänemark':'Europa','Spanien':'Europa',
    'Italien':'Europa','Belgien':'Europa','Norwegen':'Europa','Finnland':'Europa',
    'Irland':'Europa','Österreich':'Europa','Polen':'Europa','Portugal':'Europa',
    'Japan':'Asien/Pazifik','China':'Asien/Pazifik','Südkorea':'Asien/Pazifik',
    'Taiwan':'Asien/Pazifik','Australien':'Asien/Pazifik','Indien':'Asien/Pazifik',
    'Hongkong':'Asien/Pazifik','Singapur':'Asien/Pazifik','Indonesien':'Asien/Pazifik',
    'Malaysia':'Asien/Pazifik','Thailand':'Asien/Pazifik','Philippinen':'Asien/Pazifik',
    'Brasilien':'Lateinamerika','Chile':'Lateinamerika','Kolumbien':'Lateinamerika',
    'Peru':'Lateinamerika','Argentinien':'Lateinamerika',
    'Saudi-Arabien':'Mittlerer Osten','Israel':'Mittlerer Osten','VAE':'Mittlerer Osten',
    'Katar':'Mittlerer Osten','Kuwait':'Mittlerer Osten',
    'Südafrika':'Afrika','Ägypten':'Afrika','Nigeria':'Afrika',
    'Sonstige':'Sonstige',
}

# ==================== PORTFOLIO HELPERS ====================

def _parse_portfolio_csv(file_bytes: bytes) -> pd.DataFrame:
    """Parse Finanzen.net Zero Orderhistorie CSV → aktuelle Nettopositionen."""
    df = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), sep=';', decimal=',',
                             encoding=enc, dtype=str)
            break
        except Exception:
            continue
    if df is None or df.empty:
        return pd.DataFrame()
    df.columns = df.columns.str.strip()
    needed = {'Status', 'Richtung', 'ISIN', 'Name', 'WKN', 'Anzahl ausgeführt', 'Ausführung Kurs', 'Wert'}
    if not needed.issubset(df.columns):
        return pd.DataFrame()
    df = df[df['Status'] == 'ausgeführt'].copy()
    if df.empty:
        return pd.DataFrame()
    for col in ['Anzahl ausgeführt', 'Ausführung Kurs', 'Wert']:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce'
        ).fillna(0.0)
    _buy_types  = ['Kauf', 'Sparplan', 'Depot-Einbuchung']
    _sell_types = ['Verkauf', 'Rückgabe', 'Rücknahme', 'Entnahme', 'Depot-Ausbuchung']
    buys  = df[df['Richtung'].isin(_buy_types)].copy()
    sells = df[df['Richtung'].isin(_sell_types)].copy()
    if buys.empty:
        return pd.DataFrame()
    buys['_wert_abs'] = buys['Wert'].abs()
    buy_agg = (buys.groupby('ISIN')
               .agg(name=('Name', 'first'), wkn=('WKN', 'first'),
                    total_bought=('Anzahl ausgeführt', 'sum'),
                    total_invested_eur=('_wert_abs', 'sum'),
                    avg_exec_price=('Ausführung Kurs', 'mean'))
               .reset_index())
    buy_agg['avg_cost'] = (buy_agg['total_invested_eur'] / buy_agg['total_bought'].replace(0, float('nan')))
    if not sells.empty:
        sell_agg = sells.groupby('ISIN').agg(total_sold=('Anzahl ausgeführt', 'sum')).reset_index()
        port = buy_agg.merge(sell_agg, on='ISIN', how='left')
    else:
        port = buy_agg.copy()
        port['total_sold'] = 0.0
    port['total_sold'] = port['total_sold'].fillna(0.0)
    port['shares'] = (port['total_bought'] - port['total_sold']).round(4)
    # Position ist offen wenn: genug Anteile ODER genug Restwert (OR statt AND — z.B. 0.0001 × €50k = €5 zählt)
    port['_residual_val'] = port['shares'] * port['avg_cost'].fillna(0)
    port = port[(port['shares'] >= 0.001) | (port['_residual_val'] >= 1.0)].copy()
    port = port[port['shares'] > 0].copy()  # Negative Bestände (Datenfehler) entfernen
    port = port.drop(columns=['_residual_val'])
    port['cost_basis'] = port['avg_cost'] * port['shares']
    port['is_crypto'] = port['ISIN'].str.startswith('XC')
    warrant_wkn_prefix = ('GJ', 'UJ', 'MJ', 'MA', 'GX', 'HC', 'XS', 'GA', 'SB', 'TB')
    port['is_warrant'] = (
        ~port['is_crypto'] &
        port['wkn'].str[:2].isin(warrant_wkn_prefix)
    )
    return port.sort_values('total_invested_eur', ascending=False).reset_index(drop=True)


@st.cache_data(ttl=86400, show_spinner=False)
def _openfigi_batch(isins: tuple, wkn_by_isin: dict = None) -> dict:
    """Batch-Lookup ISIN → yfinance-Ticker via OpenFIGI. Fallback: WKN-Lookup für nicht gemappte ISINs."""
    # Xetra=GY, Frankfurt=GF, Munich=GM, Hamburg=GH, Stuttgart=GS, Berlin=GB
    _suffix = {'GY': '.DE', 'GF': '.F', 'GM': '.MU', 'GH': '.HM', 'GS': '.SG', 'GB': '.BE',
               'NA': '.AS', 'FP': '.PA', 'LN': '.L',
               'SW': '.SW', 'SS': '.ST', 'DC': '.CO', 'JT': '.T', 'HK': '.HK'}
    _prefer = {
        'US': ['UW', 'UN', 'US', 'UA', 'UT'], 'KY': ['UW', 'UN', 'US'],
        'CA': ['CN', 'CT'], 'DE': ['GY'], 'NL': ['NA'], 'FR': ['FP'],
        'CH': ['SW'], 'SE': ['SS'], 'DK': ['DC'], 'JP': ['JT'],
        'IE': ['LN', 'GY'], 'CN': ['HK'],
        # GBp-Pence-Bug: deutsches EUR-Listing vermeidet /100-Konvertierungsfehler
        'GB': ['GY', 'GF', 'LN'],
        # Nicht-EUR-Märkte → bevorzuge deutsches Listing (direkt in EUR, kein FX-Fehler)
        'KR': ['GY', 'GF'],  # Südkorea
        'TW': ['GY', 'GF'],  # Taiwan
        'IN': ['GY', 'GF'],  # Indien
        'BR': ['GY', 'GF'],  # Brasilien
        'AU': ['GY', 'GF'],  # Australien
        'SG': ['GY', 'GF'],  # Singapur
        'IL': ['GY', 'GF'],  # Israel
        'ZA': ['GY', 'GF'],  # Südafrika
    }

    def _pick_ticker(items, country_prefix):
        pref = _prefer.get(country_prefix, [])
        for exch in pref:
            for fi in items:
                if fi.get('exchCode') == exch and fi.get('ticker'):
                    return fi['ticker'] + _suffix.get(exch, '')
        fi = items[0]
        t, e = fi.get('ticker', ''), fi.get('exchCode', '')
        return (t + _suffix.get(e, '')) if t else None

    result: dict = {}
    valids = [i for i in isins if not i.startswith('XC') and i != '------' and len(i) == 12]
    for start in range(0, len(valids), 10):
        batch = valids[start:start + 10]
        try:
            r = requests.post('https://api.openfigi.com/v3/mapping',
                              json=[{'idType': 'ID_ISIN', 'idValue': i} for i in batch],
                              headers={'Content-Type': 'application/json'}, timeout=12)
            if r.status_code != 200:
                continue
            for idx, item in enumerate(r.json()):
                isin = batch[idx]
                items = item.get('data') or []
                if not items:
                    continue
                tkr = _pick_ticker(items, isin[:2])
                if tkr:
                    result[isin] = tkr
        except Exception:
            pass
        time.sleep(0.3)

    # WKN-Fallback für ISINs die OpenFIGI nicht per ISIN gefunden hat
    if wkn_by_isin:
        failed = [i for i in valids if i not in result]
        for isin in failed:
            wkn = wkn_by_isin.get(isin, '')
            if not wkn or len(wkn) < 4:
                continue
            try:
                r = requests.post('https://api.openfigi.com/v3/mapping',
                                  json=[{'idType': 'ID_WERTPAPIER', 'idValue': wkn}],
                                  headers={'Content-Type': 'application/json'}, timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    items = (data[0].get('data') or []) if data else []
                    if items:
                        tkr = _pick_ticker(items, isin[:2])
                        if tkr:
                            result[isin] = tkr
            except Exception:
                pass
            time.sleep(0.2)

    # GDR → geeigneter Ticker (erreichbar von Railway; KRX ist geblockt)
    # Samsung GDR auf LSE (SMSN.L) handelt bei ~218.000 GBp ≈ €2.580 — korrekte Preisreferenz
    # SSNGY/SSNLF sind US-OTC-ADRs mit völlig anderem Preisniveau (~$14) → falsch für Portfolio-Bewertung
    _GDR_HARDCODED = {
        'US78392B1070': '000660.KS',  # SK Hynix → KOSPI (KRW→EUR via yFinance)
        'US7960502018': 'SMSN.L',  # Samsung GDR Pref → LSE GDR (~€2.580 = 218.000 GBp)
        'US7960508882': 'SMSN.L',  # Samsung GDR Stamm → LSE GDR (~€2.580)
        'CNE100006M58': '0300.HK', # Midea Group H-Aktien → HKEx (~€9,96)
    }
    for isin in valids:
        if isin in _GDR_HARDCODED:
            result[isin] = _GDR_HARDCODED[isin]  # Immer überschreiben: KRX/OpenFIGI-Fehler vermeiden

    # ISIN-Pattern-Fallback: direkte Ableitung wenn OpenFIGI blockiert ist (Railway 403)
    # Koreanische ISINs: KR + Typ(1) + KRX-Code(6) + Check(3)  →  XXXXXX.KS
    # Japanische ISINs:  JP + Präfix(1) + TSE-Code(4) + Check(5) →  XXXX.T
    for isin in valids:
        if isin in result:
            continue
        cc = isin[:2]
        if cc == 'KR':
            result[isin] = f"{isin[3:9]}.KS"
        elif cc == 'JP':
            result[isin] = f"{isin[3:7]}.T"

    return result


@st.cache_data(ttl=3600, show_spinner=False)
def _get_eur_fx_rate(from_currency: str) -> float:
    """Wechselkurs: 1 from_currency = X EUR (gecacht 1h). Mehrere Fallbacks."""
    if from_currency in ('EUR', ''):
        return 1.0

    # Plausible Bandbreiten: 1 Einheit dieser Währung in EUR
    _sane = {
        'JPY': (0.003,  0.012),   # ~0.0063
        'USD': (0.70,   1.30),
        'GBP': (1.00,   1.60),
        'CHF': (0.85,   1.50),
        'KRW': (0.0004, 0.0012),
        'CNY': (0.10,   0.20),
        'HKD': (0.08,   0.17),
        'CAD': (0.55,   0.85),
        'AUD': (0.45,   0.80),
        'SEK': (0.06,   0.12),
        'NOK': (0.06,   0.12),
        'DKK': (0.12,   0.16),
        'SGD': (0.55,   0.85),
        'TWD': (0.020,  0.045),
        'INR': (0.007,  0.016),
        'BRL': (0.12,   0.25),
        'TRY': (0.018,  0.050),
        'MXN': (0.032,  0.065),
        'ZAR': (0.035,  0.075),
        'ILS': (0.18,   0.35),
    }

    def _validate(rate, ccy):
        """Gibt korrekten Rate zurück oder None; erkennt invertierte Rückgabe automatisch."""
        if not rate or rate <= 0:
            return None
        lo, hi = _sane.get(ccy, (1e-9, 1e6))
        if lo <= rate <= hi:
            return float(rate)
        inv = 1.0 / rate
        if lo <= inv <= hi:
            return float(inv)
        return None

    # Versuch 1: direkte yFinance FX-Rate XXXEUR=X
    try:
        fi = yf.Ticker(f"{from_currency}EUR=X").fast_info
        rate = getattr(fi, 'last_price', None)
        validated = _validate(rate, from_currency)
        if validated:
            return validated
    except Exception:
        pass
    # Versuch 2: Inverse via EURXXX=X (z.B. EURKRW=X → 1/rate)
    try:
        fi2 = yf.Ticker(f"EUR{from_currency}=X").fast_info
        rate2 = getattr(fi2, 'last_price', None)
        if rate2 and float(rate2) > 0:
            validated2 = _validate(1.0 / float(rate2), from_currency)
            if validated2:
                return validated2
    except Exception:
        pass
    # Versuch 3: FMP FX-Rate
    if FMP_API_KEY:
        try:
            _fr = requests.get(
                f"https://financialmodelingprep.com/api/v3/fx/{from_currency}EUR",
                params={'apikey': FMP_API_KEY}, timeout=5)
            if _fr.ok and _fr.json():
                _rate = _fr.json()[0].get('bid') or _fr.json()[0].get('ask')
                validated3 = _validate(_rate, from_currency)
                if validated3:
                    return validated3
        except Exception:
            pass
    # Fallback: Näherungswerte (werden täglich selten gebraucht, nur bei API-Ausfall)
    _approx = {
        'KRW': 0.000667, 'CNY': 0.130, 'JPY': 0.0063, 'GBP': 1.17,
        'USD': 0.92,  'HKD': 0.118, 'CAD': 0.68,  'AUD': 0.59,
        'CHF': 1.05,  'SEK': 0.087, 'NOK': 0.086, 'DKK': 0.134,
        'TWD': 0.030, 'SGD': 0.69,  'INR': 0.011, 'BRL': 0.18,
        'MXN': 0.048, 'ZAR': 0.050, 'TRY': 0.028, 'ILS': 0.25,
    }
    return _approx.get(from_currency, 1.0)


@st.cache_data(ttl=300, show_spinner=False)
def _portfolio_quote_ext(ticker: str) -> dict:
    """Kursdaten in EUR: Preis, 52W-Range, Tagesveränderung, FX-Rate. Probiert alternative Suffixe als Fallback."""
    _empty = {'price_eur': None, 'year_high_eur': None, 'year_low_eur': None,
              'day_chg_pct': None, 'fx': 1.0}

    import concurrent.futures as _cf_pq
    def _fetch(t):
        def _do():
            try:
                fi = yf.Ticker(t).fast_info
                price = float(getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_price', None) or 0)
                if not price:
                    return None
                currency = str(getattr(fi, 'currency', 'EUR') or 'EUR').strip()
                if currency == 'GBp' or (currency == 'GBP' and t.endswith('.L') and price > 500):
                    price /= 100.0
                    currency = 'GBP'
                # Harte Korrektur: .T-Ticker sind immer JPY, egal was yFinance meldet
                if t.endswith('.T') and currency != 'JPY':
                    currency = 'JPY'
                fx = _get_eur_fx_rate(currency) if currency != 'EUR' else 1.0
                # Plausibilitäts-Check: Einzelkurs > €50.000 ist fast immer ein FX-Bug
                if fx != 1.0 and price * fx > 50_000:
                    fx_fallback = _get_eur_fx_rate.__wrapped__(currency) if hasattr(_get_eur_fx_rate, '__wrapped__') else None
                    # Nochmals mit 1/fx versuchen
                    if price / fx < 50_000:
                        fx = 1.0 / fx
                y_high  = getattr(fi, 'year_high', None)
                y_low   = getattr(fi, 'year_low', None)
                day_chg = getattr(fi, 'regular_market_change_percent', None)
                return {
                    'price_eur':     price * fx,
                    'year_high_eur': float(y_high) * fx if y_high else None,
                    'year_low_eur':  float(y_low)  * fx if y_low  else None,
                    'day_chg_pct':   float(day_chg) if day_chg is not None else None,
                    'fx':            fx,
                }
            except Exception:
                return None
        try:
            with _cf_pq.ThreadPoolExecutor(max_workers=1) as _ex:
                return _ex.submit(_do).result(timeout=5.0)
        except Exception:
            return None

    result = _fetch(ticker)
    if result:
        return result

    # Alternative Börsen-Suffixe ausprobieren
    _alts = []
    if ticker.endswith('.DE'):
        base = ticker[:-3]
        _alts = [base + '.F', base + '.MU', base + '.HM', base]
    elif ticker.endswith('.F'):
        base = ticker[:-2]
        _alts = [base + '.DE', base + '.MU', base]
    elif ticker.endswith('.L'):
        _alts = [ticker[:-2]]
    elif ticker.endswith('.KS'):
        _alts = []
    elif ticker.endswith('.HK'):
        # HK-Ticker: yFinance braucht 4-stellige Nummern mit Leading Zero (300.HK → 0300.HK)
        _hk_base = ticker[:-3]
        if _hk_base.isdigit() and len(_hk_base) < 4:
            _alts = [_hk_base.zfill(4) + '.HK']
        else:
            _alts = []
    elif '.' not in ticker:
        _alts = [ticker + '.DE', ticker + '.F', ticker + '.L', ticker + '.AS', ticker + '.PA']
    for alt in _alts:
        result = _fetch(alt)
        if result:
            return result

    def _fmp_quote(sym):
        """FMP Quote als direkter Kurs-Abruf — unterstützt KRX, CNY, JPY etc."""
        if not FMP_API_KEY:
            return None
        try:
            _fr = requests.get(
                f"https://financialmodelingprep.com/api/v3/quote/{sym}",
                params={'apikey': FMP_API_KEY}, timeout=5)
            if not (_fr.ok and _fr.json()):
                return None
            _fd = _fr.json()[0]
            _price = float(_fd.get('price') or 0)
            if not _price:
                return None
            _currency = str(_fd.get('currency') or 'EUR').strip()
            if _currency == 'GBp':
                _price /= 100.0
                _currency = 'GBP'
            _fx = _get_eur_fx_rate(_currency) if _currency != 'EUR' else 1.0
            # Sanity-Check: KRW-Kurs × 0.000667 ≈ EUR → Ergebnis darf nicht > 10× den Marktpreis sein
            _price_eur = _price * _fx
            if _price_eur <= 0 or _price_eur > 1_000_000:
                return None
            _chg = _fd.get('changesPercentage')
            return {
                'price_eur':     _price_eur,
                'year_high_eur': float(_fd['yearHigh']) * _fx if _fd.get('yearHigh') else None,
                'year_low_eur':  float(_fd['yearLow'])  * _fx if _fd.get('yearLow')  else None,
                'day_chg_pct':   float(_chg) if _chg is not None else None,
                'fx':            _fx,
            }
        except Exception:
            return None

    # FMP-Fallback wenn yFinance (inkl. Alternativen) keinen Kurs liefert
    if FMP_API_KEY:
        _base = ticker.split('.')[0]
        # Für KRX-Ticker auch mit Punkt-Suffix probieren
        _fmp_candidates = [ticker, _base]
        if ticker.endswith('.KS') or (len(_base) == 6 and _base.isdigit()):
            _fmp_candidates = [_base + '.KS', _base, ticker]
        elif ticker.endswith('.T') or (len(_base) == 4 and _base.isdigit()):
            _fmp_candidates = [_base + '.T', _base, ticker]
        elif ticker.endswith('.HK') and _base.isdigit() and len(_base) < 4:
            # HK-Ticker zero-padden: 300.HK → 0300.HK
            _fmp_candidates = [_base.zfill(4) + '.HK', ticker, _base]
        elif '.' not in ticker and ticker.isalpha():
            # GDR/OTC/LSE-Ticker (000660.KS (SK Hynix KOSPI), SMSN.L) — auch .L probieren
            _fmp_candidates = [ticker, ticker + '.L', _base]
        for _fmp_sym in _fmp_candidates:
            _r = _fmp_quote(_fmp_sym)
            if _r:
                return _r

        # China A-Shares zusätzlich probieren
        if ticker.endswith('.SS') or ticker.endswith('.SZ'):
            _r = _fmp_quote(ticker) or _fmp_quote(_base)
            if _r:
                return _r

    return _empty


# US-Datenticker für ETF-Holdings-Lookup (XETRA/LSE ETFs haben kaum funds_data in yFinance)
_PF_ETF_DATA_TKR: dict = {
    'SXR8.DE':'IVV',   'EUNL.DE':'URTH',  'XDWD.DE':'URTH',  'XMWO.DE':'URTH',
    'VWCE.DE':'VT',    'FWRA.DE':'VT',    'VWRL.L':'VT',     'IWDA.AS':'URTH',
    'EQQQ.DE':'QQQ',   'CNDX.L':'QQQ',    'IS3N.DE':'IEMG',  'IS3R.DE':'IEMG',
    'IMEA.DE':'IEMG',  'XMME.DE':'EEM',   'IQQD.DE':'EEM',   'SPY5.DE':'SPY',
    'LCUW.DE':'IVV',   'IUSE.DE':'IVV',   'SXR2.DE':'IVV',   'VUSA.L':'IVV',
    'CSPX.L':'IVV',    'C500.DE':'IVV',   'SP5C.DE':'IVV',   'PRAW.DE':'URTH',
    'PRWA.DE':'URTH',  'EXW1.DE':'FEZ',   'MEUD.DE':'FEZ',   'LYPS.DE':'FEZ',
    'IQQY.DE':'VGK',   'IEUA.DE':'VGK',   'SPYY.DE':'VGK',   'XESC.DE':'FEZ',
    'EXS1.DE':'EWG',   'DBXD.DE':'EWG',   'DAXE.DE':'EWG',   'EXV5.DE':'EWJ',
    'XDJP.DE':'EWJ',   'IQQJ.DE':'EWJ',   'IQQC.DE':'MCHI',  'IUSN.DE':'SCHA',
    'ZPRV.DE':'IWM',   'EXI5.DE':'IJH',   'ISPA.DE':'SCHD',  'QDIV.DE':'VYM',
    'XDIV.DE':'VYM',   'XDWT.DE':'IXN',   'QDVE.DE':'XLK',   'IUIT.DE':'IXN',
    'XDWH.DE':'IXV',   'QDVG.DE':'XLV',   'HEAL.DE':'IXV',   'XDWF.DE':'IXG',
    'SXRV.DE':'XLC',   'XDWU.DE':'XLU',   'XMIN.DE':'INDA',  'XMKR.DE':'EWY',
    'IS3W.DE':'EWT',   'IQQH.DE':'ICLN',  'VHYL.L':'VYM',
}


@st.cache_data(ttl=86400, show_spinner=False)
def _etf_top_holdings_cached(ticker: str) -> list:
    """Top-Holdings eines ETFs als [(name, symbol, weight_frac), ...] — gecacht 24h."""
    import concurrent.futures as _cf_eth
    def _parse(fd):
        th = getattr(fd, 'top_holdings', None)
        if th is None or (hasattr(th, 'empty') and th.empty):
            return []
        _nc = next((c for c in ['holdingName','name','Symbol','symbol'] if c in th.columns), None)
        _wc = next((c for c in ['holdingPercent','weight','Weight','Holding Percent'] if c in th.columns), None)
        _sc = next((c for c in ['symbol','Symbol','ticker','Ticker'] if c in th.columns), None)
        rows = []
        for _, row in th.iterrows():
            n = str(row[_nc]) if _nc else ''
            w = float(row[_wc]) if _wc and pd.notna(row.get(_wc)) else 0.0
            s = str(row[_sc]) if _sc and pd.notna(row.get(_sc, '')) else ''
            if s in ('nan', 'None', ''): s = ''
            if w > 0 and n:
                rows.append((n, s, w if w <= 1.0 else w / 100.0))
        return rows
    # yFinance — zuerst direkt, dann US-Datenticker
    for _t in [ticker, _PF_ETF_DATA_TKR.get(ticker, '')]:
        if not _t:
            continue
        try:
            def _do(t=_t):
                return _parse(yf.Ticker(t).funds_data)
            with _cf_eth.ThreadPoolExecutor(max_workers=1) as _ex:
                rows = _ex.submit(_do).result(timeout=6.0)
            if rows:
                return rows
        except Exception:
            pass
    # FMP fallback
    if FMP_API_KEY:
        for _t in [ticker, _PF_ETF_DATA_TKR.get(ticker, ticker)]:
            if not _t:
                continue
            try:
                _fr = requests.get(
                    f"https://financialmodelingprep.com/api/v3/etf-holder/{_t}",
                    params={'apikey': FMP_API_KEY}, timeout=5)
                if _fr.ok and _fr.json():
                    rows = []
                    for h in _fr.json()[:25]:
                        n = h.get('asset') or h.get('name') or ''
                        s = h.get('symbol') or ''
                        w = float(h.get('weightPercentage') or 0) / 100.0
                        if w > 0 and n:
                            rows.append((n, s, w))
                    if rows:
                        return rows
            except Exception:
                pass
    return []


def _portfolio_price(ticker: str):
    """Wrapper → aktueller Kurs in EUR (gecacht via _portfolio_quote_ext)."""
    return _portfolio_quote_ext(ticker).get('price_eur')


@st.cache_data(ttl=3600, show_spinner=False)
def _build_performance(csv_bytes: bytes, benchmark_ticker: str):
    """Portfolio vs Benchmark Performance. Gibt (dates, invested, bm_value) zurück."""
    df = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            df = pd.read_csv(io.BytesIO(csv_bytes), sep=';', decimal=',',
                             encoding=enc, dtype=str)
            break
        except Exception:
            continue
    if df is None or df.empty:
        return None
    df.columns = df.columns.str.strip()
    date_col = None
    for c in ['Datum', 'Ausführungsdatum', 'Ausführung Datum', 'Handelsdatum', 'Datum/Uhrzeit', 'Date']:
        if c in df.columns:
            date_col = c
            break
    if date_col is None:
        return None
    if 'Status' in df.columns:
        df = df[df['Status'] == 'ausgeführt'].copy()
    if df.empty or 'Richtung' not in df.columns or 'Wert' not in df.columns:
        return None
    df['_date'] = pd.to_datetime(df[date_col].astype(str).str[:10], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['_date'])
    df['_wert'] = pd.to_numeric(
        df['Wert'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0.0)
    _sell_types = ['Verkauf', 'Rückgabe', 'Rücknahme', 'Entnahme', 'Depot-Ausbuchung']
    _buy_types  = ['Kauf', 'Sparplan', 'Depot-Einbuchung']
    df['_eur'] = df['_wert'].abs()
    df.loc[df['Richtung'].isin(_sell_types), '_eur'] = -df.loc[df['Richtung'].isin(_sell_types), '_wert'].abs()
    df = df[df['Richtung'].isin(_buy_types + _sell_types)].sort_values('_date').reset_index(drop=True)
    if df.empty:
        return None
    first_date = df['_date'].min()
    today = pd.Timestamp.today().normalize()
    try:
        bm_raw = yf.download(benchmark_ticker, start=first_date - pd.Timedelta(days=10),
                             end=today + pd.Timedelta(days=1), interval='1d',
                             progress=False, auto_adjust=True)
        if bm_raw.empty:
            return None
        bm = bm_raw['Close'].squeeze()
        if isinstance(bm, pd.DataFrame):
            bm = bm.iloc[:, 0]
        bm.index = pd.to_datetime(bm.index).normalize()
    except Exception:
        return None
    month_ends = pd.date_range(
        start=first_date.to_period('M').to_timestamp('M'),
        end=today.to_period('M').to_timestamp('M'),
        freq='ME'
    )
    dates_out, invested_out, bm_val_out = [], [], []
    cumulative_invested = 0.0
    bm_units = 0.0
    tx_pointer = 0
    for month_end in month_ends:
        while tx_pointer < len(df) and df.loc[tx_pointer, '_date'] <= month_end:
            row = df.loc[tx_pointer]
            eur = row['_eur']
            bm_before = bm[bm.index <= row['_date']]
            if not bm_before.empty:
                bm_price_at_tx = float(bm_before.iloc[-1])
                if bm_price_at_tx > 0 and abs(eur) > 1e-6:
                    bm_units += eur / bm_price_at_tx
            cumulative_invested += eur
            tx_pointer += 1
        if cumulative_invested <= 0:
            continue
        bm_at_end = bm[bm.index <= month_end]
        if bm_at_end.empty:
            continue
        bm_price_end = float(bm_at_end.iloc[-1])
        dates_out.append(month_end)
        invested_out.append(round(cumulative_invested, 2))
        bm_val_out.append(round(bm_units * bm_price_end, 2))
    if not dates_out:
        return None
    return dates_out, invested_out, bm_val_out

_SECTOR_DE = {
    'Technology': 'IT & Technologie',
    'Communication Services': 'Telekommunikation',
    'Consumer Cyclical': 'Nicht-Basiskonsumgüter',
    'Consumer Defensive': 'Basiskonsumgüter',
    'Financial Services': 'Finanzwesen',
    'Healthcare': 'Gesundheitswesen',
    'Industrials': 'Industrie',
    'Energy': 'Energie',
    'Basic Materials': 'Grundstoffe',
    'Real Estate': 'Immobilien',
    'Utilities': 'Versorger',
}

_SECTOR_COLORS = {
    'IT & Technologie': '#1565c0',
    'Telekommunikation': '#00acc1',
    'Nicht-Basiskonsumgüter': '#43a047',
    'Basiskonsumgüter': '#81c784',
    'Finanzwesen': '#f9a825',
    'Gesundheitswesen': '#7cb342',
    'Industrie': '#8e24aa',
    'Energie': '#e64a19',
    'Grundstoffe': '#795548',
    'Immobilien': '#f06292',
    'Versorger': '#ffd740',
    'ETF / Fonds': '#42a5f5',
    'Krypto': '#ff7043',
    'Optionsscheine': '#90a4ae',
    'Sonstige': '#546e7a',
}

_REGION_COLORS = {
    'Amerika': '#1565c0',
    'Europa': '#43a047',
    'Asien': '#e64a19',
    'Australien': '#ffd740',
    'Global': '#42a5f5',
    'Sonstige': '#546e7a',
}

_ASSET_COLORS = {
    'Aktien': '#1565c0',
    'ETF / Fonds': '#42a5f5',
    'Krypto': '#ff7043',
    'Optionsscheine': '#90a4ae',
}

_EU_SFX  = {'DE','PA','AS','L','MI','MC','SW','ST','CO','OL','HE','BR','VX','IR','LS','VI','WA','PR'}
_ASI_SFX = {'T','HK','SS','SZ','KS','BO','NS','SI','KL','BK','TWO','TW'}
_AUS_SFX = {'AX','NZ'}
_AM_SFX  = {'SA','MX','CN','TO','V'}


def _ticker_to_region(ticker: str) -> str:
    if not ticker or '.' not in ticker:
        return 'Amerika'
    sfx = ticker.rsplit('.', 1)[1].upper()
    if sfx in _EU_SFX:  return 'Europa'
    if sfx in _ASI_SFX: return 'Asien'
    if sfx in _AUS_SFX: return 'Australien'
    if sfx in _AM_SFX:  return 'Amerika'
    return 'Sonstige'


_SFX_COUNTRY = {
    'DE':'Deutschland','F':'Deutschland','BE':'Deutschland','MU':'Deutschland','HA':'Deutschland',
    'PA':'Frankreich',
    'L':'UK','IL':'UK',
    'AS':'Niederlande',
    'MI':'Italien',
    'MC':'Spanien',
    'SW':'Schweiz','VX':'Schweiz',
    'ST':'Schweden',
    'CO':'Dänemark',
    'OL':'Norwegen',
    'HE':'Finnland',
    'BR':'Belgien',
    'IR':'Irland',
    'LS':'Portugal',
    'VI':'Österreich',
    'WA':'Polen',
    'KS':'Südkorea','KQ':'Südkorea',
    'T':'Japan',
    'HK':'Hongkong',
    'SS':'China','SZ':'China',
    'BO':'Indien','NS':'Indien',
    'SI':'Singapur',
    'KL':'Malaysia',
    'BK':'Thailand',
    'TW':'Taiwan','TWO':'Taiwan',
    'AX':'Australien',
    'NZ':'Neuseeland',
    'SA':'Brasilien',
    'MX':'Mexiko',
    'TO':'Kanada','V':'Kanada','CN':'Kanada',
}


def _ticker_to_country(ticker: str) -> str:
    if not ticker or '.' not in ticker:
        return 'USA'
    sfx = ticker.rsplit('.', 1)[1].upper()
    return _SFX_COUNTRY.get(sfx, 'USA')


# GDR-ISINs haben US-ISIN aber echtes Heimatland — Ticker-Suffix würde 'USA' liefern
_GDR_COUNTRY = {
    'US78392B1070': 'Südkorea',  # SK Hynix GDR
    'US7960502018': 'Südkorea',  # Samsung Electronics GDR Pref
    'US7960508882': 'Südkorea',  # Samsung Electronics GDR
    'CNE100006M58': 'China',     # Midea Group
}


_ISIN_SECTOR_HARD = {
    'US78392B1070': 'Technology',        # SK Hynix GDR
    'US7960502018': 'Technology',        # Samsung Electronics GDR Pref
    'US7960508882': 'Technology',        # Samsung Electronics GDR Stamm
    'CNE100006M58': 'Consumer Cyclical', # Midea Group
}


@st.cache_data(ttl=86400, show_spinner=False)
def _get_ticker_info_cached(ticker: str) -> dict:
    """Sektor + QuoteType via yFinance (gecacht 24h). Timeout 4s pro Call."""
    import concurrent.futures as _cf
    _empty = {'sector': '', 'quote_type': 'EQUITY', 'recommendation': '',
              'target_native': None, 'div_rate_native': 0.0}
    try:
        # quote_type sofort via fast_info (kein Netzwerk-Hang möglich)
        fi = yf.Ticker(ticker).fast_info
        qt = str(getattr(fi, 'quote_type', 'EQUITY') or 'EQUITY').upper()
        _empty['quote_type'] = qt
        # Vollständige Info mit 4s Timeout
        with _cf.ThreadPoolExecutor(max_workers=1) as _ex:
            _fut = _ex.submit(lambda: yf.Ticker(ticker).info)
            try:
                info = _fut.result(timeout=4.0)
                return {
                    'sector':          info.get('sector') or '',
                    'quote_type':      (info.get('quoteType') or qt).upper(),
                    'recommendation':  (info.get('recommendationKey') or '').lower(),
                    'target_native':   info.get('targetMeanPrice'),
                    'div_rate_native': info.get('trailingAnnualDividendRate') or 0.0,
                }
            except _cf.TimeoutError:
                return _empty
    except Exception:
        return _empty


@st.cache_data(ttl=3600, show_spinner=False)
def _sparklines_bulk(tickers: tuple) -> dict:
    """Batch-Download 3M-Wochendaten → SVG-Sparklines (gecacht 1h, 1 API-Call)."""
    if not tickers:
        return {}
    try:
        raw = yf.download(list(tickers), period='3mo', interval='1wk',
                          progress=False, auto_adjust=True)
        if raw.empty:
            return {}
        close = raw['Close']

        def _to_svg(vals):
            if len(vals) < 4:
                return ''
            mn, mx = min(vals), max(vals)
            rng = mx - mn or 1
            w, h = 110, 32
            pts = ' '.join(f"{int(i/(len(vals)-1)*w)},{int((1-(v-mn)/rng)*(h-6)+3)}"
                           for i, v in enumerate(vals))
            clr = _C_POSITIVE if vals[-1] >= vals[0] else _C_NEGATIVE
            return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
                    f'<polyline points="{pts}" fill="none" stroke="{clr}" '
                    f'stroke-width="1.8" stroke-linejoin="round"/></svg>')

        result = {}
        if isinstance(close, pd.Series):
            vals = close.dropna().tolist()
            if tickers:
                result[tickers[0]] = _to_svg(vals)
        else:
            for col in close.columns:
                vals = close[col].dropna().tolist()
                svg = _to_svg(vals)
                if svg:
                    result[str(col)] = svg
        return result
    except Exception:
        return {}


@st.cache_data(ttl=300, show_spinner=False)
def _calc_portfolio_irr(csv_bytes: bytes, current_eur_value: float):
    """IZF (Internen Zinsfuß) + einfache Rendite aus Orderhistorie-Cashflows.
    Gibt zurück: (irr_annual, simple_return, days_total, total_invested) oder Nones."""
    current_eur_value = round(current_eur_value, 0)
    df = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            df = pd.read_csv(io.BytesIO(csv_bytes), sep=';', decimal=',', encoding=enc, dtype=str)
            break
        except Exception:
            continue
    if df is None or df.empty:
        return None, None, None, None
    df.columns = df.columns.str.strip()
    date_col = None
    for c in ['Datum', 'Ausführungsdatum', 'Ausführung Datum', 'Handelsdatum', 'Datum/Uhrzeit', 'Date']:
        if c in df.columns:
            date_col = c
            break
    if not date_col or 'Richtung' not in df.columns or 'Wert' not in df.columns:
        return None, None, None, None
    if 'Status' in df.columns:
        df = df[df['Status'] == 'ausgeführt'].copy()
    df['_date'] = pd.to_datetime(df[date_col].astype(str).str[:10], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['_date'])
    df['_wert'] = pd.to_numeric(
        df['Wert'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0.0)
    _sell_t = ['Verkauf', 'Rückgabe', 'Rücknahme', 'Entnahme', 'Depot-Ausbuchung']
    _buy_t  = ['Kauf', 'Sparplan', 'Depot-Einbuchung']
    df = df[df['Richtung'].isin(_buy_t + _sell_t)].copy()
    df['_cf'] = -df['_wert'].abs()
    df.loc[df['Richtung'].isin(_sell_t), '_cf'] = df.loc[df['Richtung'].isin(_sell_t), '_wert'].abs()
    df = df.sort_values('_date').reset_index(drop=True)
    if df.empty:
        return None, None, None, None
    today = pd.Timestamp.today().normalize()
    t0 = df['_date'].min()
    days_total = max(1, (today - t0).days)
    total_invested = df.loc[df['_cf'] < 0, '_cf'].abs().sum()
    total_received = df.loc[df['_cf'] > 0, '_cf'].sum()
    if total_invested <= 0:
        return None, None, days_total, total_invested
    simple_return = (current_eur_value + total_received - total_invested) / total_invested
    if days_total < 14:
        return None, simple_return, days_total, total_invested
    flows = list(zip(df['_date'].tolist(), df['_cf'].tolist()))
    flows.append((today, float(current_eur_value)))

    def _npv(r):
        acc = 0.0
        for d, cf in flows:
            yrs = (d - t0).days / 365.25
            acc += cf / ((1.0 + r) ** yrs)
        return acc

    lo, hi = -0.95, 15.0
    try:
        npv_lo, npv_hi = _npv(lo), _npv(hi)
        if npv_lo * npv_hi > 0:
            return None, simple_return, days_total, total_invested
        for _ in range(200):
            mid = (lo + hi) / 2.0
            if _npv(mid) > 0:
                lo = mid
            else:
                hi = mid
            if hi - lo < 1e-8:
                break
        irr = (lo + hi) / 2.0
    except Exception:
        return None, simple_return, days_total, total_invested
    return irr, simple_return, days_total, total_invested


@st.cache_data(ttl=3600, show_spinner=False)
def _detect_savings_plans(csv_bytes: bytes) -> list:
    """Erkennt regelmäßige Sparpläne: gleiche ISIN, regelmäßige Intervalle, ähnliche Beträge."""
    df = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            df = pd.read_csv(io.BytesIO(csv_bytes), sep=';', decimal=',', encoding=enc, dtype=str)
            break
        except Exception:
            continue
    if df is None or df.empty:
        return []
    df.columns = df.columns.str.strip()
    date_col = None
    for c in ['Datum', 'Ausführungsdatum', 'Ausführung Datum', 'Handelsdatum', 'Datum/Uhrzeit', 'Date']:
        if c in df.columns:
            date_col = c
            break
    if not date_col or 'Richtung' not in df.columns or 'Wert' not in df.columns:
        return []
    if 'Status' in df.columns:
        df = df[df['Status'] == 'ausgeführt'].copy()
    _buy_types = ['Kauf', 'Sparplan', 'Depot-Einbuchung']
    df = df[df['Richtung'].isin(_buy_types)].copy()
    df['_date'] = pd.to_datetime(df[date_col].astype(str).str[:10], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['_date'])
    df['_wert'] = pd.to_numeric(
        df['Wert'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
        errors='coerce'
    ).fillna(0.0).abs()
    plans = []
    for isin, grp in df.groupby('ISIN'):
        grp = grp.sort_values('_date').reset_index(drop=True)
        if len(grp) < 3:
            continue
        dates   = grp['_date'].tolist()
        amounts = grp['_wert'].tolist()
        ivls    = [(dates[i+1] - dates[i]).days for i in range(len(dates) - 1)]
        if not ivls:
            continue
        mean_iv = sum(ivls) / len(ivls)
        if mean_iv < 7:
            continue
        std_iv  = (sum((x - mean_iv) ** 2 for x in ivls) / len(ivls)) ** 0.5 if len(ivls) > 1 else 0
        cv_iv   = std_iv / mean_iv if mean_iv > 0 else 1
        if cv_iv > 0.65:
            continue
        if   13 <= mean_iv <= 20:  freq = "2-wöchentlich"
        elif 20 <= mean_iv <= 45:  freq = "monatlich"
        elif 45 <= mean_iv <= 80:  freq = "zweimonatlich"
        elif 80 <= mean_iv <= 105: freq = "quartalsweise"
        else:                      freq = f"alle ~{int(mean_iv)} Tage"
        avg_amt = sum(amounts) / len(amounts)
        name    = grp['Name'].iloc[0] if 'Name' in grp.columns else isin
        plans.append({'isin': isin, 'name': str(name)[:38], 'count': len(grp),
                      'avg_amount': avg_amt, 'total': sum(amounts),
                      'start': dates[0].strftime('%b %Y'), 'last': dates[-1].strftime('%b %Y'),
                      'freq': freq})
    return sorted(plans, key=lambda x: x['total'], reverse=True)


@st.cache_data(ttl=3600, show_spinner=False)
def _calc_realized_pnl(csv_bytes: bytes) -> dict:
    """Realisierte Gewinne/Verluste (Durchschnittskostenmethode, wie deutsches Broker-Standard).
    Gibt zurück: {'total_pnl': float, 'total_sell_value': float, 'positions': list[dict]}"""
    df = None
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            df = pd.read_csv(io.BytesIO(csv_bytes), sep=';', decimal=',', encoding=enc, dtype=str)
            break
        except Exception:
            continue
    if df is None or df.empty:
        return {}
    df.columns = df.columns.str.strip()
    needed = {'Richtung', 'ISIN', 'Name', 'Anzahl ausgeführt', 'Wert'}
    if not needed.issubset(df.columns):
        return {}
    if 'Status' in df.columns:
        df = df[df['Status'] == 'ausgeführt'].copy()
    for col in ['Anzahl ausgeführt', 'Wert']:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce').fillna(0.0)
    _buy_types  = ['Kauf', 'Sparplan', 'Depot-Einbuchung']
    _sell_types = ['Verkauf', 'Rückgabe', 'Rücknahme', 'Entnahme', 'Depot-Ausbuchung']
    buys  = df[df['Richtung'].isin(_buy_types)].copy()
    sells = df[df['Richtung'].isin(_sell_types)].copy()
    if buys.empty or sells.empty:
        return {'total_pnl': 0.0, 'total_sell_value': 0.0, 'positions': []}
    buy_agg = (buys.groupby('ISIN')
               .agg(name=('Name', 'first'),
                    total_bought=('Anzahl ausgeführt', 'sum'),
                    total_cost=('Wert', lambda x: x.abs().sum()))
               .reset_index())
    buy_agg['avg_cost'] = buy_agg['total_cost'] / buy_agg['total_bought'].replace(0, float('nan'))
    sell_agg = (sells.groupby('ISIN')
                .agg(name=('Name', 'first'),
                     total_sold=('Anzahl ausgeführt', 'sum'),
                     sell_value=('Wert', lambda x: x.abs().sum()))
                .reset_index())
    merged = sell_agg.merge(buy_agg[['ISIN','avg_cost']], on='ISIN', how='left')
    merged['cost_of_sold'] = merged['avg_cost'] * merged['total_sold']
    merged['pnl'] = merged['sell_value'] - merged['cost_of_sold']
    no_cost_isins = merged[merged['avg_cost'].isna()]['ISIN'].tolist()
    positions = []
    for _, row in merged.iterrows():
        if pd.notna(row['pnl']):
            positions.append({
                'isin': row['ISIN'], 'name': str(row['name'])[:35],
                'shares_sold': row['total_sold'], 'sell_value': row['sell_value'],
                'cost_of_sold': row['cost_of_sold'], 'pnl': row['pnl'],
            })
    positions.sort(key=lambda x: abs(x['pnl']), reverse=True)
    total_pnl = merged['pnl'].sum()
    total_sell = merged['sell_value'].sum()
    return {'total_pnl': total_pnl, 'total_sell_value': total_sell,
            'positions': positions, 'no_cost_isins': no_cost_isins}


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px 0;'>
        <span style='font-size:2rem;'>📈</span>
        <div style='color:{_C_ACCENT}; font-size:1.3rem; font-weight:700; margin-top:6px;'>StocksMB</div>
        <div style='color:#37474f; font-size:0.75rem;'>Aktienanalyse Tool</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Hell/Dunkel-Toggle ────────────────────────────────────────────
    _lm = st.session_state.get("light_mode", False)
    st.toggle("🌙 Dunkel-Modus" if _lm else "☀️ Hell-Modus", key="light_mode")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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
        st.markdown(f"<div style='color:{_C_ACCENT}; font-size:0.8rem; padding:6px 4px;'>{st.session_state['search_msg']}</div>", unsafe_allow_html=True)

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
        st.session_state["show_portfolio"] = False
        st.session_state["show_stocks"] = False
        st.rerun()
    if not st.session_state.get("show_stocks") and st.button("💡 Aktienideen", use_container_width=True):
        st.session_state["show_stocks"] = True
        st.session_state["show_landing"] = False
        st.session_state["show_portfolio"] = False
        st.session_state["show_etf_analyzer"] = False
        st.rerun()
    if st.button("📁 Mein Portfolio", use_container_width=True):
        st.session_state["show_portfolio"] = True
        st.session_state["show_landing"] = False
        st.session_state["show_etf_analyzer"] = False
        st.session_state["show_stocks"] = False
        st.rerun()
    if st.button("🔎 ETF-Analyzer", use_container_width=True):
        st.session_state["show_etf_analyzer"] = True
        st.session_state["show_portfolio"] = False
        st.session_state["show_landing"] = False
        st.session_state["show_stocks"] = False
        st.rerun()

    st.markdown("<div class='section-header'>⚙️ Einstellungen</div>", unsafe_allow_html=True)
    show_peers = st.toggle("Peer-Vergleich anzeigen", value=True)
    show_insider = st.toggle("Insider-Transaktionen", value=True)
    show_dcf = st.toggle("DCF Rechner", value=True)

    # ── Konto ──────────────────────────────────────────────────────────
    _wl_pw = os.getenv("PORTFOLIO_PASSWORD", "")
    if _wl_pw:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🔐 Konto</div>", unsafe_allow_html=True)
        if st.session_state.get("wl_unlocked"):
            st.markdown(
                "<div style='color:{_C_ACCENT};font-size:0.78rem;padding:4px 0 6px 0;'>🔓 Angemeldet</div>",
                unsafe_allow_html=True)
            if st.button("Abmelden", use_container_width=True, key="wl_logout"):
                st.session_state["wl_unlocked"] = False
                st.session_state["watchlist"] = []
                st.rerun()
        else:
            _pw_inp = st.text_input("Passwort", type="password", key="wl_pw_inp",
                                     label_visibility="collapsed", placeholder="Passwort eingeben…")
            if st.button("Entsperren", use_container_width=True, key="wl_unlock_btn"):
                if _pw_inp == _wl_pw:
                    st.session_state["wl_unlocked"] = True
                    st.session_state["watchlist"] = _wl_load_file()
                    st.rerun()
                else:
                    st.error("Falsches Passwort.")

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
                    _wl_save_file(st.session_state["watchlist"])
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
    import datetime as _qdt
    _q_idx = _qdt.date.today().timetuple().tm_yday % len(_QUOTES)
    _q_text, _q_author = _QUOTES[_q_idx]
    if st.session_state.get("light_mode"):
        st.markdown(f"""
<div style='background:#f0f7ff;border:1px solid #bdd7f5;border-left:4px solid #1565c0;
border-radius:14px;padding:20px 24px;margin-bottom:28px;'>
  <div style='color:#4a5568;font-size:0.65rem;text-transform:uppercase;
  letter-spacing:.1em;margin-bottom:10px;'>💬 Zitat des Tages</div>
  <div style='color:#2d3748;font-size:0.95rem;line-height:1.7;
  font-style:italic;'>„{_q_text}"</div>
  <div style='color:#1565c0;font-size:0.78rem;font-weight:600;
  margin-top:10px;text-align:right;'>— {_q_author}</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div style='background:linear-gradient(135deg,#0a1628,#0d1f3c);
border:1px solid #1e3a5f;border-left:4px solid #00e5ff;
border-radius:14px;padding:20px 24px;margin-bottom:28px;'>
  <div style='color:#78909c;font-size:0.65rem;text-transform:uppercase;
  letter-spacing:.1em;margin-bottom:10px;'>💬 Zitat des Tages</div>
  <div style='color:#cfd8dc;font-size:0.95rem;line-height:1.7;
  font-style:italic;'>„{_q_text}"</div>
  <div style='color:{_C_ACCENT};font-size:0.78rem;font-weight:600;
  margin-top:10px;text-align:right;'>— {_q_author}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; padding:48px 0 32px 0;">
        <div style="font-size:3rem; font-weight:800; color:#fff; letter-spacing:-1px;">
            📈 <span style="color:#00e5ff;">Stocks</span>MB
        </div>
        <div style="color:{_C_ACCENT}; font-size:1.1rem; margin-top:10px;">
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
            clr = _C_POSITIVE if pct >= 0 else _C_NEGATIVE
            arrow = "▲" if pct >= 0 else "▼"
            px_str = f"{d['cur']}{d['price']:,.0f}"
            col.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:14px 8px; cursor:default;">
                <div class="metric-label" style="font-size:0.7rem;">{name}</div>
                <div style="color:{_C_TEXT_PRIMARY}; font-size:1.05rem; font-weight:700; margin:4px 0;">{px_str}</div>
                <div style="color:{clr}; font-size:0.82rem; font-weight:600;">{arrow} {abs(pct):.2f}%</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Makro-Dashboard ───────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Makro-Dashboard</div>", unsafe_allow_html=True)
    macro = _pf_disk_load("macro_basic_v4", max_age_hours=24)
    if macro is None:
        with st.spinner("Lade Makrodaten…"):
            macro = load_macro_data()
        _pf_disk_save("macro_basic_v4", macro)

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
        st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin-bottom:6px;'>💱 Wechselkurse</div>",
                    unsafe_allow_html=True)
        fx_cols = st.columns(len(macro["fx"]))
        for col, (label, d) in zip(fx_cols, macro["fx"].items()):
            pct = d["pct"]
            clr = _C_POSITIVE if pct >= 0 else _C_NEGATIVE
            arrow = "▲" if pct >= 0 else "▼"
            _tip = _FX_TIPS.get(label, "")
            _tip_html = (f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                         f'<span class="tt-box">{_tip}</span></span>') if _tip else ""
            col.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:10px 6px;">
                <div class="metric-label" style="font-size:0.68rem;">{label}{_tip_html}</div>
                <div style="color:{_C_TEXT_PRIMARY}; font-size:0.95rem; font-weight:700; margin:3px 0;">
                    {d['price']:.{4 if d['price'] < 10 else 2}f}
                </div>
                <div style="color:{clr}; font-size:0.75rem;">{arrow} {abs(pct):.2f}%</div>
            </div>""", unsafe_allow_html=True)

    if macro["macro"]:
        st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin:10px 0 6px 0;'>🌐 Makro-Indikatoren</div>",
                    unsafe_allow_html=True)
        macro_items = list(macro["macro"].items())
        mc_cols = st.columns(len(macro_items))
        for col, (label, d) in zip(mc_cols, macro_items):
            val = d["value"]
            unit = d["unit"]
            if "Inflation" in label:
                clr = _C_NEGATIVE if val > 3.0 else _C_NEUTRAL if val > 2.0 else _C_POSITIVE
            elif "Arbeitslosigkeit" in label:
                clr = _C_NEGATIVE if val > 6.0 else _C_NEUTRAL if val > 4.5 else _C_POSITIVE
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

    # ── BIP-Wachstum ──────────────────────────────────────────────────
    _gdp_specs_ui = ["🇺🇸 USA", "🇪🇺 Eurozone", "🇩🇪 Deutschland", "🇨🇳 China", "🇯🇵 Japan", "🇬🇧 UK", "🇮🇳 Indien"]
    _gdp_data = macro.get("gdp", {})
    st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin:10px 0 6px 0;'>📈 BIP-Wachstum (YoY, aktuellstes Quartal)</div>",
                unsafe_allow_html=True)
    _gdp_cols = st.columns(len(_gdp_specs_ui))
    for _gc, _glab in zip(_gdp_cols, _gdp_specs_ui):
        _gval = _gdp_data.get(_glab)
        if _gval is not None:
            _gc_clr = _C_POSITIVE if _gval > 2.5 else _C_POSITIVE_SFT if _gval > 1.0 else \
                      _C_NEUTRAL if _gval >= 0 else _C_NEGATIVE
            _gdisp = f"{_gval:+.1f}%"
        else:
            _gc_clr, _gdisp = "#37474f", "…"
        _gc.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:10px 6px;">
            <div class="metric-label" style="font-size:0.68rem; line-height:1.3;">{_glab}</div>
            <div style="color:{_gc_clr}; font-size:1.0rem; font-weight:700; margin:4px 0;">
                {_gdisp}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Misery Index + Yield Curve + Consumer Sentiment ───────────────
    _misery      = macro.get("misery", {})
    _yc          = macro.get("yield_curve")
    _cs          = macro.get("consumer_sentiment")
    _ez_unemp_d  = macro.get("ez_unemployment")
    _konjunktur_specs = [
        ("misery", "🌡️ Misery 🇺🇸 USA",         _misery.get("🇺🇸 USA")),
        ("misery", "🌡️ Misery 🇪🇺 Eurozone",    _misery.get("🇪🇺 Eurozone")),
        ("yc",     "📉 Zinsstruktur (10J-2J)",    _yc),
        ("cs",     "🛒 Konsumklima (Michigan)",   _cs),
        ("ez_u",   "🇪🇺 Arbeitslosigkeit",        _ez_unemp_d),
    ]

    if True:  # always show section
        st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin:10px 0 6px 0;'>🌡️ Konjunkturindikatoren</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin:10px 0 6px 0;'>🌡️ Konjunkturindikatoren</div>",
                    unsafe_allow_html=True)
        _kj_cols = st.columns(len(_konjunktur_specs))
        _kj_tips = {
            "misery": "Misery Index = Arbeitslosenquote + Inflationsrate. Historischer US-Schnitt: ~8–10 %. Über 12 = belastend für Konsumenten.",
            "yc":     "Zinskurve: 10J-Rendite minus 2J-Rendite (USA). Negativ = invertiert = historisch zuverlässiger Rezessionsindikator (6–18 Monate Vorlauf).",
            "cs":     "University of Michigan Consumer Sentiment Index. Historischer Schnitt: ~86. Unter 65 = ausgeprägte Konsumzurückhaltung.",
            "ez_u":   "Eurozone Arbeitslosenquote (ILO, saisonbereinigt). Historisch niedrig unter 7 %, historisch hoch über 10 %.",
        }
        for _kc, (_ktype, _klabel, _kval) in zip(_kj_cols, _konjunktur_specs):
            _kc_tip = _kj_tips.get(_ktype, "")
            _tip_html = (f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                         f'<span class="tt-box">{_kc_tip}</span></span>') if _kc_tip else ""
            if _kval is None:
                _kc_clr, _kdisp = "#37474f", "…"
            elif _ktype == "misery":
                _kc_clr = _C_NEGATIVE if _kval > 14 else _C_NEUTRAL if _kval > 10 else _C_POSITIVE
                _kdisp = f"{_kval:.1f}%"
            elif _ktype == "yc":
                _kc_clr = _C_NEGATIVE if _kval < 0 else _C_NEUTRAL if _kval < 0.3 else _C_POSITIVE
                _kdisp = f"{_kval:+.2f}%"
            elif _ktype == "cs":
                _kc_clr = _C_POSITIVE if _kval > 80 else _C_NEUTRAL if _kval > 65 else _C_NEGATIVE
                _kdisp = f"{_kval:.0f}"
            else:
                _kc_clr = _C_NEGATIVE if _kval > 8 else _C_NEUTRAL if _kval > 6.5 else _C_POSITIVE
                _kdisp = f"{_kval:.1f}%"
            _kc.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:10px 6px;">
                <div class="metric-label" style="font-size:0.68rem; line-height:1.3;">{_klabel}{_tip_html}</div>
                <div style="color:{_kc_clr}; font-size:1.0rem; font-weight:700; margin:4px 0;">
                    {_kdisp}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Buffett-Indikator & S&P 500 PEG ──────────────────────────────
    _bi             = macro.get("buffett")
    _sp_peg         = macro.get("sp500_peg")
    _sp_pe          = macro.get("sp500_pe")
    _sp_eg          = macro.get("sp500_eg")
    _peg_source     = macro.get("sp500_peg_source", "")
    _sp_trailing_pe = macro.get("sp500_trailing_pe")
    _sp_forward_pe  = macro.get("sp500_forward_pe")
    if _bi or _sp_peg or _sp_pe or _sp_trailing_pe:
        _bi_col, _peg_col = st.columns(2)

        if _bi:
            with _bi_col:
                if _bi < 75:   _bi_clr, _bi_lbl = _C_POSITIVE, "Unterbewertet"
                elif _bi < 90: _bi_clr, _bi_lbl = _C_POSITIVE_SFT, "Fair bewertet"
                elif _bi < 115:_bi_clr, _bi_lbl = _C_NEUTRAL, "Leicht überbewertet"
                elif _bi < 140:_bi_clr, _bi_lbl = "#ff8f00", "Überbewertet"
                else:          _bi_clr, _bi_lbl = _C_NEGATIVE, "Stark überbewertet"
                _bi_pct_bar = min(int(_bi / 200 * 100), 100)
                _bi_vs_hist = "deutlich über dem historischen Schnitt (80–100%)" if _bi > 130 else \
                              "über dem historischen Schnitt (80–100%)" if _bi > 100 else \
                              "im historischen Normalbereich (80–100%)" if _bi >= 80 else \
                              "unter dem historischen Schnitt (80–100%)"
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">Buffett-Indikator'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">Gesamte US-Marktkapitalisierung (Wilshire 5000) ÷ US-BIP. Buffett nannte ihn 1999/2000 als Warnsignal vor dem Dotcom-Crash. Schwäche: kein Timing-Werkzeug — Märkte können jahrelang "überbewertet" bleiben (1996–2000). Historischer Mittelwert: ~80–100%.</span></span></span>'
                    f'<span style="color:{_bi_clr};font-weight:700;">{_bi:.0f}%</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_bi_pct_bar}%;height:5px;border-radius:4px;background:{_bi_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>0%</span><span style="color:{_bi_clr};">{_bi_lbl}</span><span>200%</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;75% = günstig · 75–90% = fair · 90–115% = leicht teuer · &gt;115% = teuer · &gt;140% = Warnsignal</div>'
                    f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>Einordnung:</b> Aktuell {_bi:.0f}% — {_bi_vs_hist}. '
                    f'Als Makro-Kontext-Signal geeignet, nicht als Timing-Tool. '
                    f'Treffsicher 1999 &amp; 2007, aber kein zuverlässiger Einstiegszeitpunkt.</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        if _sp_peg or _sp_pe or _sp_trailing_pe:
            with _peg_col:
                _pe_ref = _sp_trailing_pe or _sp_pe or 0
                if _sp_peg:
                    if _sp_peg < 1.5:   _peg_clr, _peg_lbl = _C_POSITIVE, "Günstig"
                    elif _sp_peg < 2.0: _peg_clr, _peg_lbl = _C_POSITIVE_SFT, "Fair"
                    elif _sp_peg < 3.0: _peg_clr, _peg_lbl = _C_NEUTRAL, "Teuer"
                    else:               _peg_clr, _peg_lbl = _C_NEGATIVE, "Sehr teuer"
                    _peg_bar     = min(int(_sp_peg / 5 * 100), 100)
                    _peg_display = f"PEG {_sp_peg:.2f}x"
                    _eg_str      = f" · EPS-Wachstum {_sp_eg:.1f}%" if _sp_eg else ""
                    _src_str     = f"<br>Quelle: {_peg_source}" if _peg_source else ""
                    _peg_note    = (f"PEG = KGV ÷ EPS-Wachstum%. PEG {_sp_peg:.2f}x — {_peg_lbl.lower()} vs. hist. Ø ~1,8x."
                                    f"{_eg_str}.{_src_str}")
                else:
                    if _pe_ref < 15:   _peg_clr, _peg_lbl = _C_POSITIVE, "Günstig"
                    elif _pe_ref < 18: _peg_clr, _peg_lbl = _C_POSITIVE_SFT, "Fair"
                    elif _pe_ref < 23: _peg_clr, _peg_lbl = _C_NEUTRAL, "Leicht teuer"
                    elif _pe_ref < 28: _peg_clr, _peg_lbl = "#ff8f00", "Teuer"
                    else:              _peg_clr, _peg_lbl = _C_NEGATIVE, "Sehr teuer"
                    _peg_bar     = min(int((_pe_ref - 10) / 30 * 100), 100)
                    _peg_display = f"KGV {_pe_ref:.1f}x"
                    _peg_note    = (f"Kein EPS-Wachstum verfügbar — Bewertung via KGV. "
                                    f"Aktuell {_pe_ref:.1f}x, hist. S&amp;P-Schnitt ~15–18x → {_peg_lbl.lower()}.")

                # KGV-Zeile: trailing + forward nebeneinander
                _kgv_sub = ""
                if _sp_trailing_pe:
                    _kgv_sub += f'<span style="color:{_C_TEXT_MUTED};">KGV (trailing) </span><span style="color:{_C_TEXT_MUTED2};font-weight:600;">{_sp_trailing_pe:.1f}x</span>'
                if _sp_forward_pe:
                    _kgv_sub += f'&nbsp;&nbsp;<span style="color:{_C_TEXT_MUTED};">Forward KGV </span><span style="color:{_C_TEXT_MUTED2};font-weight:600;">{_sp_forward_pe:.1f}x</span>'

                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">S&amp;P 500 Bewertung'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">PEG = KGV ÷ EPS-Wachstum% (fair hist. ~1,5–2,0x). Quellen: yfinance forward EPS + multpl.com YoY EPS. Ohne PEG-Daten: Fallback auf trailing KGV (hist. S&amp;P-Schnitt ~15–18x).</span></span></span>'
                    f'<span style="color:{_peg_clr};font-weight:700;">{_peg_display}</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_peg_bar}%;height:5px;border-radius:4px;background:{_peg_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>{"0x" if _sp_peg else "10x"}</span><span style="color:{_peg_clr};">{_peg_lbl}</span><span>{"5x" if _sp_peg else "40x"}</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'{"&lt;1,5x = günstig · 1,5–2,0x = fair · 2–3x = teuer · &gt;3x = sehr teuer · Ø ~1,8x" if _sp_peg else "&lt;15x = günstig · 15–18x = fair · 18–23x = leicht teuer · &gt;28x = sehr teuer"}</div>'
                    + (f'<div style="font-size:0.62rem;margin-top:4px;">{_kgv_sub}</div>' if _kgv_sub else '')
                    + f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>Einordnung:</b> {_peg_note}</div>'
                    f'</div>',
                    unsafe_allow_html=True)

    # ── Erweiterte Bewertungsmodelle ──────────────────────────────────
    _shiller    = macro.get("shiller_cape")
    _erp        = macro.get("erp")
    _tobins_q   = macro.get("tobins_q")
    _mcap_gnp   = macro.get("mcap_gnp")
    _margin_adj = macro.get("margin_adj_pe")
    _active_models = [x for x in [_shiller, _erp, _tobins_q, _mcap_gnp, _margin_adj] if x is not None]

    if _active_models:
        def _norm_score(val, cheap, fair_lo, fair_hi, expensive):
            if val <= cheap:       return 15
            elif val <= fair_lo:   return 35
            elif val <= fair_hi:   return 50
            elif val <= expensive: return 70
            else:                  return 90

        _scores = []
        if _shiller:    _scores.append(_norm_score(_shiller,    15, 22, 28, 38))
        if _tobins_q:   _scores.append(_norm_score(_tobins_q,   2.0, 3.0, 4.5, 6.0))
        if _mcap_gnp:   _scores.append(_norm_score(_mcap_gnp,   75, 90, 115, 140))
        if _bi:         _scores.append(_norm_score(_bi,         75, 90, 115, 140))
        if _margin_adj: _scores.append(_norm_score(_margin_adj, 15, 20, 28, 38))
        if _erp is not None:
            _scores.append(_norm_score(-_erp, -5, -2, 0, 2))

        _mv_score = round(sum(_scores) / len(_scores)) if _scores else 50
        if _mv_score < 30:    _mv_clr, _mv_lbl = _C_POSITIVE, "Unterbewertet"
        elif _mv_score < 45:  _mv_clr, _mv_lbl = _C_POSITIVE_SFT, "Günstig"
        elif _mv_score < 57:  _mv_clr, _mv_lbl = _C_NEUTRAL, "Fair"
        elif _mv_score < 72:  _mv_clr, _mv_lbl = "#ff8f00", "Überbewertet"
        else:                 _mv_clr, _mv_lbl = _C_NEGATIVE, "Stark überbewertet"

        st.markdown(
            '<div style="margin-top:18px;margin-bottom:6px;font-size:0.82rem;'
            'font-weight:600;color:{_C_TEXT_MUTED2};letter-spacing:.04em;">'
            '📐 ERWEITERTE BEWERTUNGSMODELLE</div>',
            unsafe_allow_html=True)

        _col_a, _col_b, _col_c = st.columns(3)

        if _shiller:
            if _shiller < 15:   _sc_clr, _sc_lbl = _C_POSITIVE, "Historisch günstig"
            elif _shiller < 22: _sc_clr, _sc_lbl = _C_POSITIVE_SFT, "Unter Ø"
            elif _shiller < 28: _sc_clr, _sc_lbl = _C_NEUTRAL, "Leicht erhöht"
            elif _shiller < 38: _sc_clr, _sc_lbl = "#ff8f00", "Hoch"
            else:               _sc_clr, _sc_lbl = _C_NEGATIVE, "Extrem hoch"
            _sc_bar = min(int((_shiller - 5) / 50 * 100), 100)
            with _col_a:
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">Shiller CAPE'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">Shiller KGV = S&amp;P 500 Kurs ÷ inflationsbereinigter 10-Jahres-Ø-Gewinn. '
                    f'Campbell &amp; Shiller (1988). Hist. Ø ~17×, Dotcom-Hoch 44×. '
                    f'Starke Prognosekraft für 10–15-j. Realrenditen — kein Timing-Tool.</span></span></span>'
                    f'<span style="color:{_sc_clr};font-weight:700;">{_shiller:.1f}×</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_sc_bar}%;height:5px;border-radius:4px;background:{_sc_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>5×</span><span style="color:{_sc_clr};">{_sc_lbl}</span><span>55×</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;15× = günstig · 15–22× = fair · 22–28× = teuer · &gt;38× = Dotcom-Niveau</div>'
                    f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>Quelle:</b> multpl.com · Hist. Ø ~17×. '
                    f'Erw. 10-j. Realrendite bei {_shiller:.0f}×: '
                    f'{"1–3%" if _shiller > 35 else "3–5%" if _shiller > 28 else "5–7%" if _shiller > 20 else "7–10%"}.</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        if _erp is not None:
            if _erp > 4.0:    _erp_clr, _erp_lbl = _C_POSITIVE, "Sehr attraktiv"
            elif _erp > 2.0:  _erp_clr, _erp_lbl = _C_POSITIVE_SFT, "Attraktiv"
            elif _erp > 0.5:  _erp_clr, _erp_lbl = _C_NEUTRAL, "Neutral"
            elif _erp > -1.0: _erp_clr, _erp_lbl = "#ff8f00", "Teuer vs. Bonds"
            else:             _erp_clr, _erp_lbl = _C_NEGATIVE, "TINA vorbei"
            _erp_bar = min(max(int((_erp + 3) / 9 * 100), 2), 98)
            _fpe_disp = _sp_forward_pe or _sp_trailing_pe or 20
            _t10_disp = macro.get("macro", {}).get("🇺🇸 10J Rendite", {}).get("value", 0)
            with _col_b:
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">Equity Risk Premium'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">ERP = Forward Earnings Yield (1/ForwardKGV×100) − 10J Treasury. '
                    f'Hist. fair ~3–4%. Negatives ERP: Staatsanleihen rentieren besser als Aktien. '
                    f'Einziges Modell das Zinsen direkt einbezieht.</span></span></span>'
                    f'<span style="color:{_erp_clr};font-weight:700;">{_erp:+.2f}%</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_erp_bar}%;height:5px;border-radius:4px;background:{_erp_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>−3%</span><span style="color:{_erp_clr};">{_erp_lbl}</span><span>+6%</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&gt;4% = sehr attraktiv · 2–4% = fair · 0–2% = teuer · &lt;0% = Bonds besser</div>'
                    f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>Rechnung:</b> EY {100/_fpe_disp:.1f}% − 10J {_t10_disp:.1f}% = ERP {_erp:+.2f}%.</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        if _tobins_q:
            if _tobins_q < 2.0:   _tq_clr, _tq_lbl = _C_POSITIVE, "Günstig"
            elif _tobins_q < 3.0: _tq_clr, _tq_lbl = _C_POSITIVE_SFT, "Fair"
            elif _tobins_q < 4.5: _tq_clr, _tq_lbl = _C_NEUTRAL, "Erhöht"
            elif _tobins_q < 6.0: _tq_clr, _tq_lbl = "#ff8f00", "Hoch"
            else:                 _tq_clr, _tq_lbl = _C_NEGATIVE, "Sehr hoch"
            _tq_bar = min(int(_tobins_q / 8 * 100), 100)
            with _col_c:
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">Tobin\'s Q (Proxy)'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">Tobin\'s Q = Marktwert ÷ Wiederbeschaffungskosten. '
                    f'Nobel-Ökonom Tobin (1969): Q&gt;1 → Markt überbewertet Realkapital. '
                    f'Proxy: S&amp;P 500 P/B. Hist. Ø ~2,5–3,0×.</span></span></span>'
                    f'<span style="color:{_tq_clr};font-weight:700;">{_tobins_q:.1f}×</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_tq_bar}%;height:5px;border-radius:4px;background:{_tq_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>1×</span><span style="color:{_tq_clr};">{_tq_lbl}</span><span>8×</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;2× = günstig · 2–3× = fair · 3–4,5× = erhöht · &gt;6× = extrem</div>'
                    f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>Proxy:</b> S&amp;P 500 P/B {_tobins_q:.1f}× (multpl.com). {_tq_lbl}.</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        _col_d, _col_e, _col_f = st.columns(3)

        if _mcap_gnp:
            if _mcap_gnp < 75:    _mg_clr, _mg_lbl = _C_POSITIVE, "Unterbewertet"
            elif _mcap_gnp < 90:  _mg_clr, _mg_lbl = _C_POSITIVE_SFT, "Fair"
            elif _mcap_gnp < 115: _mg_clr, _mg_lbl = _C_NEUTRAL, "Leicht teuer"
            elif _mcap_gnp < 140: _mg_clr, _mg_lbl = "#ff8f00", "Teuer"
            else:                 _mg_clr, _mg_lbl = _C_NEGATIVE, "Stark überbewertet"
            _mg_bar = min(int(_mcap_gnp / 200 * 100), 100)
            with _col_d:
                _bi_str = f'Buffett={str(int(_bi))}% (GDP) · ' if _bi else ""
                _diff_str = f'Diff. {str(int(abs(_mcap_gnp - (_bi or 0))))}pp (Globalisierung).' if _bi else ""
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">Marktk. / GNP'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">Wilshire 5000 ÷ GNP. GNP berücksichtigt Auslandsgewinne — '
                    f'robuster für global tätige S&amp;P-500-Konzerne (~50% int. Umsatz). '
                    f'Buffett-Indikator nutzt GDP. Hist. Ø ~80–100%.</span></span></span>'
                    f'<span style="color:{_mg_clr};font-weight:700;">{_mcap_gnp:.0f}%</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_mg_bar}%;height:5px;border-radius:4px;background:{_mg_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>0%</span><span style="color:{_mg_clr};">{_mg_lbl}</span><span>200%</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;75% = günstig · 75–90% = fair · 90–115% = leicht teuer · &gt;140% = Warnsignal</div>'
                    f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>vs. Buffett:</b> {_bi_str}GNP={_mcap_gnp:.0f}%. {_diff_str}</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        if _margin_adj:
            _ma_base = _sp_trailing_pe or _sp_pe or 0
            _cm = macro.get("corp_margin", 0) or 0
            if _margin_adj < 15:   _ma_clr, _ma_lbl = _C_POSITIVE, "Günstig"
            elif _margin_adj < 20: _ma_clr, _ma_lbl = _C_POSITIVE_SFT, "Fair"
            elif _margin_adj < 28: _ma_clr, _ma_lbl = _C_NEUTRAL, "Erhöht"
            elif _margin_adj < 38: _ma_clr, _ma_lbl = "#ff8f00", "Hoch"
            else:                  _ma_clr, _ma_lbl = _C_NEGATIVE, "Sehr hoch"
            _ma_bar = min(int((_margin_adj - 5) / 50 * 100), 100)
            with _col_e:
                st.markdown(
                    f'<div class="insight-box" style="padding:10px 14px 8px 14px;">'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                    f'<span style="color:{_C_TEXT_SEC};">Margin-adj. KGV'
                    f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                    f'<span class="tt-box">Hussman-Stil: Trailing KGV normalisiert für Gewinnmargen. '
                    f'Wenn Margen über hist. Ø (7,5%) liegen, sind Gewinne "aufgebläht". '
                    f'Formel: KGV × (aktuelle Marge / 7,5%).</span></span></span>'
                    f'<span style="color:{_ma_clr};font-weight:700;">{_margin_adj:.1f}×</span></div>'
                    f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                    f'<div style="width:{_ma_bar}%;height:5px;border-radius:4px;background:{_ma_clr};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                    f'<span>5×</span><span style="color:{_ma_clr};">{_ma_lbl}</span><span>55×</span></div>'
                    f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                    f'&lt;15× = günstig · 15–20× = fair · 20–28× = erhöht · &gt;38× = extrem</div>'
                    f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                    f'<b>Basis:</b> KGV {_ma_base:.1f}× · Marge {_cm:.1f}% (Ø 7,5%) → adj. {_margin_adj:.1f}×. {_ma_lbl}.</div>'
                    f'</div>',
                    unsafe_allow_html=True)

        with _col_f:
            st.markdown(
                f'<div class="insight-box" style="padding:10px 14px 8px 14px;border:1px solid {_mv_clr}30;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:6px;">'
                f'<span style="color:{_C_TEXT_SEC};">Multivariate Composite'
                f'<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                f'<span class="tt-box">Gleichgewichteter Score aller verfügbaren Modelle: '
                f'Shiller CAPE, Tobin\'s Q, Buffett, MarktK./GNP, Margin-adj. KGV, ERP. '
                f'50 = fair · &lt;30 = günstig · &gt;70 = überbewertet. Kein Timing-Tool.</span></span></span>'
                f'<span style="color:{_mv_clr};font-weight:700;">{_mv_lbl}</span></div>'
                f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;margin-bottom:4px;">'
                f'<div style="width:{_mv_score}%;height:5px;border-radius:4px;background:{_mv_clr};"></div></div>'
                f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
                f'<span>0</span><span style="color:{_mv_clr};">Score {_mv_score}</span><span>100</span></div>'
                f'<div style="font-size:0.62rem;color:#37474f;margin-top:4px;">'
                f'&lt;30 = günstig · 30–45 = leicht günstig · 45–57 = fair · 57–72 = teuer · &gt;72 = sehr teuer</div>'
                f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};margin-top:5px;border-top:1px solid #0d2340;padding-top:5px;">'
                f'<b>Modelle:</b> {len(_scores)} von 6 aktiv. Ø-Signal: {_mv_lbl}.</div>'
                f'</div>',
                unsafe_allow_html=True)

    # ── Erweitertes Makro-Dashboard (Expander) ────────────────────────
    try:
        _em = _pf_disk_load("macro_extended", max_age_hours=24)
        if _em is None:
            _em = load_extended_macro()
            _pf_disk_save("macro_extended", _em)
    except Exception:
        _em = {"modules": {}, "regime": {}}

    with st.expander("🔬 Erweitertes Makro-Dashboard — Regime-Analyse", expanded=False):
      try:
        _reg   = _em.get("regime", {})
        _mods  = _em.get("modules", {})
        _rscore= _reg.get("score", 0)
        _rlbl  = _reg.get("label", "Neutral")
        _rclr  = _reg.get("color", _C_NEUTRAL)
        _rmod  = _reg.get("modules", {})

        # ── Regime-Badge ──────────────────────────────────────────────
        _bar_pct = int(min(max((_rscore + 3) / 6 * 100, 2), 98))
        st.markdown(
            f'<div class="insight-box" style="padding:12px 16px 10px;">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
            f'<span style="color:{_C_TEXT_SEC};font-size:0.82rem;font-weight:600;">🧭 Makro-Regime Score</span>'
            f'<span style="color:{_rclr};font-size:1.2rem;font-weight:800;">{_rlbl}</span></div>'
            f'<div style="background:{_C_SURFACE};border-radius:6px;height:8px;margin-bottom:6px;">'
            f'<div style="width:{_bar_pct}%;height:8px;border-radius:6px;background:linear-gradient(90deg,#ff5252,#ffd600,#00e676);"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:0.65rem;color:#37474f;">'
            f'<span>Risk-Off</span><span style="color:{_rclr};font-weight:600;">Score: {_rscore:+.2f}</span><span>Risk-On</span></div>'
            f'<div style="font-size:0.62rem;color:#455a64;margin-top:6px;">'
            f'Composite aus 7 Modulen (z-Score-gewichtet). &gt;0,5 = Risk-On · −0,5–0,5 = Neutral · &lt;−0,5 = Risk-Off</div>'
            f'</div>',
            unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Modul-Scores Übersicht ────────────────────────────────────
        _mod_order = ["Wachstum", "Finanzierung", "Kredit", "Marktbreite", "Inflation", "Liquidität", "Faktoren"]
        _mod_icons = {"Wachstum":"📈", "Finanzierung":"💧", "Kredit":"⚠️",
                      "Marktbreite":"🌐", "Inflation":"🔥", "Liquidität":"💰", "Faktoren":"🔄"}
        _mod_cols = st.columns(len(_mod_order))
        for _ci, _mk in enumerate(_mod_order):
            _ms = _rmod.get(_mk, 0)
            _mc = _C_POSITIVE if _ms > 0.3 else _C_NEGATIVE if _ms < -0.3 else _C_NEUTRAL
            _mod_cols[_ci].markdown(
                f'<div class="metric-card" style="text-align:center;padding:8px 4px;">'
                f'<div style="font-size:0.62rem;color:{_C_TEXT_MUTED};line-height:1.3;">{_mod_icons.get(_mk,"")}<br>{_mk}</div>'
                f'<div style="color:{_mc};font-size:0.9rem;font-weight:700;margin-top:3px;">{_ms:+.1f}</div>'
                f'</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Indikator-Heatmap ─────────────────────────────────────────
        _all_names, _all_z, _all_vals, _all_units = [], [], [], []
        for _mk in _mod_order:
            for _iname, _iv in _mods.get(_mk, {}).items():
                _short = _iname[:22]
                _all_names.append(_short)
                _all_z.append(_iv.get("z", 0))
                _all_vals.append(f"{_iv.get('value',0)}{_iv.get('unit','')}")
                _all_units.append("*" if _iv.get("is_mock") else "")

        if _all_z:
            import plotly.graph_objects as go
            _z_arr = np.array([_all_z])
            _z_clipped = np.clip(_z_arr, -3, 3)
            _text_arr = [[f"{v}{u}" for v, u in zip(_all_vals, _all_units)]]
            _fig_hm = go.Figure(go.Heatmap(
                z=_z_clipped, x=_all_names, y=["Z-Score"],
                text=_text_arr, texttemplate="%{text}",
                colorscale=[[0,_C_NEGATIVE],[0.5,_C_NEUTRAL],[1,_C_POSITIVE]],
                zmin=-3, zmax=3, showscale=True,
                colorbar=dict(title="Z-Score", thickness=10, len=0.8,
                              tickvals=[-3,-1.5,0,1.5,3],
                              ticktext=["−3 (Bär)","−1,5","0","1,5","3 (Bull)"],
                              tickfont=dict(color="#b0bec5", size=9)),
            ))
            _fig_hm.update_layout(
                template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
                plot_bgcolor=_C_CHART_PLOT,
                height=120, margin=dict(l=60, r=20, t=10, b=60),
                xaxis=dict(tickangle=-35, tickfont=dict(size=9, color="#90a4ae")),
                yaxis=dict(tickfont=dict(size=9, color="#546e7a")),
            )
            st.plotly_chart(_fig_hm, use_container_width=True)
            st.markdown('<div style="font-size:0.58rem;color:#37474f;text-align:right;">* Schätzwert (kein kostenfreier Datenfeed)</div>', unsafe_allow_html=True)

        # ── Zeitreihen-Charts in Tabs ─────────────────────────────────
        _chart_tab1, _chart_tab2, _chart_tab3, _chart_tab4 = st.tabs([
            "📉 Zinskurve & Kredit", "💧 Finanzierungsbed.", "🔥 Inflationserwart.", "🔄 Faktor-Regime"
        ])

        def _sparkline(series: pd.Series, title: str, color: str, yunit: str = "",
                       ref_zero: bool = False, height: int = 220):
            if series.empty or len(series) < 5:
                return None
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=series.index, y=series.values,
                mode="lines", line=dict(color=color, width=1.5),
                fill="tozeroy" if ref_zero else "none",
                fillcolor=(color.replace(")", ",0.08)").replace("rgb", "rgba") if color.startswith("rgb")
                           else f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)"),
                name=title,
            ))
            if ref_zero:
                fig.add_hline(y=0, line=dict(color="#37474f", width=1, dash="dot"))
            fig.update_layout(
                template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
                plot_bgcolor=_C_CHART_PLOT, height=height,
                margin=dict(l=0, r=0, t=22, b=0), showlegend=False,
                title=dict(text=title, font=dict(color="#64b5f6", size=11)),
                xaxis=dict(showgrid=False, tickfont=dict(size=8, color="#546e7a")),
                yaxis=dict(showgrid=True, gridcolor="#1e2d45",
                           ticksuffix=yunit, tickfont=dict(size=8, color="#546e7a")),
            )
            return fig

        with _chart_tab1:
            _cc1, _cc2 = st.columns(2)
            with _cc1:
                _s = _mods.get("Wachstum", {}).get("Zinskurve (10J–2J)", {}).get("series", pd.Series(dtype=float))
                _f = _sparkline(_s, "Zinskurve 10J–2J (%)", "#64b5f6", "%", ref_zero=True)
                if _f: st.plotly_chart(_f, use_container_width=True)
                st.markdown('<div style="font-size:0.62rem;color:#455a64;">Inversion (< 0%) = historisch zuverlässiger Rezessionsindikator (Lead: 12–18 Monate).</div>', unsafe_allow_html=True)
            with _cc2:
                _hy = _mods.get("Kredit", {}).get("HY Spread (OAS)", {}).get("series", pd.Series(dtype=float))
                _ig = _mods.get("Kredit", {}).get("IG Spread (OAS)", {}).get("series", pd.Series(dtype=float))
                if not _hy.empty or not _ig.empty:
                    _cf = go.Figure()
                    if not _hy.empty:
                        _cf.add_trace(go.Scatter(x=_hy.index, y=_hy.values, name="HY OAS",
                                                  line=dict(color=_C_NEGATIVE, width=1.5)))
                    if not _ig.empty:
                        _cf.add_trace(go.Scatter(x=_ig.index, y=_ig.values, name="IG OAS",
                                                  line=dict(color=_C_NEUTRAL, width=1.5), yaxis="y2"))
                    _cf.update_layout(
                        template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
                        plot_bgcolor=_C_CHART_PLOT, height=220,
                        margin=dict(l=0, r=40, t=22, b=0),
                        title=dict(text="Kredit-Spreads (bp)", font=dict(color="#64b5f6", size=11)),
                        legend=dict(font=dict(size=8, color="#b0bec5"), bgcolor="rgba(0,0,0,0)"),
                        xaxis=dict(showgrid=False, tickfont=dict(size=8, color="#546e7a")),
                        yaxis=dict(showgrid=True, gridcolor="#1e2d45", ticksuffix="bp",
                                   tickfont=dict(size=8, color=_C_NEGATIVE)),
                        yaxis2=dict(overlaying="y", side="right", ticksuffix="bp",
                                    tickfont=dict(size=8, color=_C_NEUTRAL), showgrid=False),
                    )
                    st.plotly_chart(_cf, use_container_width=True)
                st.markdown('<div style="font-size:0.62rem;color:#455a64;">HY-Spread >600bp = erhöhtes Kreditrisiko. IG-Spreads weiten sich typisch vor HY.</div>', unsafe_allow_html=True)

        with _chart_tab2:
            _dc1, _dc2 = st.columns(2)
            with _dc1:
                _s = _mods.get("Finanzierung", {}).get("Chicago Fed FCI", {}).get("series", pd.Series(dtype=float))
                _f = _sparkline(_s, "Chicago Fed FCI", _C_POSITIVE_SFT, ref_zero=True)
                if _f: st.plotly_chart(_f, use_container_width=True)
                st.markdown('<div style="font-size:0.62rem;color:#455a64;">Negativ = lockere Finanzierungsbedingungen. Positiv = restriktiv (Druck auf Kredit & Aktien).</div>', unsafe_allow_html=True)
            with _dc2:
                _s = _mods.get("Finanzierung", {}).get("10J Realzins (TIPS)", {}).get("series", pd.Series(dtype=float))
                _f = _sparkline(_s, "10J Realzins TIPS (%)", "#ff8f00", "%", ref_zero=True)
                if _f: st.plotly_chart(_f, use_container_width=True)
                st.markdown('<div style="font-size:0.62rem;color:#455a64;">Realzins > 2% = erheblicher Gegenwind für Wachstumsaktien und EM-Assets.</div>', unsafe_allow_html=True)

        with _chart_tab3:
            _ec1, _ec2 = st.columns(2)
            _be5 = _mods.get("Inflation", {}).get("5J Breakeven Inflation", {}).get("series", pd.Series(dtype=float))
            _be10= _mods.get("Inflation", {}).get("10J Breakeven Inflation",{}).get("series", pd.Series(dtype=float))
            with _ec1:
                _f = _sparkline(_be5, "5J Breakeven Inflation (%)", "#ce93d8", "%")
                if _f: st.plotly_chart(_f, use_container_width=True)
            with _ec2:
                _f = _sparkline(_be10, "10J Breakeven Inflation (%)", "#80cbc4", "%")
                if _f: st.plotly_chart(_f, use_container_width=True)
            st.markdown('<div style="font-size:0.62rem;color:#455a64;">Goldilocks-Zone: 2,0–2,5%. Zu hoch = Fed-Druck. Zu niedrig = Deflationsangst. Beide Signale sind bearish.</div>', unsafe_allow_html=True)

        with _chart_tab4:
            _fc1, _fc2, _fc3 = st.columns(3)
            for _col, _mk, _ikey, _clr in [
                (_fc1, "Faktoren", "Growth vs. Value",     "#64b5f6"),
                (_fc2, "Faktoren", "Small vs. Large Cap",  _C_POSITIVE_SFT),
                (_fc3, "Faktoren", "Zyklisch vs. Defensiv",_C_NEUTRAL),
            ]:
                _s = _mods.get(_mk, {}).get(_ikey, {}).get("series", pd.Series(dtype=float))
                if not _s.empty:
                    _s_norm = (_s / _s.iloc[0] * 100)
                    _f = _sparkline(_s_norm, _ikey, _clr, height=200)
                    if _f: _col.plotly_chart(_f, use_container_width=True)
            st.markdown('<div style="font-size:0.62rem;color:#455a64;">Indexiert auf 100 (Startpunkt = Beginn des 2-Jahres-Fensters). Steigt = erste Komponente outperformt.</div>', unsafe_allow_html=True)

        # ── Indikatoren-Detail Tabelle ────────────────────────────────
        st.markdown(f"<div style='color:{_C_TEXT_MUTED};font-size:0.72rem;margin:8px 0 4px 0;'>📋 Alle Indikatoren</div>", unsafe_allow_html=True)
        _rows = []
        for _mk in _mod_order:
            for _iname, _iv in _mods.get(_mk, {}).items():
                _z = _iv.get("z", 0)
                _sig = "🟢 Bullish" if _z > 0.5 else "🔴 Bearish" if _z < -0.5 else "🟡 Neutral"
                _rows.append({
                    "Modul": _mk, "Indikator": _iname,
                    "Wert": f"{_iv.get('value','')}{_iv.get('unit','')}",
                    "Z-Score": f"{_z:+.2f}",
                    "Signal": _sig,
                    "Hinweis": "⚠️ Schätzwert" if _iv.get("is_mock") else "✓ Echtdaten",
                })
        if _rows:
            st.dataframe(pd.DataFrame(_rows), use_container_width=True, hide_index=True)
      except Exception as _ex:
        st.markdown(f'<div style="color:#ff5252;font-size:0.75rem;">Fehler beim Laden des erweiterten Dashboards: {_ex}</div>', unsafe_allow_html=True)

    # ── Sektor-Heatmap + Sentiment ────────────────────────────────────
    _sh_col, _sent_col = st.columns([3, 2])

    with _sh_col:
        if macro.get("sectors"):
            st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin:10px 0 6px 0;'>🗺️ Sektor-Performance (MTD)</div>",
                        unsafe_allow_html=True)
            _secs = macro["sectors"]
            _sorted_secs = sorted(_secs.items(), key=lambda x: x[1], reverse=True)
            _heat_cols = st.columns(len(_sorted_secs))
            for col, (sname, pct) in zip(_heat_cols, _sorted_secs):
                if pct >= 2:
                    bg, clr = "rgba(0,230,118,0.15)", _C_POSITIVE
                elif pct >= 0.5:
                    bg, clr = "rgba(0,230,118,0.07)", _C_POSITIVE_SFT
                elif pct >= -0.5:
                    bg, clr = "rgba(100,181,246,0.08)", "#90a4ae"
                elif pct >= -2:
                    bg, clr = "rgba(255,82,82,0.07)", "#ff8a65"
                else:
                    bg, clr = "rgba(255,82,82,0.15)", _C_NEGATIVE
                arrow = "▲" if pct >= 0 else "▼"
                col.markdown(f"""
                <div style="background:{bg}; border:1px solid {clr}33; border-radius:6px;
                             text-align:center; padding:8px 4px;">
                    <div style="font-size:0.62rem; color:{_C_TEXT_MUTED}; line-height:1.2;">{sname}</div>
                    <div style="color:{clr}; font-size:0.78rem; font-weight:700; margin-top:3px;">
                        {arrow}{abs(pct):.1f}%
                    </div>
                </div>""", unsafe_allow_html=True)

    with _sent_col:
        st.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.75rem; margin:10px 0 6px 0;'>😨 Markt-Sentiment</div>",
                    unsafe_allow_html=True)
        _vix = macro.get("vix")
        _fg  = macro.get("fear_greed", {})

        _has_sentiment = bool(_vix or _fg)

        if _vix:
            _vix_clr = _C_NEGATIVE if _vix > 25 else _C_NEUTRAL if _vix > 18 else _C_POSITIVE
            _vix_lbl = "Hohe Volatilität" if _vix > 25 else "Moderat" if _vix > 18 else "Ruhig"
            _vix_pct = min(int(_vix / 50 * 100), 100)
            st.markdown(
                f'<div class="insight-box" style="padding:10px 14px 6px 14px; margin-bottom:6px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:4px;">'
                f'<span style="color:{_C_TEXT_SEC};">VIX<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                f'<span class="tt-box">CBOE Volatilitätsindex. Misst erwartete S&P-500-Schwankungen (30 Tage). Unter 15 = ruhig · 15–25 = moderat · über 25 = Angst/Unsicherheit.</span></span></span>'
                f'<span style="color:{_vix_clr};font-weight:700;">{_vix}</span></div>'
                f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;">'
                f'<div style="width:{_vix_pct}%;height:5px;border-radius:4px;background:{_vix_clr};"></div></div>'
                f'<div style="font-size:0.68rem;color:{_C_TEXT_MUTED};margin-top:2px;">{_vix_lbl}</div>'
                f'</div>',
                unsafe_allow_html=True)

        if _fg:
            _fs = _fg["score"]
            _fr = _fg.get("rating", "").replace("_", " ").title()
            _fg_clr = _C_NEGATIVE if _fs < 25 else _C_NEUTRAL if _fs < 45 else \
                      "#90a4ae" if _fs < 55 else _C_NEUTRAL if _fs < 75 else _C_POSITIVE
            st.markdown(
                f'<div class="insight-box" style="padding:10px 14px 6px 14px; margin-bottom:6px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:4px;">'
                f'<span style="color:{_C_TEXT_SEC};">Sentiment-Score<span class="tt" tabindex="0"> <span class="tt-icon">ⓘ</span>'
                f'<span class="tt-box">Eigene Berechnung aus: VIX-Level (40%) + SPY 30-Tage-Momentum (35%) + SPY über 200-Tage-MA (25%). Kein CNN-Datenfeed.</span></span></span>'
                f'<span style="color:{_fg_clr};font-weight:700;">{_fs} — {_fr}</span></div>'
                f'<div style="background:{_C_SURFACE};border-radius:4px;height:5px;">'
                f'<div style="width:{_fs}%;height:5px;border-radius:4px;background:{_fg_clr};"></div></div>'
                f'</div>',
                unsafe_allow_html=True)

        if _has_sentiment:
            st.markdown('<div style="font-size:0.65rem;color:#37474f;margin-top:2px;">VIX: CBOE · Sentiment: eigene Berechnung (VIX + SPY-Momentum + 200-MA)</div>',
                        unsafe_allow_html=True)

    # ── KI-Makroanalyse ─────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🌍 KI-Makroanalyse</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:linear-gradient(135deg,#0a1a35 0%,#0d2040 100%);
    border:1px solid #1a3a6c;border-radius:16px;padding:18px 24px 14px 24px;margin-bottom:14px;
    box-shadow:0 4px 32px rgba(0,80,200,0.10);'>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:6px;'>
            <span style='font-size:1.6rem;'>🌍</span>
            <div>
                <div style='font-size:1.1rem;font-weight:700;color:#e3f2fd;'>Makroökonomische Lageanalyse</div>
                <div style='color:{_C_TEXT_MUTED};font-size:0.77rem;margin-top:2px;'>
                    Konjunkturzyklus · Zyklische Branchen · Unternehmensgewinne · Zinsumfeld · Anlageempfehlungen
                </div>
            </div>
        </div>
        <div style='color:#78909c;font-size:0.78rem;border-top:1px solid #1a3a5c;padding-top:8px;margin-top:4px;'>
            Basiert auf Echtzeitdaten (FRED, yFinance) — Fed Rate, EZB, Inflation, VIX, Bewertungsniveaus.
            Ergebnis wird 24 Stunden gespeichert. Kein Anlageberatung.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _maki_pk = "ki_makro_result"
    _maki_mk = "ki_makro_model"
    _maki_ts = "ki_makro_time"

    if _maki_pk not in st.session_state:
        _maki_disk = _pf_disk_load("ki_makro_analysis", max_age_hours=24)
        if _maki_disk and isinstance(_maki_disk, dict):
            st.session_state[_maki_pk] = _maki_disk.get("text", "")
            st.session_state[_maki_mk] = _maki_disk.get("model", "")
            st.session_state[_maki_ts] = _maki_disk.get("time", "")

    _maki_c1, _maki_c2 = st.columns([5, 1])
    with _maki_c1:
        _maki_gen = st.button(
            "🌍 Makro analysieren", type="primary", key="btn_maki_gen",
            disabled=not GEMINI_API_KEY,
            help="Analysiert aktuelle Makrolage auf Basis echter FRED/yFinance-Daten"
        )
    with _maki_c2:
        _maki_regen = st.button(
            "🔄 Neu", key="btn_maki_regen",
            disabled=(_maki_pk not in st.session_state or not GEMINI_API_KEY),
            help="Analyse aktualisieren"
        )
    if not GEMINI_API_KEY:
        st.caption("🔑 GEMINI_API_KEY in Railway-Umgebungsvariablen eintragen.")

    if _maki_gen or _maki_regen:
        _mdat   = macro.get("macro", {})
        _mfed   = _mdat.get("🇺🇸 Fed Rate",        {}).get("value", "n/v")
        _mecb   = _mdat.get("🇪🇺 EZB Rate",         {}).get("value", "n/v")
        _m10y   = _mdat.get("🇺🇸 10J Rendite",      {}).get("value", "n/v")
        _mcpi   = _mdat.get("🇺🇸 Inflation",         {}).get("value", "n/v")
        _mcore  = _mdat.get("🇺🇸 Kerninflation",     {}).get("value", "n/v")
        _mezinf = _mdat.get("🇪🇺 Inflation",         {}).get("value", "n/v")
        _munem  = _mdat.get("🇺🇸 Arbeitslosigkeit",  {}).get("value", "n/v")
        _mjpinf = _mdat.get("🇯🇵 Inflation",         {}).get("value", "n/v")
        _mvix   = macro.get("vix")
        _mfg    = macro.get("fear_greed", {})
        _mfgsco = _mfg.get("score")
        _mfgrat = _mfg.get("rating", "")
        _mspe   = macro.get("sp500_trailing_pe")
        _msfpe  = macro.get("sp500_forward_pe")
        _mspeg  = macro.get("sp500_peg")
        _mseg   = macro.get("sp500_eg")
        _merp   = macro.get("erp")
        _mcape  = macro.get("shiller_cape")
        _mcmarg = macro.get("corp_margin")
        _mbuff  = macro.get("buffett", {})
        _msecs  = macro.get("sectors", {})
        _mreg   = _em.get("regime", {})
        _mrsco  = _mreg.get("score", 0)
        _mrlab  = _mreg.get("label", "Neutral")
        _mmods  = _mreg.get("modules", {})
        _mgdp   = macro.get("gdp", {})
        _mmisery= macro.get("misery", {})
        _myc    = macro.get("yield_curve")
        _mcs    = macro.get("consumer_sentiment")
        _mez_u  = macro.get("ez_unemployment")

        def _mfmt(v, decimals=1, suffix=""):
            return f"{v:.{decimals}f}{suffix}" if v is not None else "n/v"

        _buff_line = ""
        if _mbuff:
            _bv = _mbuff if isinstance(_mbuff, (int, float)) else _mbuff.get("value")
            if _bv:
                _buff_line = f"- Buffett-Indikator (Marktkapitalisierung/BIP): {_bv:.0f}%"

        _secs_line = ""
        if _msecs:
            _sec_sorted = sorted(
                _msecs.items(),
                key=lambda x: (x[1] if isinstance(x[1], (int, float)) else x[1].get("mtd", 0)),
                reverse=True)
            _secs_line = "Sektorperformance (MTD): " + ", ".join(
                f"{s} {(d if isinstance(d, (int, float)) else d.get('mtd', 0)):+.1f}%"
                for s, d in _sec_sorted[:6])

        _mmod_str = " · ".join(f"{k} {v:+.2f}" for k, v in _mmods.items()) if _mmods else "n/v"

        _sys_maki = (
            "Du bist ein erfahrener Kapitalmarktstratege und Finanzwissenschaftler "
            "(20+ Jahre institutionelles Portfolio-Management, Makro-Research, Asset Allocation). "
            "Du kombinierst volkswirtschaftliche Theorie präzise mit pragmatischer Marktanalyse. "
            "Erkenne Zyklen früh, leite konkrete Anlageimplikationen ab. "
            "Antworte ausschließlich auf Deutsch. Sei direkt, konkret und ehrlich — "
            "keine vagen Formulierungen, keine Marketing-Sprache."
        )

        _usr_maki = f"""Analysiere die aktuelle makroökonomische Lage anhand dieser aktuellen Datenpunkte:

**GELDPOLITIK & ZINSEN:**
- Fed Funds Rate: {_mfmt(_mfed)}%
- EZB Einlagesatz: {_mfmt(_mecb)}%
- US 10J Staatsanleihe: {_mfmt(_m10y)}%
- Equity Risk Premium (ERP): {_mfmt(_merp)}%

**INFLATION:**
- US CPI (YoY): {_mfmt(_mcpi)}%  |  US Kernrate: {_mfmt(_mcore)}%
- Eurozone HICP (YoY): {_mfmt(_mezinf)}%  |  Japan CPI: {_mfmt(_mjpinf)}%

**BIP-WACHSTUM (YoY, aktuellstes Quartal):**
{chr(10).join(f"- {k}: {v:+.1f}%" for k, v in _mgdp.items()) if _mgdp else "- Daten nicht verfügbar"}

**KONJUNKTUR & ARBEIT:**
- US Arbeitslosenquote: {_mfmt(_munem)}%  |  EZ Arbeitslosenquote: {_mfmt(_mez_u)}%
- US Misery Index: {_mfmt(_mmisery.get("🇺🇸 USA"))}%  |  EZ Misery Index: {_mfmt(_mmisery.get("🇪🇺 Eurozone"))}%
- Zinskurve USA (10J-2J): {_mfmt(_myc, 2)}% {"⚠️ Invertiert" if _myc is not None and _myc < 0 else ""}
- Michigan Consumer Sentiment: {_mfmt(_mcs, 0)}
- Unternehmensgewinnmarge (S&P 500, % des BIP): {_mfmt(_mcmarg)}%
{_buff_line}

**AKTIENMARKT-BEWERTUNG:**
- S&P 500 Trailing KGV: {_mfmt(_mspe)}x  |  Forward KGV: {_mfmt(_msfpe)}x
- Shiller CAPE: {_mfmt(_mcape)}x  |  PEG-Ratio: {_mfmt(_mspeg)}
- Erwartetes Gewinnwachstum (S&P 500): {_mfmt(_mseg)}%

**MARKTSENTIMENT:**
- VIX (Volatilität): {_mfmt(_mvix)}
- Fear & Greed Score: {_mfmt(_mfgsco, 0)} — {_mfgrat}
- {_secs_line}

**MAKRO-REGIME (z-Score-gewichtet, eigene Berechnungen):**
- Regime: {_mrlab} (Composite-Score: {_mrsco:+.2f})
- Module: {_mmod_str}

---

Erstelle eine strukturierte finanzwirtschaftliche Analyse in genau diesem Format:

## 🔄 Konjunkturzyklusposition
Wo stehen wir präzise im Wirtschaftszyklus (Früh-/Mittzyklus, Late-Cycle, Kontraktion)? Welche Datenpunkte belegen das? Rezessionswahrscheinlichkeit einschätzen.

## 🏭 Zyklische Branchen — Wo stehen wir?
Welche Sektoren profitieren, welche leiden in der aktuellen Zyklusphase? Mindestens 4 Sektoren konkret analysieren (zyklisch vs. defensiv, Konsumgüter, Industrie, Finanzwerte, Technologie, Energie, Immobilien/REITs, Rohstoffe). Klare Über-/Untergewichtungsempfehlung.

## 📊 Unternehmensgewinnentwicklung
Wie entwickeln sich Unternehmensgewinne aktuell? Margendruck oder -expansion? EPS-Momentum, Revisions-Trend, Bewertungsimplikationen aus den vorliegenden KGV/CAPE-Daten. Welche Sektoren haben Rückenwind bei Gewinnen?

## 💰 Zinsumfeld & Kapitalmarktimplikationen
Interpretation der aktuellen Zinslage: Real vs. nominale Renditen, Zinskurvenform, Zentralbankpfad. Konkrete Implikationen: Welche Assetklassen leiden, welche profitieren? Bonds als Alternative zu Aktien?

## 🎯 Anlageempfehlungen (Finanzwissenschaftliche Einschätzung)
Konkrete Asset-Allocation-Empfehlung: Was über-/untergewichten und warum? Unterscheide nach Zeithorizont (6 Monate taktisch vs. 3–5 Jahre strategisch). Besonderes Augenmerk auf Risiko/Rendite-Verhältnis im aktuellen Umfeld."""

        with st.spinner("🌍 KI analysiert Konjunktur, Sektoren und Zinsen…"):
            _maki_txt, _maki_mdl = call_ki_api(
                _sys_maki, _usr_maki, GEMINI_API_KEY, max_tokens=8000
            )
        if _maki_txt and not _maki_txt.startswith("⚠️"):
            import datetime as _maki_dt
            _maki_now = _maki_dt.datetime.now().strftime("%d.%m.%Y %H:%M")
            st.session_state[_maki_pk] = _maki_txt
            st.session_state[_maki_mk] = _maki_mdl
            st.session_state[_maki_ts] = _maki_now
            _pf_disk_save("ki_makro_analysis", {
                "text": _maki_txt, "model": _maki_mdl, "time": _maki_now
            })
            st.rerun()
        else:
            st.error(f"KI-Analyse fehlgeschlagen: {_maki_mdl or _maki_txt}")

    if _maki_pk in st.session_state and st.session_state.get(_maki_pk):
        _maki_result = st.session_state[_maki_pk]
        _maki_model  = st.session_state.get(_maki_mk, "Gemini")
        _maki_time   = st.session_state.get(_maki_ts, "")
        with st.expander("📊 Makroanalyse lesen", expanded=True):
            if _maki_time:
                st.caption(f"Stand: {_maki_time} · {_maki_model} · Gültig 24h")
            st.markdown(_maki_result)

    # ── Marktschlagzeilen ────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📰 Aktuelle Marktschlagzeilen</div>", unsafe_allow_html=True)
    with st.spinner("Lade Nachrichten…"):
        headlines = load_market_news()

    if headlines:
        for h in headlines:
            src = f"<span style='color:{_C_TEXT_MUTED}; font-size:0.72rem; margin-left:8px;'>{h['source']}</span>" if h['source'] else ""
            st.markdown(f"""
            <div class="metric-card" style="padding:14px 18px;">
                <div style="color:{_C_TEXT_PRIMARY}; font-size:0.92rem; line-height:1.4;">📌 {h['title']}{src}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="metric-card" style="color:{_C_TEXT_MUTED}; text-align:center;">Keine Nachrichten verfügbar</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.stop()

# ==================== AKTIENIDEEN PAGE ====================
elif st.session_state.get("show_stocks"):
    st.markdown("<div class='section-header'>💡 Aktienideen & Screener</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Aktienempfehlungen Accordion ──
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    with st.expander("💡  Aktienideen — Growth · Value · Dividende · Overhyped  (täglich aktualisiert)", expanded=True):
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
            bar_clr = accent if pos > 62 else _C_NEUTRAL if pos > 35 else _C_NEGATIVE
            return (f"<div style='margin-top:7px;'>"
                    f"<div style='display:flex;justify-content:space-between;"
                    f"font-size:0.63rem;color:{_C_TEXT_MUTED};margin-bottom:2px;'>"
                    f"<span>52W-Tief</span><span style='color:{_C_TEXT_MUTED};'>{pos:.0f}%</span>"
                    f"<span>52W-Hoch</span></div>"
                    f"<div style='background:{_C_BORDER};border-radius:4px;height:4px;'>"
                    f"<div style='background:{bar_clr};width:{pos}%;height:4px;"
                    f"border-radius:4px;transition:width 0.4s;'></div></div></div>")

        def _pick_card(s, accent, badges_html, extra_html=""):
            price_str = f"${s['price']:,.2f}" if s['price'] else "—"
            return f"""
            <div style='background:{_C_CARD_BG};
                 border:1px solid {_C_BORDER};border-left:3px solid {accent};
                 border-radius:12px;padding:13px 15px;margin-bottom:10px;'>
              <div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px;'>
                <span style='color:{accent};font-size:1.02rem;font-weight:800;
                      letter-spacing:0.5px;'>{s["ticker"]}</span>
                <span style='color:{_C_TEXT_SEC};font-size:0.82rem;font-weight:600;'>{price_str}</span>
              </div>
              <div style='color:{_C_TEXT_MUTED};font-size:0.72rem;margin-bottom:5px;'>{s["name"]}</div>
              <div style='color:{_C_TEXT_MUTED2};font-size:0.78rem;line-height:1.45;margin-bottom:8px;'>{s["desc"]}</div>
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
                b = (_badge("Rev▲", s["rev_growth"], "%", ".0f", _C_POSITIVE) +
                     _badge("EPS▲", s["eps_growth"], "%", ".0f", _C_POSITIVE_SFT) +
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
                b = (_badge("KUV", s["ps_ratio"], "x", ".1f", _C_NEGATIVE) +
                     _badge("KGV", s["pe_ratio"] if s["pe_ratio"] and s["pe_ratio"] < 999 else None, "x", ".0f", "#ff7043") +
                     _badge("Short", s["short_float"] if s["short_float"] > 2 else None, "%", ".0f", _C_NEUTRAL))
                if s["analyst_up"] is not None and s["analyst_up"] < 0:
                    b += _badge("Upside", s["analyst_up"], "%", ".0f", "#ef9a9a")
                st.markdown(_pick_card(s, _C_NEGATIVE, b, warn_html), unsafe_allow_html=True)

        st.markdown(
            "<div style='color:#37474f;font-size:0.68rem;text-align:center;margin-top:4px;'>"
            "⚠️ Keine Anlageberatung · Daten via Yahoo Finance · Aktualisierung alle 12 Std.</div>",
            unsafe_allow_html=True)

    # ── Mid- & Small-Cap Ideen ─────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    with st.expander("🏗️  Mid- & Small-Cap Ideen — Nischenführer mit Qualitätsfilter  (12h Cache)", expanded=False):
        st.markdown(
            f"<div style='color:{_C_TEXT_MUTED};font-size:0.75rem;margin-bottom:14px;line-height:1.6;'>"
            "Nur Titel mit <b>positivem FCF</b>, <b>Bruttomarge &gt; 35 %</b> (Mid) / <b>&gt; 40 %</b> (Small), "
            "<b>Umsatzwachstum &gt; 8 %</b> und <b>vernünftiger Verschuldung</b> werden angezeigt. "
            "Small-Caps zusätzlich: positiver EPS Pflicht. Fällt ein Titel durch den Filter, erscheint er nicht.</div>",
            unsafe_allow_html=True)
        with st.spinner("Lade Mid- & Small-Cap-Daten…"):
            _mp, _sp = load_small_mid_picks()

        def _mc_badge(label, value, suffix="", fmt=".0f", color="#64b5f6"):
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

        def _mc_card(s, accent, badges_html):
            price_str = f"${s['price']:,.2f}" if s['price'] else "—"
            cap_bn    = s["mktcap"] / 1e9
            cap_str   = f"{cap_bn:.1f} Mrd."
            return f"""
            <div style='background:{_C_CARD_BG};
                 border:1px solid {_C_BORDER};border-left:3px solid {accent};
                 border-radius:12px 12px 0 0;padding:13px 15px 10px 15px;margin-bottom:0;'>
              <div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px;'>
                <span style='color:{accent};font-size:1.02rem;font-weight:800;
                      letter-spacing:0.5px;'>{s["ticker"]}</span>
                <span style='color:{_C_TEXT_MUTED};font-size:0.74rem;'>{cap_str}</span>
              </div>
              <div style='color:{_C_TEXT_MUTED};font-size:0.72rem;margin-bottom:5px;'>{s["name"]}</div>
              <div style='color:{_C_TEXT_MUTED2};font-size:0.78rem;line-height:1.45;margin-bottom:8px;'>{s["desc"]}</div>
              <div style='line-height:2;'>{badges_html}</div>
              {_trend_bar(s["w52_pos"], accent)}
            </div>"""

        _col_mid, _col_sml = st.columns(2)

        with _col_mid:
            st.markdown(
                "<div style='color:#34d399;font-size:0.82rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;"
                "padding-bottom:7px;border-bottom:1px solid rgba(52,211,153,0.25);'>"
                "🏗️ Mid-Cap Qualität</div>",
                unsafe_allow_html=True)
            if not _mp:
                st.info("Aktuell keine Mid-Caps, die alle Qualitätshürden erfüllen.")
            for s in _mp:
                # PEG badge: grün < 1.5, gelb 1.5–2.5, rot > 2.5
                _peg = s.get("peg")
                _pfcf = s.get("pfcf")
                if _peg is not None:
                    _peg_clr = "#69f0ae" if _peg < 1.5 else _C_NEUTRAL if _peg < 2.5 else _C_NEGATIVE
                    _val_badge = _mc_badge("PEG", _peg, "", ".2f", _peg_clr)
                elif _pfcf is not None:
                    _pfc_clr = "#69f0ae" if _pfcf < 20 else _C_NEUTRAL if _pfcf < 35 else _C_NEGATIVE
                    _val_badge = _mc_badge("P/FCF", _pfcf, "x", ".0f", _pfc_clr)
                else:
                    _val_badge = ""
                b = (_mc_badge("Rev▲", s["rev_growth"], "%", ".0f", _C_POSITIVE) +
                     _mc_badge("GM", s["gross_margin"], "%", ".0f", "#34d399") +
                     _mc_badge("FCF", s["fcf_yield"], "%", ".1f", "#40c4ff") +
                     _mc_badge("ROE", s["roe"] if s["roe"] > 0 else None, "%", ".0f", "#a5d6a7") +
                     _val_badge)
                st.markdown(_mc_card(s, "#34d399", b), unsafe_allow_html=True)
                if st.button(f"🔍 {s['ticker']} analysieren",
                             key=f"mc_go_{s['ticker']}", use_container_width=True):
                    _go_to_ticker(s["ticker"])
                    st.rerun()
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with _col_sml:
            st.markdown(
                "<div style='color:#fb923c;font-size:0.82rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px;"
                "padding-bottom:7px;border-bottom:1px solid rgba(251,146,60,0.25);'>"
                "🔬 Small-Cap Nischen</div>",
                unsafe_allow_html=True)
            if not _sp:
                st.info("Aktuell keine Small-Caps, die alle Qualitätshürden erfüllen.")
            for s in _sp:
                _peg = s.get("peg")
                _pfcf = s.get("pfcf")
                if _peg is not None:
                    _peg_clr = "#69f0ae" if _peg < 1.5 else _C_NEUTRAL if _peg < 2.5 else _C_NEGATIVE
                    _val_badge = _mc_badge("PEG", _peg, "", ".2f", _peg_clr)
                elif _pfcf is not None:
                    _pfc_clr = "#69f0ae" if _pfcf < 20 else _C_NEUTRAL if _pfcf < 35 else _C_NEGATIVE
                    _val_badge = _mc_badge("P/FCF", _pfcf, "x", ".0f", _pfc_clr)
                else:
                    _val_badge = ""
                b = (_mc_badge("Rev▲", s["rev_growth"], "%", ".0f", _C_POSITIVE) +
                     _mc_badge("GM", s["gross_margin"], "%", ".0f", "#fb923c") +
                     _mc_badge("FCF", s["fcf_yield"], "%", ".1f", "#fbbf24") +
                     _val_badge)
                st.markdown(_mc_card(s, "#fb923c", b), unsafe_allow_html=True)
                if st.button(f"🔍 {s['ticker']} analysieren",
                             key=f"sc_go_{s['ticker']}", use_container_width=True):
                    _go_to_ticker(s["ticker"])
                    st.rerun()
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown(
            "<div style='color:#37474f;font-size:0.68rem;text-align:center;margin-top:4px;'>"
            "⚠️ Keine Anlageberatung · Mid/Small-Caps = höheres Risiko · Daten via Yahoo Finance</div>",
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
                "<div style='color:{_C_TEXT_MUTED};font-size:0.75rem;margin-bottom:8px;'>"
                f"<b>{len(_sc_picks)} Treffer</b> · Score ≥ 65 · Kurs ≥ 8 % unter geschätztem Fair Value · "
                "Sortiert nach Score × Discount</div>",
                unsafe_allow_html=True)
            for _sp in _sc_picks:
                _sp_cur  = _sp["currency"]
                _sp_disc = _sp["discount"]
                _sp_disc_clr = _C_POSITIVE if _sp_disc >= 15 else _C_NEUTRAL if _sp_disc >= 10 else "#90a4ae"
                _sp_score_clr = _C_POSITIVE if _sp["score"] >= 80 else _C_NEUTRAL if _sp["score"] >= 70 else "#90a4ae"
                st.markdown(f"""
                <div class="metric-card" style="padding:10px 14px;margin-bottom:8px;">
                  <div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:3px;">
                    <span style="color:{_C_TEXT_PRIMARY};font-size:0.95rem;font-weight:700;">{_sp['ticker']}</span>
                    <span style="color:{_sp_score_clr};font-size:0.82rem;font-weight:700;">Score {_sp['score']}</span>
                  </div>
                  <div style="display:flex;align-items:baseline;justify-content:space-between;">
                    <span style="color:{_C_TEXT_MUTED};font-size:0.72rem;">{_sp.get('sector','')}</span>
                    <span style="font-size:0.78rem;white-space:nowrap;">
                      <span style="color:{_C_TEXT_SEC};">{_sp['price']:.2f} {_sp_cur}</span>
                      <span style="color:{_C_TEXT_MUTED};margin:0 4px;">→ FV</span>
                      <span style="color:{_C_ACCENT};">{_sp['fv']:.2f}</span>
                      <span style="color:{_sp_disc_clr};font-weight:700;margin-left:6px;">-{_sp_disc:.1f}%</span>
                    </span>
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
                            f"<span style='color:{_C_ACCENT};font-size:0.95rem;font-weight:800;"
                            f"letter-spacing:0.4px;'>{_tk}</span>"
                            f"<span style='color:{_C_TEXT_MUTED};font-size:0.7rem;'>{_nm}</span>"
                            f"</div>"
                            f"<div style='color:#78909c;font-size:0.73rem;line-height:1.4;'>{_ds}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        if st.button(f"→ {_tk} analysieren", key=f"sec_{_sec_name}_{_tk}",
                                     use_container_width=True):
                            _go_to_ticker(_tk)
                            st.rerun()

    # ── Quality Top-Picks (Score ≥ 70, täglich aktualisiert) ──────────
    with st.expander("⭐ Quality Top-Picks — Score ≥ 70 (täglich aktualisiert)", expanded=False):
        with st.spinner("Berechne Quality-Scores…"):
            _qtp = load_quality_highscore()
        if _qtp:
            st.markdown(
                f"<div style='font-size:0.78rem;color:{_C_TEXT_MUTED2};margin-bottom:10px;'>"
                f"{len(_qtp)} Aktien mit Score ≥ 70 — sortiert nach Quality-Score</div>",
                unsafe_allow_html=True)
            for _q in _qtp:
                _sc_clr = _C_POSITIVE if _q["score"] >= 90 else _C_POSITIVE_SFT if _q["score"] >= 85 else _C_NEUTRAL if _q["score"] >= 80 else "#ffa726"
                st.markdown(
                    f'<div class="metric-card" style="padding:10px 14px;margin-bottom:6px;cursor:pointer;">'
                    f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                    f'<div>'
                    f'<span style="font-weight:700;color:{_C_TEXT_PRIMARY};">{_q["ticker"]}</span>'
                    f'<span style="color:{_C_TEXT_MUTED};font-size:0.78rem;margin-left:8px;">{_q["name"]}</span>'
                    f'</div>'
                    f'<span style="color:{_sc_clr};font-weight:700;font-size:1.0rem;">Score {_q["score"]}</span>'
                    f'</div>'
                    f'<div style="margin-top:5px;font-size:0.72rem;">'
                    f'<span style="color:{_C_TEXT_MUTED};">Rev-Wachstum </span><span style="color:{_C_TEXT_MUTED2};">{_q["rev_growth"]:+.1f}%</span>'
                    f'&nbsp;&nbsp;<span style="color:{_C_TEXT_MUTED};">Brutto-Marge </span><span style="color:{_C_TEXT_MUTED2};">{_q["gross_margin"]:.1f}%</span>'
                    f'&nbsp;&nbsp;<span style="color:{_C_TEXT_MUTED};">FCF Yield </span><span style="color:{_C_TEXT_MUTED2};">{_q["fcf_yield"]:.1f}%</span>'
                    f'&nbsp;&nbsp;<span style="color:{_C_TEXT_MUTED};">ROE </span><span style="color:{_C_TEXT_MUTED2};">{_q["roe"]:.1f}%</span>'
                    f'</div></div>',
                    unsafe_allow_html=True)
                if st.button(f"Analysieren → {_q['ticker']}", key=f"qtp_{_q['ticker']}", use_container_width=False):
                    _go_to_ticker(_q["ticker"])
                    st.rerun()
        else:
            st.info("Keine Qualitäts-Picks gefunden — Daten werden geladen. Bitte kurz warten.")

    # ── Daytrading Kandidaten (ATR + Volumen, stündlich aktualisiert) ───
    with st.expander("⚡ Daytrading Kandidaten — ATR & Volumen (stündlich)", expanded=False):
        with st.spinner("Lade Daytrading-Daten…"):
            _dtp = load_daytrading_picks()
        if _dtp:
            st.markdown(
                "<div style='font-size:0.78rem;color:{_C_TEXT_MUTED2};margin-bottom:10px;'>"
                "Sortiert nach ATR% × 0,6 + Rel. Volumen × 0,4 — hohe Beweglichkeit priorisiert</div>",
                unsafe_allow_html=True)
            for _d in _dtp:
                _typ_clr = "#ff8f00" if _d["typ"] == "Leveraged ETF" else "#64b5f6" if _d["typ"] == "ETF" else "#a5d6a7"
                _vol_clr = _C_POSITIVE if _d["rel_vol"] > 1.5 else _C_NEUTRAL if _d["rel_vol"] > 0.8 else _C_NEGATIVE
                st.markdown(
                    f'<div class="metric-card" style="padding:10px 14px;margin-bottom:6px;">'
                    f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                    f'<div>'
                    f'<span style="font-weight:700;color:{_C_TEXT_PRIMARY};">{_d["ticker"]}</span>'
                    f'<span style="color:{_C_TEXT_MUTED};font-size:0.76rem;margin-left:8px;">{_d["name"]}</span>'
                    f'<span style="background:rgba(0,0,0,0.3);color:{_typ_clr};border-radius:3px;'
                    f'padding:1px 5px;font-size:0.65rem;margin-left:6px;">{_d["typ"]}</span>'
                    f'</div>'
                    f'<span style="color:{_C_TEXT_MUTED2};font-weight:600;">${_d["price"]:.2f}</span>'
                    f'</div>'
                    f'<div style="margin-top:5px;font-size:0.72rem;">'
                    f'<span style="color:{_C_TEXT_MUTED};">ATR% </span><span style="color:#ff8f00;font-weight:600;">{_d["atr_pct"]:.1f}%</span>'
                    f'&nbsp;&nbsp;<span style="color:{_C_TEXT_MUTED};">Rel. Vol </span><span style="color:{_vol_clr};font-weight:600;">{_d["rel_vol"]:.2f}×</span>'
                    f'&nbsp;&nbsp;<span style="color:{_C_TEXT_MUTED};">Score </span><span style="color:{_C_TEXT_MUTED2};">{_d["score"]:.1f}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True)
                if st.button(f"Chart → {_d['ticker']}", key=f"dtp_{_d['ticker']}", use_container_width=False):
                    _go_to_ticker(_d["ticker"])
                    st.rerun()
        else:
            st.info("Daytrading-Daten werden geladen…")

    # ── KI-Investmentstrategie ─────────────────────────────────────────────────
    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:{_C_CARD_BG};
    border:1px solid {_C_BORDER};border-left:4px solid {_C_ACCENT};border-radius:16px;
    padding:22px 26px 16px 26px;margin-bottom:16px;
    box-shadow:0 4px 20px rgba(0,80,200,0.08);'>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px;'>
            <span style='font-size:1.8rem;'>🤖</span>
            <div>
                <div style='font-size:1.15rem;font-weight:700;color:{_C_TEXT_PRIMARY};'>KI-Investmentstrategie</div>
                <div style='color:{_C_ACCENT};font-size:0.78rem;margin-top:2px;'>
                    Als professioneller Langfristinvestor — Burggraben · Wachstum · Bewertung · Zukunft
                </div>
            </div>
        </div>
        <div style='color:{_C_TEXT_MUTED};font-size:0.8rem;border-top:1px solid {_C_BORDER};padding-top:10px;margin-top:4px;'>
            Die KI wählt Aktien, die den breiten Markt (MSCI World) langfristig übertreffen sollen —
            basierend auf dauerhaften Wettbewerbsvorteilen, Wachstumspotenzial und fairer Bewertung.
            Kein Anlageberatung.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _ki_pk  = "ki_landing_picks"
    _ki_mk  = "ki_landing_model"
    _ki_ts  = "ki_landing_ts"

    _kc1, _kc2 = st.columns([5, 1])
    with _kc1:
        _ki_gen = st.button("🤖 KI-Aktienauswahl generieren", type="primary",
                            use_container_width=True, key="btn_ki_gen",
                            disabled=not GEMINI_API_KEY)
    with _kc2:
        _ki_ref = st.button("🔄 Neu", use_container_width=True, key="btn_ki_ref",
                            disabled=(_ki_pk not in st.session_state or not GEMINI_API_KEY))

    if not GEMINI_API_KEY:
        st.caption("🔑 GEMINI_API_KEY in Railway-Umgebungsvariablen eintragen.")

    if _ki_ref:
        for _k in [_ki_pk, _ki_mk, _ki_ts]:
            st.session_state.pop(_k, None)
        st.rerun()

    if _ki_gen and _ki_pk not in st.session_state:
        _sys_ki = (
            "Du bist ein erfahrener institutioneller Investor mit der Philosophie von "
            "Warren Buffett, Charlie Munger und dem Konzept des 'Quality Investing'. "
            "Du analysierst Aktien nach: dauerhaftem Burggraben (Wettbewerbsvorteil), "
            "Wachstumspotenzial über 5–10 Jahre, fundamentaler Qualität (hohe Eigenkapitalrendite, "
            "starker Free Cashflow, solide Bilanz) sowie fairer Bewertung. "
            "Dein Ziel: Aktien identifizieren, die den MSCI World Index langfristig "
            "signifikant outperformen können. Antworte ausschließlich auf Deutsch. "
            "Sei konkret, fundiert und ehrlich — keine Marketing-Sprache."
        )
        _usr_ki = (
            "Wähle genau 7 Aktien aus, in die du als professioneller institutioneller Investor "
            "heute langfristig investieren würdest. Misch Wachstums- und Quality-Value-Titel. "
            "Mindestens 2 europäische oder asiatische Titel (nicht nur US-Mega-Caps). "
            "Begründe jede Wahl strukturiert.\n\n"
            "Für jede Aktie exakt dieses Format:\n\n"
            "**[Nr]. [TICKER] – [FIRMENNAME]**\n"
            "*[SEKTOR] · [Wachstum / Quality-Value / Dividende+Wachstum]*\n\n"
            "🏰 **Burggraben:** [Konkreter, dauerhafter Wettbewerbsvorteil — warum verliert "
            "das Unternehmen keine Kunden?]\n"
            "📈 **Wachstumskatalysator:** [Was treibt das Wachstum die nächsten 10 Jahre? "
            "TAM, Marktanteil, neue Märkte?]\n"
            "💰 **Bewertung:** [Ist die Aktie fair/günstig/teuer? Kurze KGV- oder "
            "Cashflow-Einschätzung]\n"
            "⚠️ **Hauptrisiko:** [Das wichtigste Risiko in einem Satz]\n\n"
            "---\n\n"
            "Wiederhole dieses Format für alle 7 Aktien, getrennt durch '---'.\n\n"
            "Schreibe abschließend:\n"
            "**Strategie & Portfolio-Logik:** [Warum ergänzen sich diese 7 Aktien? Wie "
            "soll diese Kombination den Markt langfristig schlagen?]"
        )
        with st.spinner("🤖 KI analysiert globale Märkte und Fundamentaldaten…"):
            _ki_txt, _ki_mdl = _try_gemini(
                [{"role": "system", "content": _sys_ki},
                 {"role": "user",   "content": _usr_ki}],
                max_tokens=8000, temperature=0.65, api_key=GEMINI_API_KEY
            )
        if _ki_txt:
            import datetime as _kidt
            st.session_state[_ki_pk] = _ki_txt
            st.session_state[_ki_mk] = _ki_mdl
            st.session_state[_ki_ts] = _kidt.datetime.now().strftime("%d.%m.%Y %H:%M")
            st.rerun()
        else:
            st.error(f"KI-Analyse fehlgeschlagen: {_ki_mdl}")

    if _ki_pk in st.session_state:
        _ki_result = st.session_state[_ki_pk]
        _ki_model  = st.session_state.get(_ki_mk, "Gemini")
        _ki_time   = st.session_state.get(_ki_ts, "")

        # Parse blocks separated by ---
        import re as _kire
        _ki_blocks = [b.strip() for b in _ki_result.split("---") if b.strip()]

        for _kb in _ki_blocks:
            # Extract ticker for the "Analysieren" button (matches **1. NVDA –)
            _kb_tkr = None
            _m = _kire.search(r'\*\*\d+\.\s+([A-Z0-9]{1,6})\s*[–\-—]', _kb)
            if _m:
                _kb_tkr = _m.group(1)

            # Style the card
            _border = "#1565c0" if _kb_tkr else "#1a3a5c"
            st.markdown(
                f"<div style='background:#080f1e;border:1px solid {_border}33;"
                f"border-left:3px solid {_border};border-radius:10px;"
                f"padding:16px 20px 12px 20px;margin-bottom:10px;'>",
                unsafe_allow_html=True)
            st.markdown(_kb)
            if _kb_tkr:
                if st.button(f"📊 {_kb_tkr} analysieren →",
                             key=f"ki_goto_{_kb_tkr}", use_container_width=False):
                    _go_to_ticker(_kb_tkr)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.caption(f"Modell: {_ki_model} · Generiert: {_ki_time} · "
                   f"Keine Anlageberatung — eigene Recherche empfohlen.")

    st.stop()

# ==================== PORTFOLIO PAGE ====================
if st.session_state.get("show_portfolio"):
    # ── Passwortschutz ────────────────────────────────────────────────────
    if PORTFOLIO_PASSWORD and not st.session_state.get("portfolio_unlocked"):
        st.markdown("""
        <div style="text-align:center; padding:48px 0 24px 0;">
            <div style="font-size:2rem; font-weight:800; color:#fff;">🔒 Portfolio</div>
            <div style="color:{_C_ACCENT}; font-size:0.95rem; margin-top:8px;">
                Bitte Passwort eingeben
            </div>
        </div>
        """, unsafe_allow_html=True)
        _pw_col = st.columns([1, 2, 1])[1]
        with _pw_col:
            _pw_input = st.text_input("Passwort", type="password",
                                      label_visibility="collapsed",
                                      placeholder="Passwort eingeben…")
            if st.button("Entsperren", use_container_width=True, type="primary"):
                if _pw_input == PORTFOLIO_PASSWORD:
                    st.session_state["portfolio_unlocked"] = True
                    st.rerun()
                else:
                    st.error("Falsches Passwort.")
        st.stop()

    st.markdown("""
    <div style="text-align:center; padding:32px 0 20px 0;">
        <div style="font-size:2.4rem; font-weight:800; color:#fff;">📁 Mein Portfolio</div>
        <div style="color:{_C_ACCENT}; font-size:1rem; margin-top:8px;">
            Finanzen.net Zero Orderhistorie hochladen → alle Positionen werden automatisch berechnet
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Supabase auto-load (einmal pro Session) ─────────────────────────────
    if not st.session_state.get("portfolio_sb_checked"):
        st.session_state["portfolio_sb_checked"] = True
        if st.session_state.get("portfolio_csv_bytes") is None:
            _sb_raw, _sb_date = _sb_load_portfolio()
            if _sb_raw:
                st.session_state["portfolio_csv_bytes"] = _sb_raw
                st.session_state["portfolio_sb_date"] = _sb_date
                with st.spinner("Gespeichertes Portfolio wird geladen…"):
                    _auto_df = _parse_portfolio_csv(_sb_raw)
                if not _auto_df.empty:
                    st.session_state["portfolio_df"] = _auto_df.copy()
                    _auto_tradeable = _auto_df[
                        ~_auto_df['is_crypto'] & ~_auto_df['is_warrant']
                    ]['ISIN'].tolist()
                    if _auto_tradeable:
                        _auto_wkn_map = dict(zip(_auto_df['ISIN'], _auto_df['wkn'].fillna('')))
                        with st.spinner(f"Ticker für {len(_auto_tradeable)} Positionen werden ermittelt…"):
                            st.session_state["portfolio_isin_map"] = _openfigi_batch(
                                tuple(_auto_tradeable), wkn_by_isin=_auto_wkn_map)

    # ── Status-Badge ────────────────────────────────────────────────────────
    _sb_date_disp = st.session_state.get("portfolio_sb_date")
    if _sb_date_disp:
        st.markdown(
            f"<div style='background:{_C_CARD_BG};border:1px solid #1a3a55;border-radius:6px;"
            f"padding:6px 14px;font-size:0.82rem;color:{_C_ACCENT};margin-bottom:8px;display:inline-block;'>"
            f"✓ Gespeichertes Portfolio (Stand: {_sb_date_disp})</div>",
            unsafe_allow_html=True)

    # ── CSV-Upload ───────────────────────────────────────────────────────────
    # Immer anzeigen — versteckt hinter Expander wenn Portfolio bereits geladen.
    _has_portfolio = bool(st.session_state.get("portfolio_csv_bytes"))
    if _has_portfolio:
        with st.expander("📂 Neue CSV hochladen (Portfolio aktualisieren)"):
            uploaded = st.file_uploader(
                "Neue Orderhistorie hochladen (überschreibt gespeichertes Portfolio)",
                type=["csv"], key="portfolio_upload"
            )
    else:
        uploaded = st.file_uploader(
            "Orderhistorie CSV hochladen (Finanzen.net Zero → Aktivitäten → Exportieren)",
            type=["csv"], key="portfolio_upload"
        )

    if uploaded:
        raw = uploaded.read()
        st.session_state["portfolio_csv_bytes"] = raw
        with st.spinner("Positionen werden berechnet…"):
            df_port_new = _parse_portfolio_csv(raw)
        if df_port_new.empty:
            st.error("CSV konnte nicht gelesen werden. Bitte prüfe das Format (Finanzen.net Zero Orderhistorie).")
        else:
            st.session_state["portfolio_df"] = df_port_new.copy()
            tradeable = df_port_new[~df_port_new['is_crypto'] & ~df_port_new['is_warrant']]['ISIN'].tolist()
            if tradeable:
                _wkn_map = dict(zip(df_port_new['ISIN'], df_port_new['wkn'].fillna('')))
                with st.spinner(f"Ticker für {len(tradeable)} Positionen werden ermittelt…"):
                    isin_map_new = _openfigi_batch(tuple(tradeable), wkn_by_isin=_wkn_map)
                st.session_state["portfolio_isin_map"] = isin_map_new
            with st.spinner("Portfolio wird gespeichert…"):
                _saved_ok = _sb_save_portfolio(raw)
            if _saved_ok:
                import datetime as _dt_pf
                st.session_state["portfolio_sb_date"] = _dt_pf.date.today().strftime("%d.%m.%Y")
                st.success("✓ Portfolio gespeichert – wird beim nächsten Öffnen automatisch geladen.")
            st.rerun()

    df_port = st.session_state.get("portfolio_df")

    if df_port is not None and not df_port.empty:
        isin_map = st.session_state.get("portfolio_isin_map", {})

        stocks_etf = df_port[~df_port['is_crypto'] & ~df_port['is_warrant']].copy()
        crypto     = df_port[df_port['is_crypto']].copy()
        warrants   = df_port[df_port['is_warrant']].copy()

        # Manuell ausgeschlossene Positionen herausfiltern (Broker-Fehler / bereits verkauft)
        _excl_set = set(st.session_state.get("portfolio_excluded_isins", []))
        if _excl_set:
            stocks_etf = stocks_etf[~stocks_etf['ISIN'].isin(_excl_set)].copy()
            crypto     = crypto[~crypto['ISIN'].isin(_excl_set)].copy()

        # Manuelle Anteils-Korrektur via gespeichertem Delta (Δ = Zielwert − CSV-Wert zum Speicherzeitpunkt).
        # Delta wird auf aktuelle CSV-Stückzahl addiert → neue Käufe fließen automatisch ein.
        _man_shares = st.session_state.get("portfolio_manual_shares", {})
        for _msisin, _ms_entry in _man_shares.items():
            # Neues Format: {"delta": float, "csv_at_save": float}  |  altes Format: float (Migration)
            if isinstance(_ms_entry, dict):
                _ms_delta = float(_ms_entry.get("delta", 0))
            else:
                # Altes Format (absoluter Wert) — einmalig als Delta interpretieren
                # indem der gespeicherte Wert direkt als Zielwert behandelt wird:
                # Delta = gespeicherter_Wert − 0  (wird beim nächsten Speichern korrekt ersetzt)
                _ms_delta = float(_ms_entry)
            if _ms_delta == 0:
                continue
            _ms_mask = stocks_etf['ISIN'] == _msisin
            if _ms_mask.any():
                _ms_new = (stocks_etf.loc[_ms_mask, 'shares'] + _ms_delta).clip(lower=0)
                stocks_etf.loc[_ms_mask, 'shares'] = _ms_new
                stocks_etf.loc[_ms_mask, 'cost_basis'] = (
                    stocks_etf.loc[_ms_mask, 'avg_cost'] * _ms_new
                )
            _mc_mask = crypto['ISIN'] == _msisin
            if _mc_mask.any():
                _mc_new = (crypto.loc[_mc_mask, 'shares'] + _ms_delta).clip(lower=0)
                crypto.loc[_mc_mask, 'shares'] = _mc_new
                crypto.loc[_mc_mask, 'cost_basis'] = (
                    crypto.loc[_mc_mask, 'avg_cost'] * _mc_new
                )

        # Cache-Key: stabil basierend auf CSV-Inhalt (NICHT auf isin_map — die ändert sich beim FMP-Fallback!)
        _csv_b = st.session_state.get("portfolio_csv_bytes") or b""
        _csv_key = hash(_csv_b)
        _prices_cache_key  = f"prices_{_csv_key}"
        _qext_cache_key    = f"qext_{_csv_key}"
        _crypto_cache_key  = f"crypto_{_csv_key}"
        _alloc_cache_key   = f"alloc_{_csv_key}"

        prices: dict        = st.session_state.get(_prices_cache_key, {})
        quotes_ext: dict    = st.session_state.get(_qext_cache_key, {})
        _crypto_prices: dict = st.session_state.get(_crypto_cache_key, {})
        _alloc_infos: dict  = st.session_state.get(_alloc_cache_key, {})
        _sparklines: dict   = st.session_state.get(f"spark_{_alloc_cache_key}", {})

        # Manuell eingegebene Kurse übernehmen (vor Auto-Loader, damit kein Retry)
        for _mi, _mp in st.session_state.get("portfolio_manual_prices", {}).items():
            if _mp and float(_mp) > 0:
                prices[_mi] = float(_mp)

        # ── Kurse automatisch laden (nur wenn noch Positionen ohne Kurs) ─────
        _all_isins = stocks_etf['ISIN'].tolist() if not stocks_etf.empty else []

        # Disk-Cache wiederherstellen (Railway Volume /data, 30-Min TTL)
        if not prices and _all_isins:
            _pd = _pf_disk_load(f"prices_{_csv_key}", max_age_hours=0.5)
            if _pd:
                prices = _pd
                st.session_state[_prices_cache_key] = prices
            _qd = _pf_disk_load(f"qext_{_csv_key}", max_age_hours=0.5)
            if _qd:
                quotes_ext = _qd
                st.session_state[_qext_cache_key] = quotes_ext
        if _crypto_cache_key not in st.session_state and not crypto.empty:
            _cd = _pf_disk_load(f"crypto_{_csv_key}", max_age_hours=0.5)
            if _cd:
                _crypto_prices = _cd
                st.session_state[_crypto_cache_key] = _cd


        # Nur ISINs die wirklich noch nie versucht wurden (is None = kein Eintrag)
        # Wert 0.0 = versucht, kein Kurs gefunden (Sentinel, kein Retry)
        _missing_isins = [i for i in _all_isins if prices.get(i) is None]
        _prices_loaded = len(_missing_isins) == 0
        _prices_just_fetched = False
        if _missing_isins and not stocks_etf.empty:
            # GDR → geeigneter Ticker (sync mit _GDR_HARDCODED in _openfigi_batch)
            _GDR_FALLBACK = {
                'US78392B1070': '000660.KS',  # SK Hynix → KOSPI
                'US7960502018': 'SMSN.L',  # Samsung GDR Pref → LSE GDR (~€2.580)
                'US7960508882': 'SMSN.L',  # Samsung GDR Stamm → LSE GDR (~€2.580)
                'CNE100006M58': '0300.HK', # Midea Group H-Aktien → HKEx
            }
            for _gdr_isin, _gdr_tkr in _GDR_FALLBACK.items():
                if _gdr_isin in _missing_isins and _gdr_isin not in isin_map:
                    isin_map[_gdr_isin] = _gdr_tkr
            _tickers_to_load = [(isin_map.get(i), i) for i in _missing_isins if isin_map.get(i)]
            if _tickers_to_load:
                _pprog = st.progress(0, f"Kurse werden geladen: 0 / {len(_tickers_to_load)}…")
                for _pi, (_pt, _pi_isin) in enumerate(_tickers_to_load, 1):
                    _q = _portfolio_quote_ext(_pt)
                    prices[_pi_isin] = _q.get('price_eur')
                    quotes_ext[_pi_isin] = _q
                    _pprog.progress(_pi / len(_tickers_to_load),
                                    f"Kurse: {_pi} / {len(_tickers_to_load)}…")
                _pprog.empty()

                # FMP-ISIN-Fallback: für Positionen die noch keinen Preis haben
                if FMP_API_KEY:
                    _still_missing = [(_pi_isin2, isin_map.get(_pi_isin2, ''))
                                      for _pi_isin2 in _missing_isins
                                      if prices.get(_pi_isin2) is None]
                    if _still_missing:
                        _fp2 = st.progress(0, f"ISIN-Fallback: 0 / {len(_still_missing)}…")
                        for _fmi, (_fmisin, _fmtkr_old) in enumerate(_still_missing, 1):
                            try:
                                _fr = requests.get(
                                    "https://financialmodelingprep.com/api/v3/search",
                                    params={'query': _fmisin, 'limit': 8,
                                            'apikey': FMP_API_KEY}, timeout=6)
                                if _fr.ok:
                                    for _res in _fr.json():
                                        _sym = _res.get('symbol', '')
                                        _exch = _res.get('exchangeShortName', '')
                                        if not _sym:
                                            continue
                                        # Exchange-aware Suffix-Korrektur
                                        if _exch in ('KSE', 'KOSDAQ') and '.' not in _sym:
                                            _sym = f"{_sym}.KS"
                                        elif _exch in ('SHH', 'SHA') and '.' not in _sym:
                                            _sym = f"{_sym}.SS"
                                        elif _exch in ('SHZ', 'SZE') and '.' not in _sym:
                                            _sym = f"{_sym}.SZ"
                                        elif _exch in ('LSE', 'LON') and '.' not in _sym:
                                            _sym = f"{_sym}.L"
                                        elif _exch in ('HKSE', 'HKEX', 'HKG') and _sym.isdigit() and len(_sym) < 4:
                                            _sym = f"{_sym.zfill(4)}.HK"
                                        # FMP direkt abfragen (umgeht _portfolio_quote_ext-Cache)
                                        try:
                                            _fq = requests.get(
                                                f"https://financialmodelingprep.com/api/v3/quote/{_sym}",
                                                params={'apikey': FMP_API_KEY}, timeout=5)
                                            if not (_fq.ok and _fq.json()):
                                                continue
                                            _fd = _fq.json()[0]
                                            _pr = float(_fd.get('price') or 0)
                                            if not _pr:
                                                continue
                                            _cur = str(_fd.get('currency') or 'EUR').strip()
                                            if _cur == 'GBp':
                                                _pr /= 100.0; _cur = 'GBP'
                                            _fx2 = _get_eur_fx_rate(_cur) if _cur != 'EUR' else 1.0
                                            _peur = _pr * _fx2
                                            if not (0 < _peur < 1_000_000):
                                                continue
                                            _chg2 = _fd.get('changesPercentage')
                                            _q2 = {
                                                'price_eur':     _peur,
                                                'year_high_eur': float(_fd['yearHigh']) * _fx2 if _fd.get('yearHigh') else None,
                                                'year_low_eur':  float(_fd['yearLow'])  * _fx2 if _fd.get('yearLow')  else None,
                                                'day_chg_pct':   float(_chg2) if _chg2 is not None else None,
                                                'fx':            _fx2,
                                            }
                                            prices[_fmisin]     = _peur
                                            quotes_ext[_fmisin] = _q2
                                            isin_map[_fmisin]   = _sym
                                            break
                                        except Exception:
                                            continue
                            except Exception:
                                pass
                            _fp2.progress(_fmi / len(_still_missing),
                                          f"ISIN-Fallback: {_fmi} / {len(_still_missing)}…")
                        _fp2.empty()
                        st.session_state["portfolio_isin_map"] = isin_map

                _prices_just_fetched = True
            # Sentinel: alle noch nicht gefundenen Preise auf 0.0 setzen
            # damit sie beim nächsten Laden NICHT erneut versucht werden
            for _si in _missing_isins:
                if prices.get(_si) is None:
                    prices[_si] = 0.0
            st.session_state[_prices_cache_key] = prices
            st.session_state[_qext_cache_key]   = quotes_ext
            _pf_disk_save(f"prices_{_csv_key}", prices)
            _pf_disk_save(f"qext_{_csv_key}", quotes_ext)
        if _crypto_cache_key not in st.session_state and not crypto.empty:
            import re as _re
            import concurrent.futures as _cf_c
            for _, _crow in crypto.iterrows():
                _nm  = str(_crow.get('name', ''))
                _m   = _re.search(r'\(([A-Z]{2,10})\)', _nm)
                _sym = _m.group(1) if _m else (
                    _nm.strip().upper()
                    if _nm.strip().upper().isalpha() and len(_nm.strip()) <= 8 else None)
                if _sym:
                    _yf_tkr = f"{_sym}-EUR"
                    with _cf_c.ThreadPoolExecutor(max_workers=1) as _exe_c:
                        _fut_c = _exe_c.submit(lambda t=_yf_tkr: yf.Ticker(t).fast_info)
                        try:
                            _fi_c  = _fut_c.result(timeout=3.0)
                            _cp_c  = getattr(_fi_c, 'last_price', None)
                            if _cp_c and float(_cp_c) > 0:
                                _crypto_prices[_crow['ISIN']] = float(_cp_c)
                        except Exception:
                            pass
            _prices_just_fetched = True
            st.session_state[_crypto_cache_key] = _crypto_prices
            _pf_disk_save(f"crypto_{_csv_key}", _crypto_prices)
        if _prices_just_fetched:
            st.rerun()

        # ── Zusammenfassung ──────────────────────────────────────────
        total_invested = df_port['cost_basis'].sum()
        current_vals = []
        for _, row in stocks_etf.iterrows():
            p = prices.get(row['ISIN'])
            if p:
                current_vals.append(p * row['shares'])
        _crypto_val        = sum(_crypto_prices.get(r['ISIN'], 0) * r['shares'] for _, r in crypto.iterrows())
        _priced_stocks_val = sum(current_vals)
        current_total      = (_priced_stocks_val + _crypto_val) if (current_vals or _crypto_val) else None
        _priced_isins      = {isin for isin in stocks_etf['ISIN'] if prices.get(isin)}
        _priced_cost       = stocks_etf[stocks_etf['ISIN'].isin(_priced_isins)]['cost_basis'].sum() if not stocks_etf.empty else 0.0
        _crypto_cost       = crypto[crypto['ISIN'].isin(_crypto_prices)]['cost_basis'].sum() if not crypto.empty else 0.0
        _pnl_base          = _priced_cost + _crypto_cost
        pnl_eur  = (_priced_stocks_val + _crypto_val) - _pnl_base if (current_total and _pnl_base > 0) else None
        pnl_pct  = (pnl_eur / _pnl_base * 100) if (pnl_eur is not None and _pnl_base > 0) else None
        _unpriced_isins = [r['ISIN'] for _, r in stocks_etf.iterrows() if not prices.get(r['ISIN'])]
        _unpriced_isins += [r['ISIN'] for _, r in crypto.iterrows() if not _crypto_prices.get(r['ISIN'])]
        _unpriced = len(_unpriced_isins)
        _isin_to_name = {r['ISIN']: r['name'] for _, r in df_port.iterrows()}

        _pnl_str  = f"{pnl_eur:+,.0f} ({pnl_pct:+.1f}%)" if pnl_eur is not None else "—"
        _pnl_col  = _C_POSITIVE if (pnl_eur or 0) >= 0 else _C_NEGATIVE
        _stocks_str = f"€ {_priced_stocks_val:,.0f}" if _priced_stocks_val else "—"
        _total_str  = f"€ {current_total:,.0f}"       if current_total       else "—"
        _crypto_note = (f"<div style='color:{_C_TEXT_MUTED};font-size:0.62rem;margin-top:2px;'>"
                        f"+ Krypto € {_crypto_val:,.0f}</div>") if _crypto_val else ""
        if _unpriced > 0:
            _unpriced_names = ', '.join(_isin_to_name.get(i, i)[:22] for i in _unpriced_isins[:4])
            if _unpriced > 4:
                _unpriced_names += f' +{_unpriced - 4}'
            _unpriced_note = (f"<div style='color:#ff8a65;font-size:0.62rem;margin-top:2px;"
                              f"cursor:help;' title='{_unpriced_names}'>{_unpriced} ohne Kurs ⚠️</div>")
        else:
            _unpriced_note = ""
        st.markdown(f"""
        <div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin-bottom:6px;'>
          <div style='background:{_C_CARD_BG};border-radius:8px;padding:10px 12px;border:1px solid {_C_BORDER};min-width:0;'>
            <div style='color:{_C_TEXT_MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:.06em;'>Positionen</div>
            <div style='color:{_C_TEXT_PRIMARY};font-size:1.25rem;font-weight:700;margin-top:2px;'>{len(df_port)}</div>
            <div style='color:{_C_TEXT_MUTED};font-size:0.62rem;margin-top:2px;'>Aktien · ETFs · Krypto</div>
          </div>
          <div style='background:{_C_CARD_BG};border-radius:8px;padding:10px 12px;border:1px solid {_C_BORDER};min-width:0;'>
            <div style='color:{_C_TEXT_MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:.06em;'>Einstandswert</div>
            <div style='color:{_C_TEXT_PRIMARY};font-size:1.25rem;font-weight:700;margin-top:2px;'>€ {total_invested:,.0f}</div>
            <div style='color:{_C_TEXT_MUTED};font-size:0.62rem;margin-top:2px;'>Buchwert offener Positionen</div>
          </div>
          <div style='background:{_C_CARD_BG};border-radius:8px;padding:10px 12px;border:1px solid {_C_BORDER};min-width:0;'>
            <div style='color:{_C_TEXT_MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:.06em;'>Aktien &amp; ETFs</div>
            <div style='color:{_C_TEXT_PRIMARY};font-size:1.25rem;font-weight:700;margin-top:2px;'>{_stocks_str}</div>
            {_unpriced_note}
          </div>
          <div style='background:{_C_CARD_BG};border-radius:8px;padding:10px 12px;border:1px solid {_C_BORDER};min-width:0;'>
            <div style='color:{_C_TEXT_MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:.06em;'>Gesamt inkl. Krypto</div>
            <div style='color:{_C_ACCENT};font-size:1.25rem;font-weight:700;margin-top:2px;'>{_total_str}</div>
            {_crypto_note}
          </div>
          <div style='background:{_C_CARD_BG};border-radius:8px;padding:10px 12px;border:1px solid {_C_BORDER};min-width:0;'>
            <div style='color:{_C_TEXT_MUTED};font-size:0.7rem;text-transform:uppercase;letter-spacing:.06em;'>P&L unreal.</div>
            <div style='color:{_pnl_col};font-size:1.05rem;font-weight:700;margin-top:2px;'>{_pnl_str}</div>
            <div style='color:{_C_TEXT_MUTED};font-size:0.62rem;margin-top:2px;'>offene Positionen</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        _caption_cols = st.columns([4, 1])
        with _caption_cols[0]:
            st.caption("ℹ️ Aktueller Wert enthält nur bewertete Positionen (kein Verrechnungskonto, keine Dividenden). "
                       "Realisierte Gewinne & Gesamtrendite → Performance-Tab.")
        with _caption_cols[1]:
            if _unpriced > 0 and st.button("🔄 Ticker neu laden", key="pf_reload_tickers",
                                            use_container_width=True, help="Kurs-Cache leeren und erneut laden"):
                # Nur Preise der ungelösten Positionen löschen — NICHT die gesamte isin_map!
                # (Löschen von portfolio_isin_map würde alle 69 Positionen per FMP-ISIN neu suchen → ~7 Min.)
                _rl_prices = st.session_state.get(_prices_cache_key, {})
                _rl_qext   = st.session_state.get(_qext_cache_key, {})
                for _ri in _unpriced_isins:
                    _rl_prices.pop(_ri, None)
                    _rl_qext.pop(_ri, None)
                st.session_state[_prices_cache_key] = _rl_prices
                st.session_state[_qext_cache_key]   = _rl_qext
                for _ck in [_alloc_cache_key, f"spark_{_alloc_cache_key}", _crypto_cache_key]:
                    st.session_state.pop(_ck, None)
                # GDR-Ticker direkt in isin_map aktualisieren ohne sie komplett zu löschen
                _rl_imap = st.session_state.get("portfolio_isin_map", {})
                for _gi, _gt in {
                    'US78392B1070': '000660.KS',
                    'US7960502018': 'SMSN.L',
                    'US7960508882': 'SMSN.L',
                    'CNE100006M58': '0300.HK',
                }.items():
                    _rl_imap[_gi] = _gt
                st.session_state["portfolio_isin_map"] = _rl_imap
                _portfolio_quote_ext.clear()
                st.rerun()

        # ── Portfolio-Korrekturen (Ausschlüsse + manuelle Kurse) ─────────────
        with st.expander("⚙️ Portfolio-Korrekturen", expanded=False):
            _pf_col1, _pf_col2 = st.columns(2)

            with _pf_col1:
                st.markdown("**Positionen ausschließen**")
                st.caption("Broker-Fehler: Position ist laut CSV noch offen, wurde aber bereits verkauft.")
                _all_pos_dict = {r['ISIN']: r['name'] for _, r in df_port.iterrows()}
                _excl_opts    = {f"{n[:38]} ({i})": i for i, n in _all_pos_dict.items()}
                _cur_excl     = st.session_state.get("portfolio_excluded_isins", [])
                _cur_excl_lbl = [lbl for lbl, isin in _excl_opts.items() if isin in _cur_excl]
                _new_excl_lbl = st.multiselect(
                    "Ausgeschlossene Positionen:",
                    options=list(_excl_opts.keys()),
                    default=_cur_excl_lbl,
                    key="pf_excl_select",
                )
                _new_excl_isins = [_excl_opts[l] for l in _new_excl_lbl]
                if sorted(_new_excl_isins) != sorted(_cur_excl):
                    st.session_state["portfolio_excluded_isins"] = _new_excl_isins
                    _save_portfolio_settings(
                        _new_excl_isins,
                        st.session_state.get("portfolio_manual_prices", {}),
                        st.session_state.get("portfolio_manual_shares", {}),
                    )
                    for _ck in [_alloc_cache_key, f"spark_{_alloc_cache_key}"]:
                        st.session_state.pop(_ck, None)
                    st.session_state["show_portfolio"] = True
                    st.session_state["show_landing"] = False
                    st.rerun()

            with _pf_col2:
                st.markdown("**Kurse manuell eingeben (EUR)**")
                st.caption("Für Positionen ohne automatischen Kurs (z.B. GDRs, exotische Ticker).")
                _man_prices = dict(st.session_state.get("portfolio_manual_prices", {}))
                _unpriced_pf = [r for _, r in df_port.iterrows()
                                if r['ISIN'] not in _excl_set and not prices.get(r['ISIN'])]
                if _unpriced_pf:
                    _changed_mp = False
                    for _urow in _unpriced_pf:
                        _uisin = _urow['ISIN']
                        _ucur  = float(_man_prices.get(_uisin, 0.0))
                        _unew  = st.number_input(
                            f"{_urow['name'][:32]}",
                            min_value=0.0, value=_ucur, step=1.0, format="%.2f",
                            key=f"mp_{_uisin}",
                            help=f"ISIN: {_uisin}",
                        )
                        if _unew != _ucur:
                            _man_prices[_uisin] = _unew
                            _changed_mp = True
                    if st.button("💾 Kurse speichern", key="pf_save_manual"):
                        _saved_mp = {k: v for k, v in _man_prices.items() if v and v > 0}
                        st.session_state["portfolio_manual_prices"] = _saved_mp
                        _save_portfolio_settings(
                            st.session_state.get("portfolio_excluded_isins", []),
                            _saved_mp,
                            st.session_state.get("portfolio_manual_shares", {}),
                        )
                        for _ck in [_prices_cache_key, _alloc_cache_key, f"spark_{_alloc_cache_key}"]:
                            st.session_state.pop(_ck, None)
                        st.session_state["show_portfolio"] = True
                        st.session_state["show_landing"] = False
                        st.rerun()
                else:
                    st.success("Alle Positionen haben einen Kurs.")

            st.markdown("---")
            st.markdown("**Anteile manuell korrigieren**")
            st.caption(
                "Tatsächliche Stückzahl eingeben. Neue Käufe in späteren CSVs werden "
                "automatisch dazugerechnet — einmal eingeben reicht."
            )
            _man_shr = dict(st.session_state.get("portfolio_manual_shares", {}))
            _all_pf_rows = [r for _, r in df_port.iterrows() if r['ISIN'] not in _excl_set]
            _shr_cols = st.columns(3)
            for _si, _srow in enumerate(_all_pf_rows):
                _sisin   = _srow['ISIN']
                _csv_sh  = float(_srow['shares'])   # roher CSV-Wert (noch kein Delta)
                _entry   = _man_shr.get(_sisin)
                # Aus gespeichertem Delta aktuellen Zielwert berechnen
                if isinstance(_entry, dict):
                    _stored_delta = float(_entry.get("delta", 0))
                elif _entry:
                    _stored_delta = float(_entry)   # altes Format: war absoluter Wert, jetzt als Delta
                else:
                    _stored_delta = 0.0
                _display_val = max(0.0, _csv_sh + _stored_delta) if _stored_delta else 0.0
                with _shr_cols[_si % 3]:
                    _new_abs = st.number_input(
                        f"{_srow['name'][:28]}",
                        min_value=0.0,
                        value=_display_val,
                        step=0.001,
                        format="%.4f",
                        key=f"ms_{_sisin}",
                        help=(
                            f"ISIN: {_sisin}\n"
                            f"CSV-Wert: {_csv_sh:.4f} Stk.\n"
                            f"{'Gespeichertes Δ: {:+.4f} Stk.'.format(_stored_delta) if _stored_delta else 'Noch keine Korrektur gespeichert'}\n"
                            f"0 = Korrektur entfernen"
                        ),
                    )
                    _new_delta = round(_new_abs - _csv_sh, 6) if _new_abs > 0 else 0.0
                    _man_shr[_sisin] = {"delta": _new_delta, "csv_at_save": _csv_sh}
            if st.button("💾 Anteile speichern", key="pf_save_shares"):
                _saved_shr = {
                    k: v for k, v in _man_shr.items()
                    if (v.get("delta", 0) if isinstance(v, dict) else v) != 0
                }
                st.session_state["portfolio_manual_shares"] = _saved_shr
                _save_portfolio_settings(
                    st.session_state.get("portfolio_excluded_isins", []),
                    st.session_state.get("portfolio_manual_prices", {}),
                    _saved_shr,
                )
                # Kurs- und Sektorcaches bleiben erhalten – Stückzahlen ändern sie nicht.
                # Navigationsschutz: explizit Portfolio-Seite behalten (verhindert Landing-Page-Redirect).
                st.session_state["show_portfolio"] = True
                st.session_state["show_landing"] = False
                st.rerun()

        tab_pos, tab_alloc, tab_perf, tab_holdings, tab_ki = st.tabs(
            ["📊 Positionen", "🥧 Aufteilung", "📈 Performance", "🔍 Holdings", "🤖 KI-Analyse"])

        # ── Disk-Cache für Sektor-/Analyst-Daten laden (überlebt Deploys) ──────
        _disk_sec_cache = _load_isin_sector_cache()
        _disk_sec_dirty = False  # wird True wenn neue Daten geladen wurden
        for _disin, _ddata in _disk_sec_cache.items():
            if _disin not in _alloc_infos:
                _alloc_infos[_disin] = _ddata
        if _disk_sec_cache:
            st.session_state[_alloc_cache_key] = _alloc_infos

        # ── Top-10 Analyst-Daten (nur fehlende Positionen — meist aus Disk-Cache) ─
        _ai_isins_needed = [(isin_map.get(i), i)
                            for i in stocks_etf.nlargest(10, 'cost_basis')['ISIN']
                            if isin_map.get(i) and i not in _alloc_infos]
        if _ai_isins_needed:
            _aprog = st.progress(0, f"Analyst-Daten: 0 / {len(_ai_isins_needed)}…")
            for _aii, (_at, _ai) in enumerate(_ai_isins_needed, 1):
                _inf_r = _get_ticker_info_cached(_at)
                _alloc_infos[_ai] = _inf_r
                _disk_sec_cache[_ai] = {k: _inf_r.get(k, '') for k in
                                        ('quote_type', 'sector', 'recommendation')}
                _disk_sec_dirty = True
                _aprog.progress(_aii / len(_ai_isins_needed),
                                f"Analyst-Daten: {_aii} / {len(_ai_isins_needed)}…")
            _aprog.empty()
            st.session_state[_alloc_cache_key] = _alloc_infos

        if _disk_sec_dirty:
            _save_isin_sector_cache(_disk_sec_cache)

        # Cache-Keys für lazy loading in den Tabs
        _sec_loaded_key = f"sec_loaded_{_alloc_cache_key}"
        _hb_cache_key   = f"hb_{_alloc_cache_key}"

        # ── Performance-Daten aus Disk-Cache wiederherstellen (/data überlebt Deploys) ──
        _irr_ck = f"irr_{_csv_key}"
        if _irr_ck not in st.session_state:
            _irr_disk = _pf_disk_load(f"irr_{_csv_key}", max_age_hours=168)
            if _irr_disk is not None:
                st.session_state[_irr_ck] = _irr_disk
        for _bmt in ("SXR8.DE", "VWCE.DE", "EQQQ.DE", "EXS1.DE"):
            _bmt_k = f"bm_{_csv_key}_{_bmt}"
            if _bmt_k not in st.session_state:
                _bmt_disk = _pf_disk_load(f"bm_{_csv_key}_{_bmt}", max_age_hours=168)
                if _bmt_disk is not None:
                    st.session_state[_bmt_k] = _bmt_disk

        # (debug counter removed)

        with tab_pos:
          try:
            # Sparklines: nur anzeigen wenn bereits im Session-/Prozess-Cache, niemals auto-laden.
            # Kein Button — Button-Click triggert Rerun → blockiert alle Tabs gleichermaßen.

            # ── Aktien & ETFs ────────────────────────────────────────────
            if not stocks_etf.empty:
                st.markdown("<div class='section-header'>📈 Aktien & ETFs</div>", unsafe_allow_html=True)
                _RBADGE = {'strongbuy':('Strong Buy',_C_POSITIVE),'buy':('Kaufen',_C_POSITIVE),
                              'hold':('Halten',_C_NEUTRAL),'sell':('Verkaufen',_C_NEGATIVE),
                              'strongsell':('Strong Sell',_C_NEGATIVE)}
                for _, row in stocks_etf.iterrows():
                    tkr       = isin_map.get(row['ISIN'])
                    cur_price = prices.get(row['ISIN'])
                    cur_val   = cur_price * row['shares'] if cur_price else None
                    pnl_pos   = ((cur_val - row['cost_basis']) / row['cost_basis'] * 100) if (cur_val and row['cost_basis'] > 0) else None
                    _qx  = quotes_ext.get(row['ISIN'], {})
                    _inf = _alloc_infos.get(row['ISIN'], {})

                    c1, c2, c3, c4, c5 = st.columns([3, 1.1, 1.1, 1.6, 1])
                    with c1:
                        _rl, _rc = _RBADGE.get(_inf.get('recommendation',''), ('',''))
                        _badge_h = (f"<span style='background:{_rc}22;color:{_rc};font-size:0.62rem;"
                                    f"padding:1px 5px;border-radius:3px;margin-left:5px;font-weight:600;'>{_rl}</span>") if _rl else ''
                        _tgt = _inf.get('target_native')
                        _tgt_h = ''
                        if _tgt and cur_price and _qx.get('fx'):
                            _up = (_tgt * _qx['fx'] / cur_price - 1) * 100
                            _uc = _C_POSITIVE if _up >= 0 else _C_NEGATIVE
                            _tgt_h = f"<span style='color:{_uc};font-size:0.62rem;margin-left:4px;'>KZ {_up:+.0f}%</span>"
                        _spark_h = (f"<div style='margin-top:3px;line-height:0;'>{_sparklines[tkr]}</div>"
                                    if tkr and tkr in _sparklines else '')
                        st.markdown(
                            f"<div style='color:{_C_TEXT_PRIMARY};font-weight:600;font-size:0.93rem;'>{row['name'][:36]}{_badge_h}{_tgt_h}</div>"
                            f"<div style='color:{_C_TEXT_MUTED};font-size:0.72rem;'>{row['ISIN']} · {row['wkn']}"
                            f"{' · '+tkr if tkr else ''}</div>{_spark_h}",
                            unsafe_allow_html=True)
                    with c2:
                        st.markdown(
                            f"<div style='color:#78909c;font-size:0.72rem;'>Anteile</div>"
                            f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.88rem;font-weight:600;'>{row['shares']:.4f}</div>",
                            unsafe_allow_html=True)
                    with c3:
                        st.markdown(
                            f"<div style='color:#78909c;font-size:0.72rem;'>Ø Kurs</div>"
                            f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.88rem;font-weight:600;'>€ {row['avg_cost']:.2f}</div>",
                            unsafe_allow_html=True)
                    with c4:
                        if cur_price:
                            _clr = _C_POSITIVE if pnl_pos and pnl_pos >= 0 else _C_NEGATIVE
                            _dc  = _qx.get('day_chg_pct')
                            _dc_h = (f"<span style='color:{_C_POSITIVE if _dc>=0 else _C_NEGATIVE};"
                                     f"font-size:0.68rem;'> {_dc:+.2f}%</span>") if _dc is not None else ''
                            _yh, _yl = _qx.get('year_high_eur'), _qx.get('year_low_eur')
                            _52h = ''
                            if _yh and _yl and _yh > _yl and cur_price and cur_price > 0:
                                _pp = max(0, min(100, (cur_price - _yl) / (_yh - _yl) * 100))
                                _pfmt = (lambda v: f"€{v:.4f}" if v < 1 else f"€{v:,.2f}" if v < 100 else f"€{v:,.0f}")
                                _52h = (f"<div style='margin-top:4px;'>"
                                        f"<div style='display:flex;justify-content:space-between;"
                                        f"color:#37474f;font-size:0.6rem;'>"
                                        f"<span>{_pfmt(_yl)}</span><span style='color:#455a64;'>52W</span>"
                                        f"<span>{_pfmt(_yh)}</span></div>"
                                        f"<div style='background:#1a2740;border-radius:3px;height:4px;margin-top:2px;'>"
                                        f"<div style='background:#42a5f5;width:{_pp:.0f}%;height:4px;border-radius:3px;'>"
                                        f"</div></div></div>")
                            st.markdown(
                                f"<div style='color:#78909c;font-size:0.72rem;'>Kurs · Heute · P&L</div>"
                                f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.88rem;font-weight:600;'>{'€ ' + (f'{cur_price:.4f}' if cur_price < 1 else f'{cur_price:,.2f}')}{_dc_h}</div>"
                                f"<div style='color:{_clr};font-size:0.8rem;font-weight:600;'>"
                                f"{pnl_pos:+.1f}% (€ {cur_val - row['cost_basis']:+,.0f})</div>{_52h}",
                                unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='color:{_C_TEXT_MUTED};font-size:0.8rem;margin-top:14px;'>kein Kurs</div>",
                                        unsafe_allow_html=True)
                    with c5:
                        if tkr:
                            if st.button("🔍", key=f"pf_ana_{row['ISIN']}", use_container_width=True,
                                         help=f"Vollanalyse: {row['name'][:30]}"):
                                _go_to_ticker(tkr)
                                st.rerun()
                    st.markdown("<hr style='border-color:#1a2740;margin:5px 0;'>", unsafe_allow_html=True)

            # ── Dividenden-Schätzung ─────────────────────────────────
            if not stocks_etf.empty and _alloc_infos:
                _div_items = []
                for _, _dr in stocks_etf.iterrows():
                    _drate = float(_alloc_infos.get(_dr['ISIN'], {}).get('div_rate_native') or 0)
                    if _drate > 0:
                        _dfx  = quotes_ext.get(_dr['ISIN'], {}).get('fx', 1.0)
                        _deur = _drate * _dfx * _dr['shares']
                        _dp   = prices.get(_dr['ISIN'])
                        _dyld = (_drate * _dfx / _dp * 100) if (_dp and _dp > 0) else None
                        _div_items.append({'name': _dr['name'][:34], 'eur': _deur, 'yield': _dyld})
                if _div_items:
                    _div_sum = sum(d['eur'] for d in _div_items)
                    with st.expander(
                        f"💰 Dividenden-Schätzung — ca. € {_div_sum:,.0f} / Jahr "
                        f"({len(_div_items)} Positionen)"):
                        for _di in sorted(_div_items, key=lambda x: x['eur'], reverse=True):
                            _ys = f"  ·  {_di['yield']:.2f}% Div.-Rendite" if _di['yield'] else ""
                            st.markdown(
                                f"<div style='display:flex;justify-content:space-between;padding:4px 2px;"
                                f"border-bottom:1px solid #1a2740;'>"
                                f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.82rem;'>{_di['name']}</span>"
                                f"<span style='color:#ffd600;font-size:0.82rem;font-weight:600;'>"
                                f"€ {_di['eur']:,.0f}/Jahr{_ys}</span></div>",
                                unsafe_allow_html=True)
                        st.caption("Quelle: trailingAnnualDividendRate (yFinance). Schätzung, nicht garantiert.")


            # ── Krypto ──────────────────────────────────────────────────
            if not crypto.empty:
                st.markdown("<div class='section-header'>₿ Krypto</div>", unsafe_allow_html=True)
                for _, row in crypto.iterrows():
                    _cp = _crypto_prices.get(row['ISIN'])
                    _cv = _cp * row['shares'] if _cp else None
                    _cpnl = (_cv - row['cost_basis']) if _cv is not None else None
                    _cpnl_pct = (_cpnl / row['cost_basis'] * 100) if (_cpnl is not None and row['cost_basis'] > 0) else None
                    _cv_str = f"€ {_cv:,.2f}" if _cv else "—"
                    _cpnl_str = f"{_cpnl:+,.2f} ({_cpnl_pct:+.1f}%)" if _cpnl is not None else "—"
                    _cpnl_col = _C_POSITIVE if (_cpnl or 0) >= 0 else _C_NEGATIVE
                    _price_str = f"€ {_cp:,.4f}" if _cp else "kein Kurs"
                    st.markdown(
                        f"<div style='background:{_C_CARD_BG};border-radius:8px;padding:10px 14px;"
                        f"border:1px solid #1a2740;margin-bottom:6px;display:flex;"
                        f"justify-content:space-between;align-items:center;'>"
                        f"<div><div style='color:{_C_TEXT_PRIMARY};font-size:0.9rem;font-weight:600;'>₿ {row['name']}</div>"
                        f"<div style='color:{_C_TEXT_MUTED};font-size:0.7rem;margin-top:2px;'>"
                        f"{row['ISIN']} · {row['shares']:.6f} Stk. · Ø {row['avg_cost']:.4f} · Kurs: {_price_str}</div></div>"
                        f"<div style='text-align:right;'>"
                        f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.95rem;font-weight:700;'>{_cv_str}</div>"
                        f"<div style='color:{_cpnl_col};font-size:0.75rem;'>{_cpnl_str}</div>"
                        f"</div></div>",
                        unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            # ── Positions-Donut ──────────────────────────────────────
            _dn_labels, _dn_values = [], []
            for _, _dnr in stocks_etf.iterrows():
                _dnp = prices.get(_dnr['ISIN'])
                _dnv = (_dnp * _dnr['shares']) if _dnp else _dnr['cost_basis']
                if _dnv > 0:
                    _dn_labels.append(_dnr['name'][:30])
                    _dn_values.append(round(_dnv, 2))
            for _, _dnr in crypto.iterrows():
                _dnp = _crypto_prices.get(_dnr['ISIN'])
                _dnv = (_dnp * _dnr['shares']) if _dnp else _dnr['cost_basis']
                if _dnv > 0:
                    _dn_labels.append(f"₿ {_dnr['name'][:24]}")
                    _dn_values.append(round(_dnv, 2))

            if _dn_labels:
                _dn_total = sum(_dn_values)
                # Kontrastreiche Farbpalette — gleichmäßig über alle Farbtöne verteilt
                _DN_PALETTE = [
                    '#2196F3','#FF5722','#4CAF50','#E91E63','#FF9800',
                    '#00BCD4','#9C27B0','#CDDC39','#F44336','#00E676',
                    '#3F51B5','#FFD600','#009688','#FF4081','#8BC34A',
                    '#7C4DFF','#FF6D00','#26C6DA','#D500F9','#76FF03',
                    '#FF1744','#00B0FF','#FFAB40','#69F0AE','#EA80FC',
                    '#40C4FF','#FF6E40','#B2FF59','#FF80AB','#82B1FF',
                ]
                _dn_clrs = [_DN_PALETTE[i % len(_DN_PALETTE)] for i in range(len(_dn_labels))]
                _dn_fig = go.Figure(go.Pie(
                    labels=_dn_labels, values=_dn_values,
                    hole=0.62, textinfo='none', sort=True,
                    hovertemplate='<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>',
                    marker=dict(colors=_dn_clrs, line=dict(color='#0a1628', width=2)),
                ))
                _dn_fig.update_layout(
                    template=_C_CHART_THEME, paper_bgcolor=_C_CHART_BG, plot_bgcolor=_C_CHART_BG,
                    showlegend=False, margin=dict(t=20, b=10, l=10, r=10), height=340,
                    annotations=[dict(
                        text=f"<b>Portfolio</b><br>€ {_dn_total:,.0f}",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=13, color='#eceff1'), align='center',
                    )],
                )
                st.plotly_chart(_dn_fig, use_container_width=True,
                                key=f"donut_{_alloc_cache_key}")

            st.caption("Kurse in EUR umgerechnet (Wechselkurs via yFinance). P&L basiert auf dem Ø-Kaufkurs aus der Orderhistorie.")


          except Exception as _e_pos:
              st.error(f"Fehler im Positionen-Tab: {_e_pos}")

        with tab_alloc:
          try:
            # ── Sektor-Daten für alle Positionen (auf Knopfdruck, einmalig gecacht) ──
            _sec_load_btn_key = f"sec_load_btn_{_alloc_cache_key}"
            if not st.session_state.get(_sec_loaded_key) and not stocks_etf.empty:
                _sec_miss2 = [(isin_map.get(r['ISIN']), r['ISIN'])
                              for _, r in stocks_etf.iterrows()
                              if r['ISIN'] not in _alloc_infos and isin_map.get(r['ISIN'])]
                if _sec_miss2:
                    if not st.session_state.get(_sec_load_btn_key):
                        st.info(
                            f"Sektordaten für {len(_sec_miss2)} Positionen fehlen noch. "
                            "Lädt ~15–60 Sek., danach für diese Sitzung gespeichert."
                        )
                        if st.button("📊 Sektordaten laden", type="primary",
                                     key="btn_sec_load", use_container_width=True):
                            st.session_state[_sec_load_btn_key] = True
                            st.rerun()
                    if st.session_state.get(_sec_load_btn_key):
                        _sprog2 = st.progress(0, f"Sektordaten: 0 / {len(_sec_miss2)}…")
                        _new_sc: dict = {}
                        for _sii2, (_stk2, _sisin2) in enumerate(_sec_miss2, 1):
                            _inf_s = _get_ticker_info_cached(_stk2)
                            _alloc_infos[_sisin2] = _inf_s
                            _new_sc[_sisin2] = {k: _inf_s.get(k, '') for k in
                                                ('quote_type', 'sector', 'recommendation')}
                            _sprog2.progress(_sii2 / len(_sec_miss2),
                                             f"Sektordaten: {_sii2} / {len(_sec_miss2)}…")
                        _sprog2.empty()
                        st.session_state[_alloc_cache_key] = _alloc_infos
                        _disk_sec_cache.update(_new_sc)
                        _save_isin_sector_cache(_disk_sec_cache)
                        st.session_state[_sec_loaded_key] = True
                else:
                    st.session_state[_sec_loaded_key] = True

            if stocks_etf.empty and crypto.empty:
                st.info("Keine Positionsdaten vorhanden.")
            else:
                _alloc_rows = []
                for _, _arow in df_port.iterrows():
                    _tkr2  = isin_map.get(_arow['ISIN'], '')
                    _info2 = _alloc_infos.get(_arow['ISIN'], {})
                    _prc   = prices.get(_arow['ISIN'])
                    _val   = max(0.0, (_prc if _prc else _arow['avg_cost']) * _arow['shares'])

                    # ETF-Erkennung: analyst-info für Top-10 + bekannte Ticker-Maps für alle anderen
                    _is_etf = (_info2.get('quote_type') == 'ETF' or
                               _tkr2 in _ETF_CW or _tkr2 in _ETF_SW)

                    if _arow['is_crypto']:
                        _ac, _reg, _sec_de = 'Krypto', 'Global', 'Krypto'
                    elif _arow['is_warrant']:
                        _ac, _reg, _sec_de = 'Optionsscheine', _ticker_to_region(_tkr2), 'Optionsscheine'
                    elif _is_etf:
                        _ac, _reg = 'ETF / Fonds', _ticker_to_region(_tkr2)
                        # Sektor-Look-Through: ETF in echte Branchen aufteilen
                        _sw_lt = _ETF_SW.get(_tkr2)
                        if _sw_lt:
                            _sw_sum = sum(_sw_lt.values()) or 1
                            for _sn, _sw_w in _sw_lt.items():
                                _alloc_rows.append({'value': _val * _sw_w / _sw_sum,
                                                    'asset': _ac, 'region': _reg, 'sector': _sn})
                            continue
                        _sec_de = 'ETF / Fonds'
                    else:
                        _ac, _reg = 'Aktien', _ticker_to_region(_tkr2)
                        _raw_sec = _info2.get('sector', '') or _ISIN_SECTOR_HARD.get(_arow['ISIN'], '')
                        _sec_de  = _SECTOR_DE.get(_raw_sec, _raw_sec) or 'Sonstige'

                    _alloc_rows.append({'value': _val, 'asset': _ac, 'region': _reg, 'sector': _sec_de})

                _adf = pd.DataFrame(_alloc_rows)
                _tot = _adf['value'].sum()

                def _mk_donut(col, cmap, title):
                    _g = _adf.groupby(col)['value'].sum().sort_values(ascending=False)
                    _lbls = _g.index.tolist()
                    _vals = _g.values.tolist()
                    _cols = [cmap.get(l, '#546e7a') for l in _lbls]
                    _fig  = go.Figure(go.Pie(
                        labels=_lbls, values=_vals, hole=0.62,
                        marker=dict(colors=_cols, line=dict(color='#0a1628', width=2)),
                        textinfo='none',
                        hovertemplate='<b>%{label}</b><br>€ %{value:,.0f} · %{percent}<extra></extra>',
                    ))
                    _fig.update_layout(
                        template=_C_CHART_THEME, paper_bgcolor=_C_CHART_BG, plot_bgcolor=_C_CHART_BG,
                        showlegend=False, height=240,
                        margin=dict(l=5, r=5, t=5, b=5),
                    )
                    return _fig, _g

                _col1, _col2, _col3 = st.columns(3)
                for _col_st, _grp_col, _cmap, _title in [
                    (_col1, 'asset',  _ASSET_COLORS,  'Assetklassen'),
                    (_col2, 'region', _REGION_COLORS, 'Regionen'),
                    (_col3, 'sector', _SECTOR_COLORS, 'Branchen'),
                ]:
                    with _col_st:
                        st.markdown(
                            f"<div style='text-align:center;color:{_C_TEXT_MUTED2};font-size:0.8rem;"
                            f"font-weight:600;letter-spacing:.08em;text-transform:uppercase;"
                            f"margin-bottom:4px;'>{_title}</div>", unsafe_allow_html=True)
                        _fig_d, _grp_d = _mk_donut(_grp_col, _cmap, _title)
                        st.plotly_chart(_fig_d, use_container_width=True)
                        for _lbl, _v in _grp_d.items():
                            _pct = _v / _tot * 100 if _tot > 0 else 0
                            _clr = _cmap.get(_lbl, '#546e7a')
                            st.markdown(
                                f"<div style='display:flex;justify-content:space-between;"
                                f"align-items:center;padding:4px 2px;"
                                f"border-bottom:1px solid #1a2740;'>"
                                f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.82rem;'>"
                                f"<span style='color:{_clr};'>●</span> {_lbl}</span>"
                                f"<span style='color:{_C_TEXT_MUTED2};font-size:0.82rem;font-weight:600;'>"
                                f"{_pct:.1f}%</span></div>",
                                unsafe_allow_html=True)

                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                st.caption("Sektoren via yFinance. Regionen basieren auf der Börsenlistung. "
                           "ETF-Look-Through → echte Länderexposition weiter unten.")

                # ── ETF Look-Through: echte Länder-/Kontinentexposition ───────
                st.markdown("<div class='section-header'>🌍 Geographische Exposition (Look-Through)</div>",
                            unsafe_allow_html=True)
                _lt: dict = {}           # Länder → EUR-Wert
                _lt_etfs_found = []      # ETFs mit bekannten CW
                _lt_etfs_missing = []    # ETFs ohne CW-Daten
                for _, _lrow in df_port.iterrows():
                    _ltkr  = isin_map.get(_lrow['ISIN'], '')
                    _lprc  = prices.get(_lrow['ISIN'])
                    _lval  = (_lprc if _lprc else _lrow['avg_cost']) * _lrow['shares']
                    _linf  = _alloc_infos.get(_lrow['ISIN'], {})
                    _is_etf = _linf.get('quote_type') == 'ETF' or _lrow.get('is_etf', False)
                    # ETFs: Look-Through via _ETF_CW
                    if _is_etf and _ltkr:
                        _lcw = _ETF_CW.get(_ltkr)
                        if _lcw:
                            _lcw_sum = sum(_lcw.values())
                            for _lc, _lw in _lcw.items():
                                _lt[_lc] = _lt.get(_lc, 0) + _lval * (_lw / _lcw_sum)
                            _lt_etfs_found.append(_lrow['name'][:28])
                        else:
                            # Kein CW → als "Sonstige" einbuchen
                            _lt['Sonstige'] = _lt.get('Sonstige', 0) + _lval
                            _lt_etfs_missing.append(_lrow['name'][:28])
                    elif _lrow.get('is_crypto'):
                        _lt['Krypto'] = _lt.get('Krypto', 0) + _lval
                    elif not _lrow.get('is_warrant'):
                        # Einzelaktien: Land via Börsen-Suffix; GDR-Überschreibung für US-ISIN mit Heimatland
                        _lctry = _GDR_COUNTRY.get(_lrow['ISIN'], _ticker_to_country(_ltkr))
                        _lt[_lctry] = _lt.get(_lctry, 0) + _lval

                _lt_total = sum(_lt.values()) or 1
                _lt_sorted = sorted(_lt.items(), key=lambda x: x[1], reverse=True)

                # Länder-Farben (gleich wie im ETF-Analyzer)
                _LT_CLR = {
                    'USA':'#1565c0','Deutschland':'#00838f','UK':'#7b1fa2',
                    'Japan':'#e65100','Frankreich':'#2e7d32','Kanada':'#f57f17',
                    'Schweiz':'#4a148c','Australien':'#00695c','China':'#b71c1c',
                    'Indien':'#ff6f00','Taiwan':'#880e4f','Südkorea':'#1b5e20',
                    'Niederlande':'#006064','Schweden':'#01579b','Spanien':'#bf360c',
                    'Brasilien':'#33691e','Sonstige':'#455a64','Krypto':'#f9a825',
                    'Nordamerika':'#1565c0','Europa':'#00695c','Asien/Pazifik':'#e64a19',
                    'Lateinamerika':'#f57f17','Mittlerer Osten':'#5d4037','Afrika':'#6d4c41',
                }

                # Kontinent-Aggregation
                _cont: dict = {}
                for _lc, _lv in _lt.items():
                    _lco = _CONTINENT_MAP.get(_lc, 'Sonstige')
                    _cont[_lco] = _cont.get(_lco, 0) + _lv
                _cont = dict(sorted(_cont.items(), key=lambda x: x[1], reverse=True))

                _lta, _ltb = st.columns([1.1, 1])
                with _lta:
                    st.markdown(f"<div style='color:{_C_ACCENT};font-size:0.72rem;font-weight:600;"
                                "letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;'>"
                                "Länder</div>", unsafe_allow_html=True)
                    for _lc, _lv in _lt_sorted[:15]:
                        _lpct = _lv / _lt_total * 100
                        _lclr = _LT_CLR.get(_lc, '#546e7a')
                        _lbar = min(int(_lpct * 1.8), 100)
                        st.markdown(
                            f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:5px;'>"
                            f"<span style='color:{_lclr};font-size:0.72rem;'>●</span>"
                            f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.76rem;flex:1;'>{_lc[:20]}</span>"
                            f"<div style='background:#1a2740;border-radius:3px;width:60px;height:6px;'>"
                            f"<div style='background:{_lclr};width:{_lbar}%;height:6px;border-radius:3px;'>"
                            f"</div></div>"
                            f"<span style='color:{_C_TEXT_MUTED2};font-size:0.76rem;font-weight:600;"
                            f"min-width:38px;text-align:right;'>{_lpct:.1f}%</span></div>",
                            unsafe_allow_html=True)
                with _ltb:
                    st.markdown(f"<div style='color:{_C_ACCENT};font-size:0.72rem;font-weight:600;"
                                "letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;'>"
                                "Kontinente</div>", unsafe_allow_html=True)
                    for _co, _cv in _cont.items():
                        _cpct = _cv / _lt_total * 100
                        _cclr = _LT_CLR.get(_co, '#546e7a')
                        st.markdown(
                            f"<div style='display:flex;justify-content:space-between;"
                            f"padding:3px 0;border-bottom:1px solid #1a2740;'>"
                            f"<span style='color:{_cclr};font-size:0.78rem;'>● {_co}</span>"
                            f"<span style='color:{_C_TEXT_MUTED2};font-size:0.78rem;font-weight:600;'>"
                            f"{_cpct:.1f}%</span></div>", unsafe_allow_html=True)
                    if len(_cont) > 1:
                        _cont_fig = go.Figure(go.Pie(
                            labels=list(_cont.keys()),
                            values=list(_cont.values()),
                            hole=0.62,
                            marker=dict(
                                colors=[_LT_CLR.get(k, '#546e7a') for k in _cont],
                                line=dict(color='#0a1628', width=2)),
                            textinfo='none',
                            hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>',
                        ))
                        _cont_fig.update_layout(
                            template=_C_CHART_THEME, paper_bgcolor=_C_CHART_BG,
                            plot_bgcolor=_C_CHART_BG, showlegend=False, height=200,
                            margin=dict(l=5, r=5, t=10, b=5))
                        st.plotly_chart(_cont_fig, use_container_width=True)

                _lt_note = ""
                if _lt_etfs_found:
                    _lt_note += f"✓ Look-Through: {', '.join(_lt_etfs_found[:4])}."
                if _lt_etfs_missing:
                    _lt_note += f" ⚠️ Keine CW-Daten: {', '.join(_lt_etfs_missing[:3])} → als Sonstige."
                if _lt_note:
                    st.caption(_lt_note)

                # ── Konzentrations-Risiko ─────────────────────────────
                st.markdown("<div class='section-header'>📊 Konzentrations-Risiko</div>",
                            unsafe_allow_html=True)
                _pv = {}
                for _, _cr in df_port.iterrows():
                    _p2 = prices.get(_cr['ISIN'])
                    _pval = (_p2 * _cr['shares']) if _p2 else _cr['cost_basis']
                    _pv[_cr['ISIN']] = (_pval, _cr['name'][:32])  # ISIN als Key verhindert Name-Kollisionen
                _ptotal = sum(v for v, _ in _pv.values()) or 1
                _pshares = {nm: val / _ptotal * 100 for _, (val, nm) in _pv.items()}
                _hhi = sum(s ** 2 for s in _pshares.values())
                if   _hhi < 1500: _hhi_label, _hhi_col = "Gut diversifiziert ✓", _C_POSITIVE
                elif _hhi < 2500: _hhi_label, _hhi_col = "Moderat konzentriert", _C_NEUTRAL
                else:             _hhi_label, _hhi_col = "Hoch konzentriert ⚠️", _C_NEGATIVE
                _hc1, _hc2, _hc3 = st.columns(3)
                _hc1.metric("HHI (Herfindahl-Index)", f"{_hhi:.0f}")
                _hc2.metric("Bewertung", _hhi_label)
                _hc3.metric("Positionen gesamt", len(_pshares))
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                _top10 = sorted(_pshares.items(), key=lambda x: x[1], reverse=True)[:10]
                _warn_pos = [n for n, s in _pshares.items() if s > 20]
                if _warn_pos:
                    st.warning(f"⚠️ Hohe Einzelkonzentration (>20%): {', '.join(_warn_pos)}")
                for _pn, _ps in _top10:
                    _bar_w = int(_ps * 4)
                    _bar_c = _C_NEGATIVE if _ps > 20 else "#42a5f5" if _ps > 10 else "#546e7a"
                    st.markdown(
                        f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:5px;'>"
                        f"<div style='color:{_C_TEXT_MUTED2};font-size:0.78rem;min-width:180px;'>{_pn}</div>"
                        f"<div style='background:#1a2740;border-radius:3px;flex:1;height:8px;'>"
                        f"<div style='background:{_bar_c};width:{min(100,_bar_w)}%;height:8px;border-radius:3px;'>"
                        f"</div></div>"
                        f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.8rem;font-weight:600;min-width:40px;text-align:right;'>"
                        f"{_ps:.1f}%</div></div>",
                        unsafe_allow_html=True)
          except Exception as _e_alloc:
              st.error(f"Fehler im Aufteilung-Tab: {_e_alloc}")

        with tab_perf:
          try:
            _csv_bytes = st.session_state.get("portfolio_csv_bytes")
            if not _csv_bytes:
                st.info("📂 Lade zuerst deine Orderhistorie-CSV hoch, um die Performance zu berechnen.")
            else:
                _perf_load_key = f"perf_load_{_csv_key}"
                _irr_cache_key = f"irr_{_csv_key}"
                if _irr_cache_key in st.session_state:
                    st.session_state[_perf_load_key] = True
                if not st.session_state.get(_perf_load_key):
                    st.info(
                        "Berechnet IZF, Gesamtrendite, Steuer-Schätzung und Benchmark-Vergleich. "
                        "Lädt ~15 Sek. — danach dauerhaft gespeichert (auch nach Deploys), "
                        "bis du eine neue CSV hochlädst."
                    )
                    if st.button("📈 Performance laden", type="primary",
                                 key="btn_perf_load", use_container_width=True):
                        st.session_state[_perf_load_key] = True
                        st.rerun()
                if st.session_state.get(_perf_load_key):
                # ── Rendite-Kennzahlen ────────────────────────────────────
                    _cur_val_perf = current_total or 0.0
                    if _irr_cache_key not in st.session_state:
                        with st.spinner("Renditekennzahlen werden berechnet…"):
                            _irr_res = _calc_portfolio_irr(_csv_bytes, _cur_val_perf)
                        st.session_state[_irr_cache_key] = _irr_res
                        _pf_disk_save(f"irr_{_csv_key}", _irr_res)
                    _irr, _simple_ret, _days, _invested_total = st.session_state[_irr_cache_key]

                    _INFL = 2.2
                    _irr_pct       = _irr * 100 if _irr is not None else None
                    _simple_pct    = _simple_ret * 100 if _simple_ret is not None else None
                    # Fisher-Formel: (1+nominal)/(1+inflation)-1 (nicht simple Subtraktion)
                    _real_ret_pct  = ((1 + _irr_pct/100) / (1 + _INFL/100) - 1) * 100 if _irr_pct is not None else None
                    _years_str     = f"{_days // 365} J. {(_days % 365) // 30} M." if _days else "—"

                    def _kpi(label, value, color=None, sub=None):
                        _val_clr = color or _C_TEXT_PRIMARY
                        sub_html = f"<div style='color:{_C_TEXT_MUTED};font-size:0.72rem;margin-top:2px;'>{sub}</div>" if sub else ""
                        return (f"<div style='background:{_C_CARD_BG};border:1px solid {_C_BORDER};border-radius:10px;"
                                f"padding:14px 16px;text-align:center;'>"
                                f"<div style='color:{_C_ACCENT};font-size:0.72rem;font-weight:600;"
                                f"letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px;'>{label}</div>"
                                f"<div style='color:{_val_clr};font-size:1.4rem;font-weight:800;'>{value}</div>"
                                f"{sub_html}</div>")

                    _k1, _k2, _k3, _k4 = st.columns(4)
                    with _k1:
                        _v = f"{_irr_pct:+.2f}% p.a." if _irr_pct is not None else "—"
                        _c = _C_POSITIVE if (_irr_pct or 0) >= 0 else _C_NEGATIVE
                        st.markdown(_kpi("IZF (Zinsfuß)", _v, _c, "Interner Zinsfuß p.a."), unsafe_allow_html=True)
                    with _k2:
                        _v = f"{_simple_pct:+.1f}%" if _simple_pct is not None else "—"
                        _c = _C_POSITIVE if (_simple_pct or 0) >= 0 else _C_NEGATIVE
                        st.markdown(_kpi("Gesamtrendite", _v, _c, "auf investiertes Kapital"), unsafe_allow_html=True)
                    with _k3:
                        _v = f"{_real_ret_pct:+.2f}% p.a." if _real_ret_pct is not None else "—"
                        _c = _C_POSITIVE if (_real_ret_pct or 0) >= 0 else _C_NEGATIVE
                        st.markdown(_kpi("Realrendite", _v, _c, f"Fisher: (1+IZF)/(1+{_INFL}%)−1"), unsafe_allow_html=True)
                    with _k4:
                        st.markdown(_kpi("Anlagedauer", _years_str, _C_TEXT_PRIMARY,
                                         f"€ {_invested_total:,.0f} investiert" if _invested_total else None),
                                    unsafe_allow_html=True)

                    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

                    # ── Steuer-Schätzung ──────────────────────────────────────
                    _KEST = 0.26375
                    _FSA  = 1000.0
                    _cur_val_tax   = current_total or 0.0
                    _cost_stocks   = stocks_etf['cost_basis'].sum() if not stocks_etf.empty else 0.0
                    _cost_crypto   = crypto['cost_basis'].sum() if not crypto.empty else 0.0
                    _unrealized_g  = _cur_val_tax - (_cost_stocks + _cost_crypto)
                    _taxable_g     = max(0.0, _unrealized_g - _FSA)
                    _kest_estimate = _taxable_g * _KEST
                    _net_after_tax = _cur_val_tax - _kest_estimate
                    _clr_tax = '#ff7043' if _kest_estimate > 0 else '#546e7a'
                    st.markdown("<div class='section-header'>💶 Steuer-Schätzung (unrealisiert)</div>",
                                unsafe_allow_html=True)
                    _tx1, _tx2, _tx3, _tx4 = st.columns(4)
                    _tx1.metric("Unrealisierter Gewinn",
                                f"€ {_unrealized_g:+,.0f}" if _unrealized_g else "—")
                    _tx2.metric("Freistellungsauftrag", f"€ {_FSA:,.0f}")
                    _tx3.metric("KESt + Soli (26,375%)",
                                f"€ {_kest_estimate:,.0f}" if _kest_estimate > 0 else "€ 0")
                    _tx4.metric("Netto nach Steuer",
                                f"€ {_net_after_tax:,.0f}" if _net_after_tax else "—")
                    st.caption("⚠️ Schätzung: Aktiengewinne 26,375% (25% KESt + 5,5% Soli). "
                               "ETF-Teilfreistellung (30%) nicht berücksichtigt. Verlustverrechnung nicht einbezogen.")
                    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

                    # ── Realisierte Gewinne / Verluste ────────────────────────
                    _rpnl = _calc_realized_pnl(_csv_bytes)
                    if _rpnl and _rpnl.get('positions'):
                        st.markdown("<div class='section-header'>💰 Realisierte Gewinne & Verluste</div>",
                                    unsafe_allow_html=True)
                        _rp_total = _rpnl.get('total_pnl', 0.0)
                        _rp_sell  = _rpnl.get('total_sell_value', 0.0)
                        _rp_clr   = _C_POSITIVE if _rp_total >= 0 else _C_NEGATIVE
                        _rp1, _rp2 = st.columns(2)
                        with _rp1:
                            st.markdown(_kpi("Realisierter P&L",
                                             f"€ {_rp_total:+,.0f}", _rp_clr,
                                             "Durchschnittskostenmethode"),
                                        unsafe_allow_html=True)
                        with _rp2:
                            st.markdown(_kpi("Verkaufsvolumen",
                                             f"€ {_rp_sell:,.0f}", "#eceff1",
                                             "Bruttoerlös aller Verkäufe"),
                                        unsafe_allow_html=True)
                        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                        _rp_rows = _rpnl.get('positions', [])
                        if _rp_rows:
                            _rp_html = ("<table style='width:100%;border-collapse:collapse;"
                                        "font-size:0.82rem;'>"
                                        "<tr style='color:{_C_TEXT_MUTED};text-transform:uppercase;"
                                        "font-size:0.68rem;letter-spacing:.06em;'>"
                                        "<th style='text-align:left;padding:4px 8px;'>Position</th>"
                                        "<th style='text-align:right;padding:4px 8px;'>Anteile verkauft</th>"
                                        "<th style='text-align:right;padding:4px 8px;'>Erlös</th>"
                                        "<th style='text-align:right;padding:4px 8px;'>P&amp;L</th></tr>")
                            for _rpr in _rp_rows[:10]:
                                _pc = _C_POSITIVE if _rpr['pnl'] >= 0 else _C_NEGATIVE
                                _sg = "+" if _rpr['pnl'] >= 0 else "−"
                                _rp_html += (f"<tr style='border-top:1px solid #1a2740;'>"
                                             f"<td style='padding:5px 8px;color:{_C_TEXT_PRIMARY};'>{_rpr['name']}</td>"
                                             f"<td style='text-align:right;padding:5px 8px;color:{_C_TEXT_MUTED2};'>"
                                             f"{_rpr['shares_sold']:.2f}</td>"
                                             f"<td style='text-align:right;padding:5px 8px;color:{_C_TEXT_MUTED2};'>"
                                             f"€ {_rpr['sell_value']:,.0f}</td>"
                                             f"<td style='text-align:right;padding:5px 8px;color:{_pc};"
                                             f"font-weight:700;'>{_sg}€ {abs(_rpr['pnl']):,.0f}</td>"
                                             f"</tr>")
                            _rp_html += "</table>"
                            st.markdown(_rp_html, unsafe_allow_html=True)
                        _nc = _rpnl.get('no_cost_isins', [])
                        if _nc:
                            st.warning(f"⚠️ {len(_nc)} Verkauf/-käufe ohne Kaufdaten (evtl. Depotübertrag): P&L für diese Positionen nicht berechnet.")
                        st.caption("⚠️ Durchschnittskostenmethode (kein FIFO). Nur Trades aus der CSV. "
                                   "Ohne Dividenden, Ordergebühren und Steuern.")
                        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

                    # ── Top / Flop ────────────────────────────────────────────
                    if not stocks_etf.empty and prices:
                        _tf_rows = []
                        for _, _tfrow in stocks_etf.iterrows():
                            _p = prices.get(_tfrow['ISIN'])
                            if not _p:
                                continue
                            _cv  = _p * _tfrow['shares']
                            _pnl = (_cv - _tfrow['cost_basis']) / _tfrow['cost_basis'] * 100 if _tfrow['cost_basis'] > 0 else 0
                            _pnl_eur = _cv - _tfrow['cost_basis']
                            _tf_rows.append({'name': _tfrow['name'][:28], 'val': _cv,
                                             'pnl_pct': _pnl, 'pnl_eur': _pnl_eur})
                        if _tf_rows:
                            _tfdf = pd.DataFrame(_tf_rows).sort_values('pnl_pct', ascending=False)
                            _top3 = _tfdf.head(3)
                            _flop3 = _tfdf.tail(3).iloc[::-1]

                            st.markdown("<div class='section-header'>🏆 Top / Flop (Gesamtrendite)</div>",
                                        unsafe_allow_html=True)
                            _ta, _tb = st.columns(2)

                            def _tf_card(row):
                                _is_pos = row['pnl_pct'] >= 0
                                _clr  = _C_POSITIVE if _is_pos else _C_NEGATIVE
                                _bg   = "rgba(0,230,118,0.06)" if _is_pos else "rgba(255,82,82,0.06)"
                                return (f"<div style='background:{_bg};border:1px solid #1e2d45;"
                                        f"border-radius:8px;padding:10px 14px;margin-bottom:6px;"
                                        f"display:flex;justify-content:space-between;align-items:center;'>"
                                        f"<div><div style='color:{_C_TEXT_PRIMARY};font-size:0.88rem;font-weight:600;'>"
                                        f"{row['name']}</div>"
                                        f"<div style='color:{_C_TEXT_MUTED};font-size:0.74rem;'>€ {row['val']:,.0f}</div></div>"
                                        f"<div style='text-align:right;'>"
                                        f"<div style='color:{_clr};font-size:1rem;font-weight:800;'>"
                                        f"{row['pnl_pct']:+.1f}%</div>"
                                        f"<div style='color:{_clr};font-size:0.74rem;opacity:.8;'>"
                                        f"€ {row['pnl_eur']:+,.0f}</div></div></div>")

                            with _ta:
                                st.markdown("**Top Gewinner**")
                                for _, _r in _top3.iterrows():
                                    st.markdown(_tf_card(_r), unsafe_allow_html=True)
                            with _tb:
                                st.markdown("**Flop Verlierer**")
                                for _, _r in _flop3.iterrows():
                                    st.markdown(_tf_card(_r), unsafe_allow_html=True)

                    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

                    # ── Benchmark-Vergleich (auf Knopfdruck — verhindert Blockade beim ersten Render) ──
                    st.markdown("<div class='section-header'>📊 Benchmark-Vergleich</div>",
                                unsafe_allow_html=True)
                    _BENCHMARKS = {
                        "S&P 500 — SXR8.DE": "SXR8.DE",
                        "MSCI World — VWCE.DE": "VWCE.DE",
                        "NASDAQ 100 — EQQQ.DE": "EQQQ.DE",
                        "DAX — EXS1.DE": "EXS1.DE",
                    }
                    bm_label = st.selectbox("Benchmark auswählen", list(_BENCHMARKS.keys()), key="pf_bm_select")
                    bm_ticker = _BENCHMARKS[bm_label]
                    _bm_cache_key = f"bm_{_csv_key}_{bm_ticker}"
                    if _bm_cache_key not in st.session_state:
                        with st.spinner("Benchmark-Daten werden geladen…"):
                            st.session_state[_bm_cache_key] = _build_performance(_csv_bytes, bm_ticker)
                        _pf_disk_save(f"bm_{_csv_key}_{bm_ticker}", st.session_state[_bm_cache_key])
                    _perf = st.session_state[_bm_cache_key]
                    if _perf is None:
                        st.warning("Benchmark-Berechnung nicht möglich — CSV benötigt eine Datums-Spalte.")
                    else:
                        _dates_p, _invested_p, _bm_p = _perf
                        _pf_val_now = current_total or 0.0
                        import plotly.graph_objects as _go
                        _fig = _go.Figure()
                        _fig.add_trace(_go.Scatter(
                            x=_dates_p, y=_invested_p,
                            name="Investiert (kumuliert)",
                            line=dict(color=_C_NEUTRAL, width=2, dash="dot"),
                            fill="tozeroy", fillcolor="rgba(255,214,0,0.07)"
                        ))
                        _fig.add_trace(_go.Scatter(
                            x=_dates_p, y=_bm_p,
                            name=f"Benchmark ({bm_label})",
                            line=dict(color="#42a5f5", width=2.5),
                            fill="tozeroy", fillcolor="rgba(66,165,245,0.09)"
                        ))
                        if _pf_val_now > 0 and _dates_p:
                            _today_ts = pd.Timestamp.today().normalize()
                            _fig.add_trace(_go.Scatter(
                                x=[_dates_p[-1], _today_ts],
                                y=[_pf_val_now, _pf_val_now],
                                name="Mein Portfolio (aktuell)",
                                line=dict(color=_C_POSITIVE, width=2.5),
                                mode="lines+markers",
                                marker=dict(size=[0, 10], color=_C_POSITIVE),
                            ))
                        _fig.update_layout(
                            template=_C_CHART_THEME, height=380,
                            paper_bgcolor=_C_CHART_BG, plot_bgcolor=_C_CHART_BG,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                            margin=dict(l=10, r=10, t=36, b=10),
                            xaxis=dict(showgrid=False, title=""),
                            yaxis=dict(showgrid=True, gridcolor="#1e2d45",
                                       tickprefix="€", tickformat=",.0f"),
                            hovermode="x unified",
                        )
                        st.plotly_chart(_fig, use_container_width=True)
                        if _bm_p and _invested_p[-1] > 0:
                            _invested_last = _invested_p[-1]
                            _bm_gain_eur = _bm_p[-1] - _invested_last
                            _bm_gain_pct = (_bm_p[-1] / _invested_last - 1) * 100
                            _pf_gain_eur = _pf_val_now - _invested_last
                            _pf_gain_pct = (_pf_val_now / _invested_last - 1) * 100 if _invested_last > 0 else 0
                            _alpha = _pf_gain_pct - _bm_gain_pct
                            _sc1, _sc2, _sc3, _sc4 = st.columns(4)
                            _sc1.metric("Investiert gesamt", f"€ {_invested_last:,.0f}")
                            _sc2.metric("Mein Portfolio", f"€ {_pf_val_now:,.0f}",
                                        delta=f"{_pf_gain_pct:+.1f}% ({_pf_gain_eur:+,.0f} €)",
                                        delta_color="normal" if _pf_gain_eur >= 0 else "inverse")
                            _sc3.metric(f"Benchmark", f"€ {_bm_p[-1]:,.0f}",
                                        delta=f"{_bm_gain_pct:+.1f}% ({_bm_gain_eur:+,.0f} €)",
                                        delta_color="normal" if _bm_gain_eur >= 0 else "inverse")
                            _alpha_color = _C_POSITIVE if _alpha >= 0 else _C_NEGATIVE
                            _alpha_sign  = "+" if _alpha >= 0 else ""
                            st.markdown(
                                f"<div style='background:#0d1a2e;border:1px solid #1e2d45;border-radius:10px;"
                                f"padding:12px 16px;text-align:center;margin-top:8px;'>"
                                f"<span style='color:{_C_ACCENT};font-size:0.75rem;font-weight:600;"
                                f"text-transform:uppercase;letter-spacing:.06em;'>Portfolio vs. Benchmark (Alpha)</span>"
                                f"<div style='color:{_alpha_color};font-size:1.5rem;font-weight:800;"
                                f"margin-top:4px;'>{_alpha_sign}{_alpha:.1f} Prozentpunkte</div>"
                                f"<div style='color:{_C_TEXT_MUTED};font-size:0.72rem;margin-top:2px;'>"
                                f"{'Outperformance' if _alpha >= 0 else 'Underperformance'} gegenüber {bm_label}</div>"
                                f"</div>",
                                unsafe_allow_html=True)
                    st.caption("Methodik: Jeder Kauf simuliert einen gleichwertigen Kauf des Benchmarks. "
                               "Verkäufe reduzieren die Benchmark-Position anteilig. Kosten nicht berücksichtigt.")

          except Exception as _e_perf:
              st.error(f"Fehler im Performance-Tab: {_e_perf}")

        with tab_holdings:
          try:
            st.markdown("<div class='section-header'>🔍 Echte Unternehmens-Exposition</div>",
                        unsafe_allow_html=True)
            st.caption("ETFs werden auf ihre Top-Holdings aufgebrochen und mit Direktinvestments kombiniert. "
                       "Nur die Top-25 Holdings je ETF werden berücksichtigt (≈40–70% des ETF-Werts).")

            # ── Holdings-Breakdown (auf Knopfdruck, einmalig gecacht) ──
            _hb_load_key = f"hb_load_{_alloc_cache_key}"
            if _hb_cache_key not in st.session_state:
                if not st.session_state.get(_hb_load_key):
                    st.info("ETF Look-Through analysiert die echten Holdings deiner ETFs. "
                            "Lädt ~15–60 Sek. (je nach Anzahl ETFs), danach für diese Sitzung gespeichert.")
                    if st.button("🔍 Holdings laden", type="primary", key="btn_hb_load",
                                 use_container_width=True):
                        st.session_state[_hb_load_key] = True
                        st.rerun()
                if st.session_state.get(_hb_load_key):
                    _hb_w: dict = {}
                    _hb_etfs_w: list = []
                    for _, _hr in stocks_etf.iterrows():
                        _hisin = _hr['ISIN']
                        _htkr  = isin_map.get(_hisin, '')
                        _hinf  = _alloc_infos.get(_hisin, {})
                        if (_hinf.get('quote_type') == 'ETF' or
                                _htkr in _ETF_CW or _htkr in _ETF_SW):
                            continue
                        _hprc = prices.get(_hisin)
                        _hval = max(0.0, (_hprc if _hprc else _hr['avg_cost']) * _hr['shares'])
                        _hkey = _htkr or _hr['name']
                        if _hkey not in _hb_w:
                            _hb_w[_hkey] = {'name': _hr['name'], 'ticker': _htkr,
                                            'direct': 0.0, 'etf_eur': 0.0, 'sources': {}}
                        _hb_w[_hkey]['direct'] += _hval
                    _hb_etf_rows2 = [(isin_map.get(_hr['ISIN'], ''), _hr)
                                     for _, _hr in stocks_etf.iterrows()
                                     if ((_alloc_infos.get(_hr['ISIN'], {}).get('quote_type') == 'ETF') or
                                         isin_map.get(_hr['ISIN'], '') in _ETF_CW or
                                         isin_map.get(_hr['ISIN'], '') in _ETF_SW)
                                     and isin_map.get(_hr['ISIN'], '')]
                    if _hb_etf_rows2:
                        _hb_prog2 = st.progress(0, f"ETF-Holdings: 0 / {len(_hb_etf_rows2)}…")
                        for _hei2, (_htkr2, _hr2) in enumerate(_hb_etf_rows2):
                            _hb_prog2.progress((_hei2 + 1) / len(_hb_etf_rows2),
                                               f"ETF-Holdings: {_hei2+1}/{len(_hb_etf_rows2)} — {_hr2['name'][:28]}…")
                            _hprc2  = prices.get(_hr2['ISIN'])
                            _heval  = max(0.0, (_hprc2 if _hprc2 else _hr2['avg_cost']) * _hr2['shares'])
                            _hetf_lbl = _hr2['name'][:28]
                            _hholdings = _etf_top_holdings_cached(_htkr2)
                            if _hholdings:
                                _hb_etfs_w.append(_hetf_lbl)
                            for _hn, _hs, _hw in _hholdings:
                                _hkey2 = _hs if _hs and _hs not in ('nan', 'None') else _hn
                                _hexposure = _heval * _hw
                                if _hkey2 not in _hb_w:
                                    _hb_w[_hkey2] = {'name': _hn, 'ticker': _hs,
                                                     'direct': 0.0, 'etf_eur': 0.0, 'sources': {}}
                                _hb_w[_hkey2]['etf_eur'] += _hexposure
                                _hb_w[_hkey2]['sources'][_hetf_lbl] = \
                                    _hb_w[_hkey2]['sources'].get(_hetf_lbl, 0.0) + _hexposure
                        _hb_prog2.empty()
                    _hb_mg: dict = {}
                    for _hk, _hd in _hb_w.items():
                        _ht = (_hd['ticker'] or '').upper().split('.')[0]
                        _hm = next((k for k, d in _hb_mg.items()
                                    if _ht and (d['ticker'] or '').upper().split('.')[0] == _ht), None)
                        if _hm:
                            _hb_mg[_hm]['direct']  += _hd['direct']
                            _hb_mg[_hm]['etf_eur'] += _hd['etf_eur']
                            for _sn, _sv in _hd['sources'].items():
                                _hb_mg[_hm]['sources'][_sn] = _hb_mg[_hm]['sources'].get(_sn, 0) + _sv
                        else:
                            _hb_mg[_hk] = dict(_hd)
                    st.session_state[_hb_cache_key] = (_hb_mg, _hb_etfs_w)

            _hb_merged, _hb_etfs_loaded = st.session_state.get(_hb_cache_key, ({}, []))

            # ── Sortieren und anzeigen ──────────────────────────────────────────
            _hb_list = sorted(
                [{'key':k, **v, 'total': v['direct']+v['etf_eur']}
                 for k,v in _hb_merged.items() if v['direct']+v['etf_eur'] >= 1.0],
                key=lambda x: x['total'], reverse=True)

            if not _hb_list:
                st.info("Keine Holdings-Daten verfügbar. ETF-Daten werden per yFinance/FMP geladen.")
            else:
                _hb_grand = sum(h['total'] for h in _hb_list)
                st.markdown(f"**{len(_hb_list)} Unternehmen** · Davon mit ETF-Exposition aus "
                            f"{len(_hb_etfs_loaded)} ETF(s): "
                            f"{', '.join(_hb_etfs_loaded[:4])}{'…' if len(_hb_etfs_loaded)>4 else ''}")
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                for _rk, _hd in enumerate(_hb_list[:35], 1):
                    _pct   = _hd['total'] / _hb_grand * 100 if _hb_grand else 0
                    _bw    = min(int(_pct * 6), 100)
                    _dclr  = '#1565c0' if _hd['direct'] > 0 else '#0d47a1'
                    # Quellentext
                    _src_parts = []
                    if _hd['direct'] > 0:
                        _src_parts.append(f"<span style='color:{_C_ACCENT};'>Direkt €{_hd['direct']:,.0f}</span>")
                    for _sn, _sv in sorted(_hd['sources'].items(), key=lambda x: x[1], reverse=True)[:3]:
                        _src_parts.append(f"<span style='color:#78909c;'>{_sn[:22]} €{_sv:,.0f}</span>")
                    _src_html = " · ".join(_src_parts)
                    st.markdown(
                        f"<div style='margin-bottom:7px;padding:7px 10px;background:{_C_CARD_BG};"
                        f"border-radius:6px;border-left:3px solid {_dclr};border:1px solid {_C_BORDER};'>"
                        f"<div style='display:flex;justify-content:space-between;"
                        f"align-items:baseline;margin-bottom:3px;'>"
                        f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.82rem;font-weight:600;'>"
                        f"{_rk}. {str(_hd['name'])[:40]}</span>"
                        f"<span style='color:{_C_TEXT_MUTED2};font-size:0.76rem;'>"
                        f"€{_hd['total']:,.0f} · {_pct:.2f}%</span></div>"
                        f"<div style='background:{_C_BORDER};height:4px;border-radius:2px;margin-bottom:4px;'>"
                        f"<div style='background:{_dclr};width:{_bw}%;height:4px;"
                        f"border-radius:2px;'></div></div>"
                        f"<div style='font-size:0.68rem;'>{_src_html}</div>"
                        f"</div>",
                        unsafe_allow_html=True)
                st.caption(f"Hinweis: ETF Look-Through erfasst nur die Top-25 Holdings je ETF. "
                           f"Der Rest ({100 - sum(h['total'] for h in _hb_list if not h['sources']) / _hb_grand * 100 if _hb_grand else 0:.0f}%+ "
                           f"des ETF-Werts) ist nicht einzeln aufgeführt.")
          except Exception as _e_hb:
              st.error(f"Fehler im Holdings-Tab: {_e_hb}\n{__import__('traceback').format_exc()}")

        with tab_ki:
          try:
            st.markdown("<div class='section-header'>🤖 KI-Portfolio-Analyse</div>",
                        unsafe_allow_html=True)
            st.caption("Die KI bewertet dein Portfolio fundamental: Qualität, Bewertung, Risiken, "
                       "Zukunftsfähigkeit und gibt konkrete Handlungsempfehlungen.")

            _kipa_pk = f"ki_pf_result_{_csv_key}"
            _kipa_mk = f"ki_pf_model_{_csv_key}"
            _kipa_ts = f"ki_pf_time_{_csv_key}"

            _kipa_c1, _kipa_c2 = st.columns([5, 1])
            with _kipa_c1:
                _kipa_gen = st.button(
                    "🤖 Portfolio analysieren", type="primary",
                    use_container_width=True, key="btn_kipa_gen",
                    disabled=not GEMINI_API_KEY,
                )
            with _kipa_c2:
                _kipa_ref = st.button(
                    "🔄 Neu", use_container_width=True, key="btn_kipa_ref",
                    disabled=(_kipa_pk not in st.session_state or not GEMINI_API_KEY),
                )
            if not GEMINI_API_KEY:
                st.caption("🔑 GEMINI_API_KEY in Railway-Umgebungsvariablen eintragen.")

            if _kipa_ref:
                for _kk in [_kipa_pk, _kipa_mk, _kipa_ts]:
                    st.session_state.pop(_kk, None)
                st.rerun()

            if _kipa_gen and _kipa_pk not in st.session_state:
                # ── Portfolio-Daten für den Prompt aufbauen ──────────────────
                import datetime as _kipa_dt

                # Aktuelle Werte + Sektoren sammeln
                _kipa_rows = []
                _kipa_sectors: dict = {}
                _kipa_regions: dict = {}
                _kipa_total_val = 0.0
                for _, _kr in stocks_etf.iterrows():
                    _kp  = prices.get(_kr['ISIN'])
                    _kv  = (_kp * _kr['shares']) if _kp else _kr['cost_basis']
                    _kinf = _alloc_infos.get(_kr['ISIN'], {})
                    _ksec = (_kinf.get('sector') or
                             _ISIN_SECTOR_HARD.get(_kr['ISIN'], 'Unbekannt'))
                    _ksec_de = _SECTOR_DE.get(_ksec, _ksec) or 'Sonstige'
                    if _kinf.get('quote_type') == 'ETF':
                        _ksec_de = 'ETF/Fonds'
                    _kpnl = ((_kv - _kr['cost_basis']) / _kr['cost_basis'] * 100
                             if _kr['cost_basis'] > 0 else 0.0)
                    _kipa_rows.append({
                        'name':   _kr['name'][:40],
                        'ticker': isin_map.get(_kr['ISIN'], ''),
                        'value':  _kv,
                        'pnl':    _kpnl,
                        'sector': _ksec_de,
                        'rec':    _kinf.get('recommendation', ''),
                        'pe':     _kinf.get('forwardPE') or _kinf.get('trailingPE'),
                        'is_etf': _kinf.get('quote_type') == 'ETF',
                    })
                    _kipa_total_val += _kv
                    _kipa_sectors[_ksec_de] = _kipa_sectors.get(_ksec_de, 0) + _kv
                    _kreg = _ticker_to_region(isin_map.get(_kr['ISIN'], ''))
                    _kipa_regions[_kreg] = _kipa_regions.get(_kreg, 0) + _kv
                for _, _kr in crypto.iterrows():
                    _kp = _crypto_prices.get(_kr['ISIN'])
                    _kv = (_kp * _kr['shares']) if _kp else _kr['cost_basis']
                    _kipa_total_val += _kv
                    _kipa_sectors['Krypto'] = _kipa_sectors.get('Krypto', 0) + _kv
                    _kipa_regions['Global'] = _kipa_regions.get('Global', 0) + _kv
                    _kipa_rows.append({'name': f"₿ {_kr['name'][:35]}", 'ticker': '',
                                       'value': _kv, 'pnl': 0, 'sector': 'Krypto',
                                       'rec': '', 'pe': None, 'is_etf': False})

                # Positionen nach Wert sortieren
                _kipa_rows.sort(key=lambda r: r['value'], reverse=True)

                # Performance-Daten
                _kipa_irr, _kipa_ret, _kipa_days, _kipa_inv = _calc_portfolio_irr(
                    st.session_state.get("portfolio_csv_bytes", b""), _kipa_total_val)
                _kipa_irr_str = f"{_kipa_irr*100:+.1f}% p.a." if _kipa_irr else "n/v"
                _kipa_ret_str = f"{_kipa_ret*100:+.1f}%" if _kipa_ret else "n/v"
                _kipa_yrs = f"{_kipa_days//365} J. {(_kipa_days%365)//30} M." if _kipa_days else "n/v"

                # Prompt aufbauen
                _pos_lines = []
                for _i, _r in enumerate(_kipa_rows[:25], 1):
                    _w = _r['value'] / _kipa_total_val * 100 if _kipa_total_val else 0
                    _pe_s = f"KGV {_r['pe']:.0f}" if _r['pe'] and float(_r['pe']) < 200 else ""
                    _pnl_s = f"G/V {_r['pnl']:+.0f}%" if _r['pnl'] else ""
                    _pos_lines.append(
                        f"{_i:2}. {_r['name']:<40} {_w:5.1f}%  "
                        f"{_r['sector']:<20} {_pe_s:<10} {_pnl_s}"
                    )
                if len(_kipa_rows) > 25:
                    _pos_lines.append(f"    ... + {len(_kipa_rows)-25} weitere Positionen")

                _sec_lines = sorted(_kipa_sectors.items(), key=lambda x: x[1], reverse=True)
                _sec_str = "\n".join(
                    f"  {s:<22} {v/_kipa_total_val*100:.1f}%" for s, v in _sec_lines if _kipa_total_val)
                _reg_lines = sorted(_kipa_regions.items(), key=lambda x: x[1], reverse=True)
                _reg_str = "\n".join(
                    f"  {r:<22} {v/_kipa_total_val*100:.1f}%" for r, v in _reg_lines if _kipa_total_val)

                _pf_summary = f"""
PORTFOLIO-ÜBERSICHT:
  Gesamtwert:         € {_kipa_total_val:,.0f}
  Anzahl Positionen:  {len(_kipa_rows)}
  Laufzeit:           {_kipa_yrs}
  IZF (p.a.):         {_kipa_irr_str}
  Gesamtrendite:      {_kipa_ret_str}

TOP-POSITIONEN (sortiert nach Wert):
{chr(10).join(_pos_lines)}

SEKTORVERTEILUNG:
{_sec_str}

GEOGRAFISCHE VERTEILUNG:
{_reg_str}
"""

                _sys_kipa = (
                    "Du bist ein erfahrener Portfoliomanager und Fundamentalanalyst. "
                    "Du bewertest echte Anlegerportfolios mit der Tiefe eines professionellen "
                    "Asset Managers — ehrlich, präzise, ohne Schönfärberei. "
                    "Du kennst die Prinzipien von Buffett, Munger, Peter Lynch und modernem "
                    "Factor Investing. Antworte ausschließlich auf Deutsch. "
                    "Sei konkret: nenne echte Positionen aus dem Portfolio, gib echte Zahlen."
                )
                _usr_kipa = (
                    f"Analysiere dieses Anleger-Portfolio umfassend und fundamental:\n\n"
                    f"{_pf_summary}\n\n"
                    "Erstelle eine strukturierte Analyse mit **exakt diesen 6 Abschnitten**, "
                    "getrennt durch '---':\n\n"
                    "**🏆 PORTFOLIO-SCORE**\n"
                    "Vergib eine Note (A+ / A / B+ / B / C / D) und erkläre in 2–3 Sätzen warum. "
                    "Berücksichtige: Qualität der Unternehmen, Diversifikation, Bewertung, "
                    "Renditeentwicklung.\n\n"
                    "---\n\n"
                    "**💎 STÄRKEN**\n"
                    "Nenne 3–5 konkrete Stärken dieses Portfolios. Beziehe dich auf echte "
                    "Positionen. Was macht dieses Portfolio gut?\n\n"
                    "---\n\n"
                    "**⚠️ SCHWÄCHEN & KLUMPENRISIKEN**\n"
                    "Nenne 3–5 echte Schwächen oder Risiken. Gibt es Klumpenrisiken "
                    "(>10% in einer Position/Region/Sektor)? Fehlende Diversifikation? "
                    "Überteuerte Positionen? Sei direkt.\n\n"
                    "---\n\n"
                    "**🔮 ZUKUNFTSFÄHIGKEIT (10-Jahres-Horizont)**\n"
                    "Wie gut ist dieses Portfolio für die nächsten 10 Jahre positioniert? "
                    "Analysiere: KI/Digitalisierung-Exposure, Energiewende-Exposition, "
                    "demografische Trends, geopolitische Risiken (China, Zölle), "
                    "Währungsrisiken. Was fehlt? Was ist überexponiert?\n\n"
                    "---\n\n"
                    "**💡 KONKRETE HANDLUNGSEMPFEHLUNGEN**\n"
                    "Gib 4–6 spezifische Empfehlungen:\n"
                    "- Was würdest du aufstocken? (Begründung)\n"
                    "- Was würdest du reduzieren oder verkaufen? (Begründung)\n"
                    "- Welche 1–2 neuen Positionen fehlen für eine bessere Balance?\n"
                    "- Welche Sektoren/Regionen sind unterrepräsentiert?\n\n"
                    "---\n\n"
                    "**📊 GESAMTFAZIT**\n"
                    "Abschließende Einschätzung in 3–4 Sätzen: Wie gut wird dieses Portfolio "
                    "den MSCI World langfristig schlagen? Was ist der wichtigste Hebel zur "
                    "Verbesserung?"
                )

                with st.spinner("🤖 KI analysiert dein Portfolio fundamental…"):
                    _kipa_txt, _kipa_mdl = _try_gemini(
                        [{"role": "system", "content": _sys_kipa},
                         {"role": "user",   "content": _usr_kipa}],
                        max_tokens=8192, temperature=0.55, api_key=GEMINI_API_KEY,
                    )
                if _kipa_txt:
                    st.session_state[_kipa_pk] = _kipa_txt
                    st.session_state[_kipa_mk] = _kipa_mdl
                    st.session_state[_kipa_ts] = _kipa_dt.datetime.now().strftime("%d.%m.%Y %H:%M")
                    st.rerun()
                else:
                    st.error(f"KI-Analyse fehlgeschlagen: {_kipa_mdl}")

            # ── Ergebnis anzeigen ────────────────────────────────────────────
            if _kipa_pk in st.session_state:
                _kipa_result = st.session_state[_kipa_pk]
                _kipa_model  = st.session_state.get(_kipa_mk, "Gemini")
                _kipa_time   = st.session_state.get(_kipa_ts, "")

                import re as _kipa_re
                _kipa_blocks = [b.strip() for b in _kipa_result.split("---") if b.strip()]

                # Farb-Map für die Abschnitt-Karten
                _kipa_colors = {
                    "SCORE":      (_C_NEUTRAL, "#1a1600"),
                    "STÄRKEN":    (_C_POSITIVE, "#001a0d"),
                    "SCHWÄCHEN":  (_C_NEGATIVE, "#1a0000"),
                    "ZUKUNFT":    ("#7c4dff", "#0d0020"),
                    "HANDLUNGS":  ("#00b0ff", "#001a2e"),
                    "FAZIT":      ("#64b5f6", "#071020"),
                }

                def _kipa_card_color(block_text: str):
                    t = block_text.upper()
                    for key, colors in _kipa_colors.items():
                        if key in t:
                            return colors
                    return ("#546e7a", "#0d1a2e")

                for _kb in _kipa_blocks:
                    _bdr, _bg = _kipa_card_color(_kb)
                    st.markdown(
                        f"<div style='background:{_bg};border:1px solid {_bdr}33;"
                        f"border-left:4px solid {_bdr};border-radius:12px;"
                        f"padding:18px 22px 14px 22px;margin-bottom:12px;'>",
                        unsafe_allow_html=True)
                    st.markdown(_kb)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.caption(
                    f"Modell: {_kipa_model} · Generiert: {_kipa_time} · "
                    f"Keine Anlageberatung — Analyse basiert auf öffentlichen Portfoliodaten.")
            else:
                # Vorschau der Analysebereiche wenn noch nicht generiert
                st.markdown(
                    "<div style='background:#080f1e;border:1px solid #1a2740;border-radius:12px;"
                    "padding:20px 24px;margin-top:8px;'>"
                    "<div style='color:{_C_ACCENT};font-size:0.95rem;font-weight:700;margin-bottom:12px;'>"
                    "Die KI analysiert folgende Bereiche:</div>"
                    "<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;'>",
                    unsafe_allow_html=True)
                for _ap, _ac in [
                    ("🏆 Portfolio-Score", "Gesamtnote A+ bis F mit Begründung"),
                    ("💎 Stärken", "Konkrete Qualitätspositionen & Stärken"),
                    ("⚠️ Risiken & Klumpen", "Konzentrations- und Bewertungsrisiken"),
                    ("🔮 Zukunftsfähigkeit", "KI, Energie, Demografie, Geopolitik"),
                    ("💡 Handlungsempfehlungen", "Was kaufen, reduzieren, ergänzen"),
                    ("📊 Gesamtfazit", "MSCI-World-Vergleich & wichtigster Hebel"),
                ]:
                    st.markdown(
                        f"<div style='background:{_C_CARD_BG};border:1px solid #1a2740;"
                        f"border-radius:8px;padding:10px 12px;'>"
                        f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.85rem;font-weight:600;'>{_ap}</div>"
                        f"<div style='color:{_C_TEXT_MUTED};font-size:0.75rem;margin-top:3px;'>{_ac}</div>"
                        f"</div>",
                        unsafe_allow_html=True)
                st.markdown("</div></div>", unsafe_allow_html=True)

          except Exception as _e_ki:
              st.error(f"Fehler im KI-Analyse-Tab: {_e_ki}")

    elif df_port is None:
        st.info("📂 Bitte lade deine Orderhistorie-CSV hoch.\n\n"
                "**So exportierst du:** Finanzen.net Zero App → Aktivitäten → oben rechts ↓ Export → CSV")

    st.stop()

# ==================== ETF ANALYZER PAGE ====================
if st.session_state.get("show_etf_analyzer"):

    # ── ETF-Suchindex (ISIN / WKN / Name → Ticker) ───────────────────────
    _ETF_DB = {
        # Global
        'IE00B4L5Y983':'SXR8.DE','IE00B3RBWM25':'VWCE.DE','IE0031442068':'SXR2.DE',
        'IE00B4L5YC18':'IS3N.DE','IE00BJ0KDQ92':'XDWD.DE','IE0032895942':'EQQQ.DE',
        'DE0005933931':'EXS1.DE','LU1781541179':'LCUW.DE','IE00B0M62Q58':'IWRD.L',
        'IE00B52MJY50':'IMEA.DE','IE00B6R52259':'IQQH.DE','LU0274208692':'XDWT.DE',
        'IE00BKM4GZ66':'IS3R.DE','LU1437016972':'XMME.DE','IE00BD45KH83':'FWRA.DE',
        'IE00B6YX5C33':'SPY5.DE','IE00B3RBWM25':'VWCE.DE','IE00B8GKDB10':'VHYL.L',
        'IE00BF4RFH31':'IUSN.DE','LU0392494562':'XMWO.DE','IE00B52SFT06':'IUSE.DE',
        # Europa
        'LU1681048804':'MEUD.DE','DE0005933956':'EXW1.DE','FR0007054358':'LYPS.DE',
        'IE0031442069':'IQQY.DE','LU0322253229':'XESC.DE','IE00BKWQ0M75':'SPYY.DE',
        'IE00B4K48X80':'IEUA.DE','LU0274209233':'XEUR.DE','IE00B3ZW0K18':'IEMC.DE',
        'IE00B02KXH56':'IQQE.DE','LU0650624025':'ZPRX.DE',
        # Japan / Asien
        'IE00B4L5YX21':'EXV5.DE','LU0274209740':'XDJP.DE','IE00B02KXK85':'IQQJ.DE',
        'IE00B5VL8F07':'IQQC.DE','IE00B52SF786':'IQQD.DE','IE00B4TX3B59':'IQQP.DE',
        # Dividend
        'IE00B3F81R35':'ISPA.DE','IE00B8GKDB10':'VHYL.L','DE0002635299':'IDVY.L',
        'IE00BYYHSQ67':'QDIV.DE','LU0292096186':'XDIV.DE',
        # Themen
        'IE00B1XNHC34':'IQQH.DE','IE00BYVJRR92':'WTAI.L','IE00BKM4GZ66':'IS3R.DE',
        # WKN → ticker
        'A0RPWH':'SXR8.DE','A1JX52':'VWCE.DE','622391':'SXR2.DE','A0HGWC':'IS3N.DE',
        'DBX1MW':'XDWD.DE','A0YEDL':'EQQQ.DE','593393':'EXS1.DE','ETF127':'LCUW.DE',
        'A2PKXG':'FWRA.DE','A0MZBE':'XMME.DE','A111EG':'IS3R.DE','A1JWXY':'SPY5.DE',
        'A1T8FV':'VHYL.L','A2DWBY':'IUSN.DE','ETF091':'MEUD.DE','593395':'EXW1.DE',
        'A0YEDL':'EQQQ.DE','A0YBR5':'EXV5.DE','A1H5EU':'IQQC.DE','LYX0RT':'LYPS.DE',
        # Name → ticker
        'msci world':'SXR8.DE','msci em':'IS3N.DE','msci emerging':'IS3N.DE',
        'all world':'VWCE.DE','ftse all world':'VWCE.DE','sp500':'SXR2.DE',
        's&p 500':'SXR2.DE','nasdaq':'EQQQ.DE','nasdaq100':'EQQQ.DE','dax':'EXS1.DE',
        'amundi world':'LCUW.DE','xtrackers world':'XDWD.DE','vanguard world':'VWCE.DE',
        'eurostoxx 50':'MEUD.DE','eurostoxx50':'MEUD.DE','euro stoxx 50':'MEUD.DE',
        'stoxx 50':'MEUD.DE','stoxx europe 50':'MEUD.DE','eurostoxx':'MEUD.DE',
        'msci europe':'IQQY.DE','msci japan':'EXV5.DE','msci china':'IQQC.DE',
        'msci usa':'IUSE.DE','nasdaq 100':'EQQQ.DE','small cap':'IUSN.DE',
        'clean energy':'IQQH.DE','dividend':'VHYL.L','hochdividende':'VHYL.L',
        'ftse 100':'ISF.L','msci asia':'IQQP.DE',
    }

    @st.cache_data(ttl=3600, show_spinner=False)
    def _resolve_etf_input(raw: str) -> str:
        """ISIN / WKN / Name → Yahoo-Ticker. Fallback: raw als Ticker."""
        q = raw.strip().upper()
        ql = raw.strip().lower()
        # Direkt in DB
        if q in _ETF_DB:   return _ETF_DB[q]
        if ql in _ETF_DB:  return _ETF_DB[ql]
        # ISIN-Format (12 Zeichen, beginnt mit 2 Buchstaben)
        if len(q) == 12 and q[:2].isalpha() and q[2:].isalnum():
            try:
                resp = requests.post(
                    'https://api.openfigi.com/v3/mapping',
                    json=[{'idType': 'ID_ISIN', 'idValue': q, 'exchCode': 'GS'}],
                    timeout=5)
                if resp.ok:
                    d = resp.json()
                    if d and d[0].get('data'):
                        tkr = d[0]['data'][0].get('ticker', '')
                        if tkr:
                            return tkr + '.DE'
            except Exception:
                pass
        # WKN-Format (6 Zeichen alphanumerisch)
        if len(q) == 6 and q.isalnum() and q in _ETF_DB:
            return _ETF_DB[q]
        # Sonst: raw als Yahoo-Ticker
        return q

    # ── Statische TER-Datenbank (amtliche KIID-Werte, ändert sich kaum) ──────
    _ETF_STATIC_TER = {
        # ── Global / MSCI World ──────────────────────────────────────────────
        'SXR8.DE':0.0020,'VWCE.DE':0.0022,'SXR2.DE':0.0007,'IS3N.DE':0.0020,
        'IS3R.DE':0.0018,'XDWD.DE':0.0019,'EQQQ.DE':0.0030,'EXS1.DE':0.0016,
        'IQQH.DE':0.0065,'XMME.DE':0.0020,'IMEA.DE':0.0018,'SPY5.DE':0.0003,
        'VWRL.L':0.0022,'IWDA.AS':0.0020,'CNDX.L':0.0033,'XDWD.L':0.0020,
        'VUSA.L':0.0007,'EUNL.DE':0.0020,'DBXD.DE':0.0009,'IS3S.DE':0.0025,
        'XMEA.DE':0.0025,'IUSN.DE':0.0035,'IUSE.DE':0.0015,'VHYL.L':0.0022,
        'XMWO.DE':0.0019,'CSPX.L':0.0007,'EIMI.L':0.0018,'WSML.DE':0.0035,
        # ── Amundi (alle TER aus offiziellen KIID) ──────────────────────────
        'FWRA.DE':0.0007,   # Amundi Prime All Country World — 0,07%
        'LCUW.DE':0.0007,   # Amundi S&P 500 (swap) — 0,07%
        'SP5C.DE':0.0007,   # Amundi S&P 500 (physisch) — 0,07%
        'C500.DE':0.0025,   # Amundi PEA S&P 500 (synthetisch) — 0,25%
        'MEUD.DE':0.0015,   # Amundi EURO STOXX 50 — 0,15%
        'DAXE.DE':0.0013,   # Amundi DAX (swap) — 0,13%
        'LCUP.DE':0.0012,   # Amundi MSCI World — 0,12%
        'LYPS.DE':0.0007,   # Amundi STOXX Europe 600 — 0,07%
        'PRAW.DE':0.0005,'PRWA.DE':0.0005,'PRIW.DE':0.0007,
        'LCUQ.DE':0.0005,'LCU.DE':0.0005,'LCUA.DE':0.0005,'PRWG.DE':0.0005,
        'OBAM.DE':0.0008,
        # ── Xtrackers (alle TER aus offiziellen KIID) ───────────────────────
        'XESC.DE':0.0009,   # Xtrackers Euro Stoxx 50 — 0,09%
        'XDJP.DE':0.0015,   # Xtrackers MSCI Japan — 0,15%
        'XDIV.DE':0.0025,   # Xtrackers MSCI World High Dividend — 0,25%
        'XMKR.DE':0.0020,   # Xtrackers MSCI Korea — 0,20%
        'XMIN.DE':0.0040,   # Xtrackers MSCI India — 0,40%
        'XDWT.DE':0.0025,'XDWH.DE':0.0025,'XDWF.DE':0.0025,'XDWU.DE':0.0025,
        'XDWE.DE':0.0025,   # Xtrackers MSCI World Energy
        'XDWR.DE':0.0025,   # Xtrackers MSCI World Real Estate
        # ── iShares Sektor-ETFs (S&P 500) ───────────────────────────────────
        'QDVE.DE':0.0015,   # S&P 500 IT — 0,15%
        'QDVG.DE':0.0015,   # S&P 500 Health Care — 0,15%
        'QDVD.DE':0.0015,   # S&P 500 Financials — 0,15%
        'SXRV.DE':0.0015,   # S&P 500 Communication — 0,15%
        'SXRP.DE':0.0015,   # S&P 500 Consumer Discretionary — 0,15%
        'SXRQ.DE':0.0015,   # S&P 500 Consumer Staples — 0,15%
        'SXRS.DE':0.0015,   # S&P 500 Energy — 0,15%
        'SXRT.DE':0.0015,   # S&P 500 Industrials — 0,15%
        'SXRU.DE':0.0015,   # S&P 500 Utilities — 0,15%
        'SXRW.DE':0.0015,   # S&P 500 Materials — 0,15%
        # ── iShares MSCI World Sektor ────────────────────────────────────────
        'IUIT.DE':0.0040,   # MSCI World IT — 0,40%
        'HEAL.DE':0.0035,   # MSCI World Health — 0,35%
        # ── Faktor-ETFs ──────────────────────────────────────────────────────
        'IWQU.DE':0.0030,   # iShares MSCI World Quality — 0,30%
        'IS3Q.DE':0.0030,   # iShares Edge MSCI World Quality — 0,30%
        'IWMO.DE':0.0030,   # iShares MSCI World Momentum — 0,30%
        'MVOL.DE':0.0020,   # iShares MSCI World Min Volatility — 0,20%
        'WVAL.DE':0.0030,   # iShares MSCI World Value — 0,30%
        'IFSW.DE':0.0025,   # iShares MSCI World Size — 0,25%
        'XDEQ.DE':0.0025,   # Xtrackers MSCI World Quality — 0,25%
        'XDEM.DE':0.0025,   # Xtrackers MSCI World Momentum — 0,25%
        'XDEV.DE':0.0025,   # Xtrackers MSCI World Value — 0,25%
        'LGQG.DE':0.0025,   # L&G Global Quality ETF — 0,25%
        # ── Europa ───────────────────────────────────────────────────────────
        'EXW1.DE':0.0010,'IQQY.DE':0.0012,'SPYY.DE':0.0012,
        'IEUA.DE':0.0012,'XEUR.DE':0.0020,'IQQE.DE':0.0040,'IEMC.DE':0.0030,
        # ── Japan / Asien ────────────────────────────────────────────────────
        'EXV5.DE':0.0012,'IQQJ.DE':0.0040,
        'IQQC.DE':0.0074,'IQQD.DE':0.0061,'IQQP.DE':0.0060,
        'IS3Y.DE':0.0018,   # iShares MSCI EM ex-China — 0,18%
        # ── Dividenden-ETFs ──────────────────────────────────────────────────
        'ISPA.DE':0.0040,'QDIV.DE':0.0025,'XDIV.DE':0.0025,'IDVY.L':0.0040,
        'ZPRV.DE':0.0030,   # SPDR MSCI USA Small Cap Value — 0,30%
        'ZPRX.DE':0.0030,   # SPDR MSCI Europe Small Cap Value — 0,30%
        'EXI5.DE':0.0020,   # iShares S&P 500 Mid Cap — 0,20%
        'IS3W.DE':0.0020,   # iShares MSCI Taiwan — 0,20%
        # ── Rohstoffe / Themen ───────────────────────────────────────────────
        'IQQH.DE':0.0065,'4GLD.DE':0.0025,   # Physical Gold — 0,25%
        'PPFB.DE':0.0025,   # Invesco Physical Gold — 0,25%
        'EGLN.DE':0.0019,   # iShares Physical Gold — 0,19%
    }

    # ── US-Datenticker (für yFinance funds_data + FMP — XETRA hat kaum Daten) ─
    _ETF_DATA_TKR = {
        # ── Global / MSCI World ──────────────────────────────────────────────
        'SXR8.DE':'IVV','VWCE.DE':'VT','SXR2.DE':'IVV','IS3N.DE':'IEMG',
        'IS3R.DE':'IEMG','XDWD.DE':'URTH','EQQQ.DE':'QQQ','EXS1.DE':'EWG',
        'IQQH.DE':'ICLN','XMME.DE':'EEM','IMEA.DE':'IEMG','SPY5.DE':'SPY',
        'VWRL.L':'VT','IWDA.AS':'URTH','CNDX.L':'QQQ','VUSA.L':'IVV',
        'EUNL.DE':'URTH','IUSN.DE':'SCHA','IUSE.DE':'IVV','VHYL.L':'VYM',
        'XMWO.DE':'URTH','CSPX.L':'IVV','EIMI.L':'IEMG','WSML.DE':'SCHA',
        'DBXD.DE':'EWG',
        # ── Amundi ──────────────────────────────────────────────────────────
        'LCUW.DE':'IVV',   # Amundi S&P 500 UCITS (swap)
        'SP5C.DE':'IVV',   # Amundi S&P 500 UCITS (physisch)
        'FWRA.DE':'VT',    # Amundi Prime All Country World
        'PRAW.DE':'URTH',  # Amundi Prime Global (Developed)
        'PRWA.DE':'VT',    # Amundi Prime All Country World (Acc)
        'LCUP.DE':'URTH',  # Amundi MSCI World
        'MEUD.DE':'FEZ',   # Amundi EURO STOXX 50
        'DAXE.DE':'EWG',   # Amundi DAX
        'LYPS.DE':'VGK',   # Amundi STOXX Europe 600
        'C500.DE':'IVV',   # Amundi PEA S&P 500
        'PRIW.DE':'VT','LCUQ.DE':'URTH','LCU.DE':'IVV',
        'LCUA.DE':'URTH','PRWG.DE':'URTH','OBAM.DE':'URTH',
        # ── Xtrackers ───────────────────────────────────────────────────────
        'XESC.DE':'FEZ',   # Xtrackers Euro Stoxx 50
        'XDJP.DE':'EWJ',   # Xtrackers MSCI Japan
        'XDIV.DE':'VYM',   # Xtrackers MSCI World High Dividend
        'XMKR.DE':'EWY',   # Xtrackers MSCI Korea
        'XMIN.DE':'INDA',  # Xtrackers MSCI India
        'XDWT.DE':'IXN',   # Xtrackers MSCI World IT
        'XDWH.DE':'IXV',   # Xtrackers MSCI World Health Care
        'XDWF.DE':'IXG',   # Xtrackers MSCI World Financials
        'XDWU.DE':'XLU',   # Xtrackers MSCI World Utilities
        'XDWE.DE':'XLE',   # Xtrackers MSCI World Energy
        'XDWR.DE':'IYR',   # Xtrackers MSCI World Real Estate
        'XDEQ.DE':'QUAL',  # Xtrackers MSCI World Quality
        'XDEM.DE':'MTUM',  # Xtrackers MSCI World Momentum
        'XDEV.DE':'VLUE',  # Xtrackers MSCI World Value
        # ── iShares Sektor (S&P 500) ─────────────────────────────────────────
        'QDVE.DE':'XLK',   # S&P 500 IT
        'QDVG.DE':'XLV',   # S&P 500 Health Care
        'QDVD.DE':'XLF',   # S&P 500 Financials
        'SXRV.DE':'XLC',   # S&P 500 Communication
        'SXRP.DE':'XLY',   # S&P 500 Consumer Discretionary
        'SXRQ.DE':'XLP',   # S&P 500 Consumer Staples
        'SXRS.DE':'XLE',   # S&P 500 Energy
        'SXRT.DE':'XLI',   # S&P 500 Industrials
        'SXRU.DE':'XLU',   # S&P 500 Utilities
        'SXRW.DE':'XLB',   # S&P 500 Materials
        # ── iShares MSCI World Sektor ────────────────────────────────────────
        'IUIT.DE':'IXN',   # iShares MSCI World IT
        'HEAL.DE':'IXV',   # iShares MSCI World Health
        # ── Faktor-ETFs ──────────────────────────────────────────────────────
        'IWQU.DE':'QUAL',  # iShares MSCI World Quality Factor
        'IS3Q.DE':'QUAL',  # iShares Edge MSCI World Quality
        'IWMO.DE':'MTUM',  # iShares MSCI World Momentum Factor
        'MVOL.DE':'USMV',  # iShares MSCI World Min Volatility
        'WVAL.DE':'VLUE',  # iShares MSCI World Value Factor
        'IFSW.DE':'SIZE',  # iShares MSCI World Size Factor
        'LGQG.DE':'QUAL',  # L&G Global Quality ETF
        # ── Europa ───────────────────────────────────────────────────────────
        'EXW1.DE':'VGK','IQQY.DE':'VGK','SPYY.DE':'VGK','IEUA.DE':'VGK',
        'XEUR.DE':'VGK','IQQE.DE':'VGK','IEMC.DE':'VGK','ZPRX.DE':'EWQ',
        # ── Japan / Asien / EM ───────────────────────────────────────────────
        'EXV5.DE':'EWJ','IQQJ.DE':'EWJ',
        'IQQC.DE':'MCHI','IQQD.DE':'EEM','IQQP.DE':'EPP',
        'IS3Y.DE':'IEMG',  # iShares MSCI EM ex-China
        # ── Dividend ─────────────────────────────────────────────────────────
        'ISPA.DE':'SCHD','QDIV.DE':'VYM','XDIV.DE':'VYM','IDVY.L':'VYM',
        # ── Small/Mid Cap ────────────────────────────────────────────────────
        'ZPRV.DE':'IWN',   # SPDR MSCI USA Small Cap Value
        'EXI5.DE':'IJH',   # iShares S&P 500 Mid Cap
        # ── EM Spezifisch ────────────────────────────────────────────────────
        'IS3W.DE':'EWT',   # iShares MSCI Taiwan
    }

    # ── Statische AUM-Werte (Näherung EUR, Stand 2025) ──────────────────────
    _ETF_STATIC_AUM = {
        # ── Große Flaggschiffe ───────────────────────────────────────────────
        'SXR8.DE': 90_000_000_000,   # iShares Core S&P 500
        'EUNL.DE': 70_000_000_000,   # iShares Core MSCI World
        'IWDA.AS': 65_000_000_000,   # iShares Core MSCI World (Amsterdam)
        'SPY5.DE': 40_000_000_000,   # SPDR S&P 500
        'CSPX.L':  60_000_000_000,   # iShares Core S&P 500 (LSE)
        'EQQQ.DE': 22_000_000_000,   # iShares Nasdaq-100
        'VWCE.DE': 20_000_000_000,   # Vanguard FTSE All-World (Acc)
        'VWRL.L':  18_000_000_000,   # Vanguard FTSE All-World (GBP)
        'IS3N.DE': 14_000_000_000,   # iShares Core MSCI EM IMI
        'XDWD.DE': 12_000_000_000,   # Xtrackers MSCI World Swap
        'EXS1.DE': 18_000_000_000,   # iShares Core DAX
        # ── Amundi ──────────────────────────────────────────────────────────
        'LCUW.DE':  7_000_000_000,   # Amundi S&P 500 UCITS (swap)
        'SP5C.DE':  8_000_000_000,   # Amundi S&P 500 UCITS (physisch)
        'FWRA.DE':  4_000_000_000,   # Amundi Prime All Country World
        'PRAW.DE':  2_000_000_000,   # Amundi Prime Global (Developed)
        'PRWA.DE':    800_000_000,   # Amundi Prime All Country World (thes.)
        'LCUP.DE':  2_500_000_000,   # Amundi MSCI World
        'MEUD.DE':  3_000_000_000,   # Amundi EURO STOXX 50
        'DAXE.DE':  1_200_000_000,   # Amundi DAX UCITS
        'LYPS.DE':  2_000_000_000,   # Amundi STOXX Europe 600
        'C500.DE':    700_000_000,   # Amundi PEA S&P 500
        # ── Xtrackers ───────────────────────────────────────────────────────
        'XMWO.DE':  3_500_000_000,   # Xtrackers MSCI World Swap 1C
        'XESC.DE':  2_500_000_000,   # Xtrackers Euro Stoxx 50
        'XMME.DE':  3_000_000_000,   # Xtrackers MSCI EM Swap
        'XDWT.DE':  6_000_000_000,   # Xtrackers MSCI World IT
        'XDWH.DE':  1_200_000_000,   # Xtrackers MSCI World Health Care
        'XDWF.DE':    600_000_000,   # Xtrackers MSCI World Financials
        'XDIV.DE':  2_200_000_000,   # Xtrackers MSCI World High Dividend
        'XDJP.DE':  1_500_000_000,   # Xtrackers MSCI Japan Swap
        'XMIN.DE':  1_000_000_000,   # Xtrackers MSCI India
        'XMKR.DE':    500_000_000,   # Xtrackers MSCI Korea
        'DBXD.DE':  3_000_000_000,   # Xtrackers DAX
        # ── iShares Sektor & Faktor ──────────────────────────────────────────
        'QDVE.DE':  3_000_000_000,   # iShares S&P 500 IT
        'QDVG.DE':  1_200_000_000,   # iShares S&P 500 Health Care
        'QDVD.DE':    600_000_000,   # iShares S&P 500 Financials
        'SXRV.DE':    500_000_000,   # iShares S&P 500 Communication
        'IUIT.DE':  3_500_000_000,   # iShares MSCI World IT
        'HEAL.DE':  1_500_000_000,   # iShares MSCI World Health
        'IWQU.DE':  3_000_000_000,   # iShares MSCI World Quality
        'IWMO.DE':  2_000_000_000,   # iShares MSCI World Momentum
        'MVOL.DE':  4_000_000_000,   # iShares MSCI World Min Volatility
        'WVAL.DE':    800_000_000,   # iShares MSCI World Value
        'WSML.DE':  2_000_000_000,   # iShares MSCI World Small Cap
        'IQQH.DE':  1_500_000_000,   # iShares Global Clean Energy
        'IQQY.DE':  2_000_000_000,   # iShares MSCI Europe
        'IQQC.DE':  1_200_000_000,   # iShares MSCI China
        # ── Sonstige ────────────────────────────────────────────────────────
        'EXW1.DE':  3_500_000_000,   # iShares STOXX Europe 600
        'IUSN.DE':  2_000_000_000,   # iShares MSCI World Small Cap
        'ISPA.DE':  8_000_000_000,   # iShares STOXX Global Select Div
        'ZPRV.DE':    500_000_000,   # SPDR MSCI USA Small Cap Value
        'ZPRX.DE':    400_000_000,   # SPDR MSCI Europe Small Cap Value
        'EXV5.DE':  1_000_000_000,   # iShares Core MSCI Japan
        'IS3W.DE':    800_000_000,   # iShares MSCI Taiwan
        'VUSA.L':   8_000_000_000,   # Vanguard S&P 500 (GBP)
        'VHYL.L':   3_000_000_000,   # Vanguard FTSE All-World High Div
    }

    # ── Statische Länder-Gewichtungen (Quelle: Fondsanbieter, Stand 2024) ────
    _ETF_STATIC_CW = {
        # MSCI All-World / Developed World
        'VWCE.DE': {'USA':62.5,'Japan':5.7,'UK':3.8,'Frankreich':3.1,'Kanada':2.9,
                    'Schweiz':2.6,'Deutschland':2.5,'Australien':2.1,'Indien':1.8,
                    'Taiwan':1.8,'Südkorea':1.6,'Niederlande':1.2,'Sonstige':7.4},
        'FWRA.DE': {'USA':62.5,'Japan':5.7,'UK':3.8,'Frankreich':3.1,'Kanada':2.9,
                    'Schweiz':2.6,'Deutschland':2.5,'Australien':2.1,'Indien':1.8,
                    'Taiwan':1.8,'Südkorea':1.6,'Niederlande':1.2,'Sonstige':7.4},
        'VWRL.L':  {'USA':62.5,'Japan':5.7,'UK':3.8,'Frankreich':3.1,'Kanada':2.9,
                    'Schweiz':2.6,'Deutschland':2.5,'Australien':2.1,'Indien':1.8,
                    'Taiwan':1.8,'Südkorea':1.6,'Niederlande':1.2,'Sonstige':7.4},
        'SXR8.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                    'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
        'XDWD.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                    'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
        'EUNL.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                    'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
        'XMWO.DE': {'USA':69.0,'Japan':6.2,'UK':4.4,'Frankreich':3.4,'Kanada':3.1,
                    'Schweiz':2.8,'Deutschland':2.8,'Australien':2.0,'Niederlande':1.4,'Sonstige':4.9},
        # S&P 500 / USA
        'SXR2.DE': {'USA':100.0},
        'IUSE.DE': {'USA':100.0},
        'LCUW.DE': {'USA':100.0},
        'VUSA.L':  {'USA':100.0},
        'SPY5.DE': {'USA':100.0},
        'CSPX.L':  {'USA':100.0},
        # NASDAQ-100
        'EQQQ.DE': {'USA':97.0,'Sonstige':3.0},
        'CNDX.L':  {'USA':97.0,'Sonstige':3.0},
        # EuroStoxx 50
        'EXW1.DE': {'Deutschland':17.2,'Frankreich':16.8,'Niederlande':14.2,'Spanien':9.5,
                    'Italien':8.5,'Belgien':4.8,'Finnland':4.2,'Irland':3.5,'Sonstige':21.3},
        'MEUD.DE': {'Deutschland':17.2,'Frankreich':16.8,'Niederlande':14.2,'Spanien':9.5,
                    'Italien':8.5,'Belgien':4.8,'Finnland':4.2,'Irland':3.5,'Sonstige':21.3},
        'LYPS.DE': {'Deutschland':17.2,'Frankreich':16.8,'Niederlande':14.2,'Spanien':9.5,
                    'Italien':8.5,'Belgien':4.8,'Finnland':4.2,'Irland':3.5,'Sonstige':21.3},
        # MSCI Europe
        'IQQY.DE': {'UK':23.8,'Frankreich':17.0,'Schweiz':13.5,'Deutschland':12.8,
                    'Niederlande':8.2,'Schweden':5.3,'Dänemark':4.1,'Spanien':3.5,
                    'Italien':3.0,'Sonstige':8.8},
        'IEUA.DE': {'UK':23.8,'Frankreich':17.0,'Schweiz':13.5,'Deutschland':12.8,
                    'Niederlande':8.2,'Schweden':5.3,'Dänemark':4.1,'Spanien':3.5,
                    'Italien':3.0,'Sonstige':8.8},
        # DAX
        'EXS1.DE': {'Deutschland':100.0},
        'DBXD.DE': {'Deutschland':100.0},
        # Japan
        'EXV5.DE': {'Japan':100.0},
        'XDJP.DE': {'Japan':100.0},
        # China
        'IQQC.DE': {'China':100.0},
        # MSCI EM
        'IS3N.DE': {'China':26.8,'Indien':14.2,'Taiwan':17.1,'Südkorea':12.3,
                    'Brasilien':5.1,'Saudi-Arabien':4.0,'Südafrika':3.5,
                    'Mexiko':2.5,'Indonesien':1.6,'Sonstige':12.9},
        'IS3R.DE': {'China':26.8,'Indien':14.2,'Taiwan':17.1,'Südkorea':12.3,
                    'Brasilien':5.1,'Saudi-Arabien':4.0,'Südafrika':3.5,
                    'Mexiko':2.5,'Indonesien':1.6,'Sonstige':12.9},
        'XMME.DE': {'China':26.8,'Indien':14.2,'Taiwan':17.1,'Südkorea':12.3,
                    'Brasilien':5.1,'Saudi-Arabien':4.0,'Südafrika':3.5,
                    'Mexiko':2.5,'Indonesien':1.6,'Sonstige':12.9},
        # Dividend
        'VHYL.L':  {'USA':60.2,'UK':7.1,'Japan':6.0,'Schweiz':4.2,'Frankreich':3.5,
                    'Deutschland':3.0,'Australien':2.8,'Sonstige':13.2},
        'ISPA.DE': {'USA':54.0,'Kanada':8.0,'UK':6.0,'Japan':5.5,'Schweiz':4.0,
                    'Frankreich':3.5,'Deutschland':3.0,'Australien':2.5,'Sonstige':13.5},
    }

    # ── Kontinent-Zuordnung ────────────────────────────────────────────────
    _CONTINENT = {
        'USA':'Nordamerika','Kanada':'Nordamerika','Mexiko':'Nordamerika',
        'UK':'Europa','Deutschland':'Europa','Frankreich':'Europa','Schweiz':'Europa',
        'Niederlande':'Europa','Schweden':'Europa','Dänemark':'Europa','Spanien':'Europa',
        'Italien':'Europa','Belgien':'Europa','Norwegen':'Europa','Finnland':'Europa',
        'Irland':'Europa','Österreich':'Europa','Polen':'Europa','Portugal':'Europa',
        'Japan':'Asien/Pazifik','China':'Asien/Pazifik','Südkorea':'Asien/Pazifik',
        'Taiwan':'Asien/Pazifik','Australien':'Asien/Pazifik','Indien':'Asien/Pazifik',
        'Hongkong':'Asien/Pazifik','Singapur':'Asien/Pazifik','Indonesien':'Asien/Pazifik',
        'Malaysia':'Asien/Pazifik','Thailand':'Asien/Pazifik','Philippinen':'Asien/Pazifik',
        'Brasilien':'Lateinamerika','Chile':'Lateinamerika','Kolumbien':'Lateinamerika',
        'Peru':'Lateinamerika','Argentinien':'Lateinamerika',
        'Saudi-Arabien':'Mittlerer Osten','Israel':'Mittlerer Osten','VAE':'Mittlerer Osten',
        'Katar':'Mittlerer Osten','Kuwait':'Mittlerer Osten',
        'Südafrika':'Afrika','Ägypten':'Afrika','Nigeria':'Afrika',
    }

    # ── Suchdatenbank für Live-Vorschläge (Ticker, Name, ISIN, WKN, TER-Text) ─
    _ETF_SEARCH_DB = [
        # Global
        ('SXR8.DE', 'iShares Core MSCI World UCITS',        'IE00B4L5Y983','A0RPWH', '0,20%'),
        ('VWCE.DE', 'Vanguard FTSE All-World UCITS Acc',     'IE00B3RBWM25','A1JX52', '0,22%'),
        ('SXR2.DE', 'iShares Core S&P 500 UCITS',            'IE0031442068','622391', '0,07%'),
        ('IS3N.DE', 'iShares Core MSCI EM IMI UCITS',        'IE00B4L5YC18','A0HGWC', '0,20%'),
        ('XDWD.DE', 'Xtrackers MSCI World Swap UCITS',       'IE00BJ0KDQ92','DBX1MW', '0,20%'),
        ('EQQQ.DE', 'Invesco NASDAQ-100 UCITS',              'IE0032895942','A0YEDL', '0,30%'),
        ('EXS1.DE', 'iShares Core DAX UCITS',                'DE0005933931','593393', '0,16%'),
        ('LCUW.DE', 'Amundi MSCI World UCITS',               'LU1781541179','ETF127', '0,12%'),
        ('FWRA.DE', 'Invesco FTSE All-World UCITS Acc',      'IE00BD45KH83','A2PKXG', '0,15%'),
        ('SPY5.DE', 'SPDR S&P 500 UCITS',                   'IE00B6YX5C33','A1JWXY', '0,03%'),
        ('VHYL.L',  'Vanguard FTSE All-World High Dividend', 'IE00B8GKDB10','A1T8FV', '0,22%'),
        ('IUSN.DE', 'iShares MSCI World Small Cap UCITS',    'IE00BF4RFH31','A2DWBY', '0,35%'),
        ('IUSE.DE', 'iShares MSCI USA UCITS',                'IE00B52SFT06','A1CL19', '0,15%'),
        ('IWRD.L',  'iShares MSCI World UCITS (USD Dist)',   'IE00B0M62Q58','A0HGV5', '0,50%'),
        ('XMWO.DE', 'Xtrackers MSCI World Swap UCITS 1C',   'LU0392494562','DBX1ME', '0,19%'),
        # Europa
        ('MEUD.DE', 'Amundi EURO STOXX 50 UCITS',           'LU1681048804','ETF091', '0,15%'),
        ('EXW1.DE', 'iShares Core EURO STOXX 50 UCITS',     'DE0005933956','593395', '0,10%'),
        ('LYPS.DE', 'Lyxor Core EURO STOXX 50 DR UCITS',    'FR0007054358','LYX0RT', '0,07%'),
        ('IQQY.DE', 'iShares MSCI Europe UCITS',             'IE0031442069','A0HGWC', '0,12%'),
        ('XESC.DE', 'Xtrackers Euro Stoxx 50 UCITS',        'LU0322253229','DBX1ME', '0,09%'),
        ('SPYY.DE', 'SPDR MSCI Europe UCITS',               'IE00BKWQ0M75','A2H9Q5', '0,12%'),
        ('IEUA.DE', 'iShares Core MSCI Europe UCITS',        'IE00B4K48X80','A0YEDG', '0,12%'),
        ('IQQE.DE', 'iShares STOXX Europe 600 UCITS',        'IE00B02KXH56','263528', '0,20%'),
        # Japan / Asien
        ('EXV5.DE', 'iShares Core MSCI Japan IMI UCITS',    'IE00B4L5YX21','A0YBR5', '0,12%'),
        ('XDJP.DE', 'Xtrackers MSCI Japan Swap UCITS',      'LU0274209740','DBX1MJ', '0,15%'),
        ('IQQC.DE', 'iShares MSCI China UCITS',              'IE00B5VL8F07','A1H5EU', '0,74%'),
        ('IQQP.DE', 'iShares MSCI AC Far East ex-Japan',    'IE00B4TX3B59','A0YEDJ', '0,74%'),
        # Dividend
        ('ISPA.DE', 'iShares STOXX Europe Select Div 30',   'IE00B3F81R35','A0H0744','0,40%'),
        ('QDIV.DE', 'iShares MSCI World Quality Div UCITS', 'IE00BYYHSQ67','A2DWBY', '0,38%'),
        ('IDVY.L',  'iShares Euro Dividend UCITS',           'DE0002635299','263529', '0,40%'),
        # Themen
        ('IQQH.DE', 'iShares Global Clean Energy UCITS',    'IE00B1XNHC34','A0MZBE', '0,65%'),
        ('XMME.DE', 'Xtrackers MSCI EM Swap UCITS',         'LU1437016972','A2H9GB', '0,20%'),
    ]

    @st.cache_data(ttl=3600, show_spinner=False)
    def _etf_perf_hist(ticker: str) -> dict:
        """Berechnet YTD / 3J / 5J aus Kurshistorie (zuverlässig für XETRA-ETFs)."""
        import datetime as _dtt
        try:
            raw = yf.download(ticker, period='6y', interval='1mo',
                              progress=False, auto_adjust=True)
            if raw.empty:
                return {}
            cl = raw['Close']
            if isinstance(cl, pd.DataFrame):
                cl = cl.iloc[:, 0]
            cl = cl.dropna()
            if cl.empty:
                return {}
            now_ts  = cl.index[-1]
            last_px = float(cl.iloc[-1])
            # Timezone-aware index handling
            tz = getattr(now_ts, 'tzinfo', None)
            def _ts(dt):
                return pd.Timestamp(dt, tz=tz) if tz else pd.Timestamp(dt)
            # YTD
            ytd_start = _ts(_dtt.date(now_ts.year, 1, 1))
            ytd_cl    = cl[cl.index >= ytd_start]
            ytd = (last_px / float(ytd_cl.iloc[0]) - 1) if len(ytd_cl) > 0 else None
            # 1Y simple
            cl_1y = cl[cl.index >= _ts(now_ts - _dtt.timedelta(days=370))]
            r1y   = (last_px / float(cl_1y.iloc[0]) - 1) if len(cl_1y) > 6 else None
            # 3Y annualized
            cl_3y = cl[cl.index >= _ts(now_ts - _dtt.timedelta(days=3*365+10))]
            r3y   = ((last_px / float(cl_3y.iloc[0])) ** (1/3) - 1) if len(cl_3y) > 18 else None
            # 5Y annualized
            cl_5y = cl[cl.index >= _ts(now_ts - _dtt.timedelta(days=5*365+15))]
            r5y   = ((last_px / float(cl_5y.iloc[0])) ** (1/5) - 1) if len(cl_5y) > 36 else None
            return {'ytd': ytd, 'ret_1y': r1y, 'ret_3y': r3y, 'ret_5y': r5y}
        except Exception:
            return {}

    @st.cache_data(ttl=3600, show_spinner=False)
    def _etf_perf_hist(ticker: str) -> dict:
        """Berechnet YTD / 3J / 5J aus Kurshistorie (zuverlässig für XETRA-ETFs)."""
        import datetime as _dtt
        try:
            raw = yf.download(ticker, period='6y', interval='1mo',
                              progress=False, auto_adjust=True)
            if raw.empty:
                return {}
            cl = raw['Close']
            if isinstance(cl, pd.DataFrame):
                cl = cl.iloc[:, 0]
            cl = cl.dropna()
            if cl.empty:
                return {}
            now_ts  = cl.index[-1]
            last_px = float(cl.iloc[-1])
            # Timezone-aware index handling
            tz = getattr(now_ts, 'tzinfo', None)
            def _ts(dt):
                return pd.Timestamp(dt, tz=tz) if tz else pd.Timestamp(dt)
            # YTD
            ytd_start = _ts(_dtt.date(now_ts.year, 1, 1))
            ytd_cl    = cl[cl.index >= ytd_start]
            ytd = (last_px / float(ytd_cl.iloc[0]) - 1) if len(ytd_cl) > 0 else None
            # 1Y simple
            cl_1y = cl[cl.index >= _ts(now_ts - _dtt.timedelta(days=370))]
            r1y   = (last_px / float(cl_1y.iloc[0]) - 1) if len(cl_1y) > 6 else None
            # 3Y annualized
            cl_3y = cl[cl.index >= _ts(now_ts - _dtt.timedelta(days=3*365+10))]
            r3y   = ((last_px / float(cl_3y.iloc[0])) ** (1/3) - 1) if len(cl_3y) > 18 else None
            # 5Y annualized
            cl_5y = cl[cl.index >= _ts(now_ts - _dtt.timedelta(days=5*365+15))]
            r5y   = ((last_px / float(cl_5y.iloc[0])) ** (1/5) - 1) if len(cl_5y) > 36 else None
            return {'ytd': ytd, 'ret_1y': r1y, 'ret_3y': r3y, 'ret_5y': r5y}
        except Exception:
            return {}

    _ETF_STATIC_DESC: dict = {
        # ── Welt-ETFs ────────────────────────────────────────────────────────
        'XDWD.DE':  "Synthetischer ETF auf den MSCI World Index mit ca. 1.500 Unternehmen aus 23 Industrieländern. Swap-basierte Replikation (Deutsche Bank). Schwerpunkt USA (~69%), Japan, UK und Frankreich.",
        'EUNL.DE':  "Physischer ETF auf den MSCI World Index mit über 1.500 Unternehmen. Einer der größten MSCI-World-ETFs in Europa mit ~€70 Mrd. Fondsvolumen. USA-Anteil ca. 70%, thesaurierend.",
        'XMWO.DE':  "Physischer MSCI World UCITS ETF mit Vollreplikation. Breite Diversifikation über 23 Industrieländer, ca. 1.500 Titel. USA dominiert mit ~70% Gewicht.",
        'IWDA.AS':  "iShares Core MSCI World UCITS ETF — einer der meistgehandelten Welt-ETFs, notiert in Amsterdam. Über 1.500 Unternehmen, physische Replikation, thesaurierend.",
        'PRAW.DE':  "Amundi Prime Global UCITS ETF — extrem kostengünstiger ETF (TER 0,05%) auf den Solactive GBS Global Markets Developed Large & Mid Cap Index. Physische Replikation.",
        'PRWA.DE':  "Amundi Prime Global UCITS ETF — extrem kostengünstiger ETF (TER 0,05%) auf den Solactive GBS Global Markets Developed Large & Mid Cap Index. Physische Replikation.",
        # ── All Country / ACWI ───────────────────────────────────────────────
        'VWCE.DE':  "Vanguard FTSE All-World UCITS ETF mit ca. 3.700 Unternehmen aus Industrie- und Schwellenländern. Physische Vollreplikation des FTSE All-World Index. USA ~62%, thesaurierend.",
        'FWRA.DE':  "Amundi Prime All Country World UCITS ETF (TER 0,05%) auf den Solactive GBS Global Markets All Cap Index mit >3.700 Titeln aus Industrie- und Schwellenländern. Physische Replikation, thesaurierend.",
        'VWRL.L':   "Vanguard FTSE All-World UCITS ETF in GBP, ausschüttend. Ca. 3.700 Unternehmen global, USA ~62%. Günstige TER von 0,22% und sehr hohe Liquidität.",
        # ── S&P 500 ───────────────────────────────────────────────────────────
        'SXR8.DE':  "iShares Core S&P 500 UCITS ETF — repliziert die 500 größten US-Unternehmen. Einer der liquidesten ETFs in Europa mit >€90 Mrd. Fondsvolumen. Physisch, thesaurierend.",
        'LCUW.DE':  "Amundi S&P 500 UCITS ETF (TER 0,07%) — synthetische Replikation des S&P 500 Index. Kostengünstigste Alternative zu SXR8.DE mit vergleichbarer Performance.",
        'SPY5.DE':  "SPDR S&P 500 UCITS ETF — europäische Version des weltweit größten ETFs. Physische Replikation der 500 größten US-Unternehmen. Sehr hohe Liquidität.",
        'IUSE.DE':  "iShares S&P 500 EUR Hedged UCITS ETF — repliziert den S&P 500 mit Währungsabsicherung gegen EUR/USD-Risiko. Geeignet für EUR-Anleger mit kurzfristigem Fokus.",
        'CSPX.L':   "iShares Core S&P 500 UCITS ETF in USD (LSE). Physische Replikation des S&P 500 mit über 500 US-Großunternehmen. Thesaurierend.",
        'VUSA.L':   "Vanguard S&P 500 UCITS ETF in USD (LSE). Physische Vollreplikation, thesaurierend. TER 0,07%.",
        # ── Nasdaq-100 ───────────────────────────────────────────────────────
        'EQQQ.DE':  "iShares Nasdaq-100 UCITS ETF — bildet die 100 größten Nicht-Finanzwerte des Nasdaq ab. ~55% IT-Sektor-Konzentration. Physische Replikation, thesaurierend.",
        'CNDX.L':   "iShares Nasdaq-100 UCITS ETF in USD (LSE). Physische Replikation der 100 größten Nasdaq-Unternehmen. Starke Technologieausrichtung mit Apple, Microsoft, NVIDIA an der Spitze.",
        # ── Schwellenländer ───────────────────────────────────────────────────
        'IS3N.DE':  "iShares Core MSCI Emerging Markets IMI UCITS ETF mit >1.400 Titeln aus Schwellenländern. China ~30%, Indien ~18%, Taiwan ~17%. Physische Replikation.",
        'XMME.DE':  "Xtrackers MSCI Emerging Markets Swap UCITS ETF — synthetische Replikation von ~1.400 EM-Aktien. China, Taiwan, Indien als Hauptmärkte.",
        # ── Europa ───────────────────────────────────────────────────────────
        'EXS1.DE':  "iShares Core DAX UCITS ETF — repliziert die 40 größten deutschen Aktien (DAX). Physische Vollreplikation, ausschüttend. Konzentration auf Industrie, Chemie und Finanzwerte.",
        'MEUD.DE':  "Lyxor Core STOXX Europe 600 UCITS ETF — abdeckt ca. 600 europäische Unternehmen. Synthetische Replikation, sehr günstige TER von 0,07%.",
        'EXW1.DE':  "iShares STOXX Europe 600 UCITS ETF — ca. 600 Unternehmen aus 17 europäischen Ländern. Physische Replikation, ausschüttend.",
        # ── Dividenden-ETFs ───────────────────────────────────────────────────
        'ISPA.DE':  "iShares STOXX Global Select Dividend 100 UCITS ETF mit den 100 dividendenstärksten Aktien weltweit. Hohe Ausschüttungsrendite (~4%), ausschüttend.",
        'QDIV.DE':  "iShares MSCI World Quality Dividend UCITS ETF — kombiniert Dividendenstärke mit Qualitätskriterien. Ca. 400 Unternehmen, ausschüttend.",
        'XDIV.DE':  "Xtrackers MSCI World High Dividend Yield UCITS ETF mit ca. 400 dividendenstarken Unternehmen weltweit. Synthetische Replikation.",
        # ── Sektor-ETFs ───────────────────────────────────────────────────────
        'XDWT.DE':  "Xtrackers MSCI World Information Technology UCITS ETF — 100% IT-Sektor, ca. 250 Unternehmen. Apple, Microsoft und NVIDIA als Hauptpositionen.",
        'QDVE.DE':  "iShares S&P 500 Information Technology Sector UCITS ETF — US-IT-Giganten wie Apple, Microsoft, NVIDIA. Stark konzentriert auf wenige Mega-Caps.",
        'XDWH.DE':  "Xtrackers MSCI World Health Care UCITS ETF — globale Pharmaunternehmen, Medizintechnik und Biotech. J&J, UnitedHealth, Eli Lilly als Hauptpositionen.",
        'IQQH.DE':  "iShares Global Clean Energy UCITS ETF mit ca. 100 Unternehmen aus erneuerbarer Energie. Windkraft, Solar, Wasserstoff. Hohe Volatilität.",
        # ── Amundi (erweitert) ────────────────────────────────────────────────
        'SP5C.DE':  "Amundi S&P 500 UCITS ETF (TER 0,07%) — physische Replikation des S&P 500 mit 500 US-Unternehmen. Günstiger Einstieg in den amerikanischen Aktienmarkt ohne Währungshedging.",
        'LCUP.DE':  "Amundi MSCI World UCITS ETF (TER 0,12%) — physische Replikation von ca. 1.500 Unternehmen aus 23 Industrieländern. Gutes Preis-Leistungs-Verhältnis für ein MSCI-World-Basisinvestment.",
        'MEUD.DE':  "Amundi EURO STOXX 50 UCITS ETF (TER 0,15%) — die 50 größten Unternehmen der Eurozone. Synthetische Replikation, hohe Liquidität. Enthält LVMH, SAP, ASML, TotalEnergies.",
        'DAXE.DE':  "Amundi DAX UCITS ETF (TER 0,13%) — synthetische Replikation des DAX 40. Fokus auf deutsche Blue Chips: SAP, Siemens, Allianz, BASF. Für gezielte Deutschland-Exposition.",
        'LYPS.DE':  "Amundi STOXX Europe 600 UCITS ETF (TER 0,07%) — breite europäische Abdeckung mit 600 Unternehmen aus 17 Ländern. Sehr günstig und diversifiziert.",
        'C500.DE':  "Amundi ETF PEA S&P 500 UCITS (TER 0,25%) — synthetisch replizierter S&P 500 für französische PEA-Konten. Für deutsche Anleger weniger relevant.",
        # ── Xtrackers (erweitert) ─────────────────────────────────────────────
        'XESC.DE':  "Xtrackers Euro Stoxx 50 UCITS ETF (TER 0,09%) — sehr günstige swap-basierte Replikation der 50 größten Eurozone-Unternehmen. Hohe Liquidität, ausschüttend.",
        'XDJP.DE':  "Xtrackers MSCI Japan Swap UCITS ETF (TER 0,15%) — Zugang zum japanischen Aktienmarkt über ~300 Unternehmen. Toyota, Sony, Keyence als Top-Positionen. Währungsrisiko JPY/EUR.",
        'XMME.DE':  "Xtrackers MSCI Emerging Markets Swap UCITS ETF (TER 0,20%) — synthetische EM-Abdeckung mit ~1.400 Titeln. China, Taiwan, Indien dominieren. Günstigere Alternative zu IS3N.DE.",
        'XDIV.DE':  "Xtrackers MSCI World High Dividend Yield UCITS ETF (TER 0,25%) — ca. 400 dividendenstarke Aktien weltweit. Ausgewogene Mischung aus Dividendenstärke und Qualität.",
        'XDWF.DE':  "Xtrackers MSCI World Financials UCITS ETF (TER 0,25%) — Banken, Versicherungen und Finanzdienstleister weltweit. JPMorgan, Berkshire, Visa als Top-Positionen.",
        'XDWU.DE':  "Xtrackers MSCI World Utilities UCITS ETF (TER 0,25%) — defensive Versorger weltweit. Nextera Energy, Enel, National Grid. Geringe Korrelation zum Gesamtmarkt.",
        'DBXD.DE':  "Xtrackers DAX UCITS ETF (TER 0,09%) — günstige swap-basierte Replikation des DAX 40. Einer der ältesten deutschen ETFs, sehr hohe Liquidität.",
        'XMWO.DE':  "Xtrackers MSCI World Swap UCITS ETF (TER 0,19%) — swap-basierte Replikation von ~1.500 Unternehmen aus 23 Industrieländern. Steuerlich vorteilhaft durch Swap-Struktur.",
        'XMIN.DE':  "Xtrackers MSCI India Swap UCITS ETF (TER 0,40%) — Zugang zum indischen Aktienmarkt via Swap. Reliance, Infosys, HDFC als Hauptpositionen. Wachstumsstark aber volatil.",
        'XMKR.DE':  "Xtrackers MSCI Korea Swap UCITS ETF (TER 0,20%) — konzentriert auf südkoreanische Technologie- und Industriekonzerne. Samsung, SK Hynix, Hyundai als Top-Positionen.",
        # ── iShares Sektor (S&P 500) ──────────────────────────────────────────
        'QDVE.DE':  "iShares S&P 500 Information Technology Sector UCITS ETF (TER 0,15%) — US-IT-Giganten: Apple, Microsoft, NVIDIA, Broadcom. Stark konzentriert, hohes Wachstumspotenzial.",
        'QDVG.DE':  "iShares S&P 500 Health Care Sector UCITS ETF (TER 0,15%) — US-Pharma und -Medizintechnik: UnitedHealth, Eli Lilly, J&J. Defensiv mit Wachstumskomponente.",
        'QDVD.DE':  "iShares S&P 500 Financials Sector UCITS ETF (TER 0,15%) — US-Banken und -Versicherungen: JPMorgan, Berkshire Hathaway, Goldman Sachs. Zinsabhängig.",
        'SXRV.DE':  "iShares S&P 500 Communication Sector UCITS ETF (TER 0,15%) — Alphabet, Meta, Netflix, Disney. Kombination aus Wachstum und Dividende.",
        'IUIT.DE':  "iShares MSCI World Information Technology UCITS ETF (TER 0,40%) — globale IT-Werte: Apple, Microsoft, NVIDIA, TSMC. Breiter als S&P 500 IT durch internationale Titel.",
        'HEAL.DE':  "iShares MSCI World Health Care UCITS ETF (TER 0,35%) — globale Pharma, Biotech und Medizintechnik. Eli Lilly, UnitedHealth, Novo Nordisk als Hauptpositionen.",
        # ── Faktor-ETFs ───────────────────────────────────────────────────────
        'IWQU.DE':  "iShares MSCI World Quality Factor UCITS ETF (TER 0,30%) — selektiert ~300 Unternehmen nach hoher Eigenkapitalrendite, stabilem Gewinnwachstum und niedriger Verschuldung.",
        'IS3Q.DE':  "iShares Edge MSCI World Quality Factor UCITS ETF (TER 0,30%) — Quality-Faktor weltweit. Historisch überlegene risikoadjustierte Rendite gegenüber dem MSCI World.",
        'IWMO.DE':  "iShares MSCI World Momentum Factor UCITS ETF (TER 0,30%) — investiert in Aktien mit starker Kursdynamik. Hohe Umschlagshäufigkeit, überdurchschnittliche Rendite in Bullmärkten.",
        'MVOL.DE':  "iShares MSCI World Minimum Volatility UCITS ETF (TER 0,20%) — reduziert Schwankungen durch gezielte Titelauswahl. Defensiv mit moderatem Rendite-Risiko-Profil.",
        'WVAL.DE':  "iShares MSCI World Value Factor UCITS ETF (TER 0,30%) — günstiger bewertete Qualitätsunternehmen weltweit. Historisch bei steigendem Zinsniveau besser als Growth-ETFs.",
        'WSML.DE':  "iShares MSCI World Small Cap UCITS ETF (TER 0,35%) — Zugang zu ~3.500 kleineren Unternehmen aus Industrieländern. Höheres Wachstumspotenzial, aber auch höhere Volatilität.",
        'ZPRV.DE':  "SPDR MSCI USA Small Cap Value UCITS ETF (TER 0,30%) — kleine US-Value-Aktien mit niedrigem KBV und KGV. Historisch starke langfristige Renditen (Fama-French Small-Cap-Value-Prämie).",
        'ZPRX.DE':  "SPDR MSCI Europe Small Cap Value UCITS ETF (TER 0,30%) — europäische Small-Cap-Value-Titel. Geringe Korrelation zu Large-Cap-ETFs, gut zur Diversifikation.",
        'LGQG.DE':  "L&G Global Quality Equity Factors UCITS ETF (TER 0,25%) — selektiert nach Qualitätskriterien wie ROE, Gewinnstabilität und Bilanzkennzahlen. Günstiger Quality-ETF.",
        # ── Clean Energy / ESG ────────────────────────────────────────────────
        'IQQY.DE':  "iShares MSCI Europe UCITS ETF (TER 0,12%) — ca. 430 europäische Unternehmen aus 15 Ländern. UK, Frankreich, Schweiz, Deutschland als Hauptmärkte.",
        'IS3Y.DE':  "iShares MSCI EM ex-China UCITS ETF (TER 0,18%) — Schwellenländer ohne China. Indien, Taiwan, Südkorea dominieren. Für Anleger die chinesisches Risiko reduzieren wollen.",
        'IQQC.DE':  "iShares MSCI China UCITS ETF (TER 0,74%) — gezielter Zugang zum chinesischen Aktienmarkt. Alibaba, Tencent, Meituan als Hauptpositionen. Hohes politisches Risiko.",
    }

    @st.cache_data(ttl=3600, show_spinner=False)
    def _etf_info(ticker: str) -> dict:
        try:
            inf = yf.Ticker(ticker).info or {}
            name_l = (inf.get('longName') or '').lower()
            if   'acc' in name_l or 'accumul' in name_l: distrib = 'Thesaurierend (Acc)'
            elif 'dist' in name_l or 'distribut' in name_l: distrib = 'Ausschüttend (Dist)'
            elif (inf.get('dividendYield') or 0) > 0.001: distrib = 'Ausschüttend (Dist)'
            else: distrib = '—'
            exch = (inf.get('exchange') or '').upper()
            _dom = {'XETRA':'Irland','GER':'DE','FRA':'DE','LSE':'Irland',
                    'L':'Irland','ARCA':'USA','NYSE':'USA','BATS':'USA',
                    'SIX':'Luxemburg','PA':'Irland/LU'}

            # TER: yfinance → statische DB → FMP (US data ticker) → Name-Heuristik
            ter = (inf.get('annualReportExpenseRatio')
                   or inf.get('totalExpenseRatio') or inf.get('expenseRatio'))
            if not ter:
                ter = _ETF_STATIC_TER.get(ticker)
            if not ter and FMP_API_KEY:
                _dt = _ETF_DATA_TKR.get(ticker, ticker)
                try:
                    _fr = requests.get(
                        f"https://financialmodelingprep.com/api/v3/profile/{_dt}",
                        params={'apikey': FMP_API_KEY}, timeout=5)
                    if _fr.ok and _fr.json():
                        _fd = _fr.json()[0]
                        ter = _fd.get('annualReportExpenseRatio') or _fd.get('expenseRatio')
                except Exception:
                    pass
            # Letzter Fallback: TER aus ETF-Name ableiten (KIID-Werte)
            if not ter:
                _nl = name_l  # bereits lowercase
                if 'prime global' in _nl or 'prime all country' in _nl or 'prime all-country' in _nl:
                    ter = 0.0005  # Amundi Prime: 0.05%
                elif 'prime' in _nl and ('amundi' in _nl or 'world' in _nl or 'global' in _nl):
                    ter = 0.0007
                elif 'prime usa' in _nl or 'prime us' in _nl or 'prime s&p' in _nl:
                    ter = 0.0005
                elif 'core msci world' in _nl or 'core world' in _nl:
                    ter = 0.0020

            # AUM: yfinance → FMP (US data ticker)
            aum = inf.get('totalAssets') or inf.get('fundTotalAssets')
            if not aum and FMP_API_KEY:
                _dt = _ETF_DATA_TKR.get(ticker, ticker)
                try:
                    _fr = requests.get(
                        "https://financialmodelingprep.com/api/v3/etf/info",
                        params={'symbol': _dt, 'apikey': FMP_API_KEY}, timeout=5)
                    if _fr.ok and _fr.json():
                        aum = _fr.json()[0].get('totalAssets')
                except Exception:
                    pass
                if not aum:
                    try:
                        _fr2 = requests.get(
                            f"https://financialmodelingprep.com/api/v3/profile/{_dt}",
                            params={'apikey': FMP_API_KEY}, timeout=5)
                        if _fr2.ok and _fr2.json():
                            aum = _fr2.json()[0].get('mktCap')
                    except Exception:
                        pass
            if not aum:
                aum = _ETF_STATIC_AUM.get(ticker)

            return {
                'name':        inf.get('longName') or inf.get('shortName') or ticker,
                'currency':    inf.get('currency','EUR'),
                'aum':         aum,
                'ter':         ter,
                'nav':         inf.get('navPrice') or inf.get('previousClose'),
                'category':    inf.get('category') or '',
                'fund_family': inf.get('fundFamily') or '',
                'inception':   inf.get('fundInceptionDate'),
                'distribution':distrib,
                'domicile':    _dom.get(exch, inf.get('country') or '—'),
                'exchange':    exch or '—',
                'div_yield':   inf.get('dividendYield'),
                'quote_type':  inf.get('quoteType','ETF'),
                'description': (_ETF_STATIC_DESC.get(ticker)
                                or inf.get('longBusinessSummary') or ''),
            }
        except Exception:
            return {}

    @st.cache_data(ttl=3600, show_spinner=False)
    def _etf_holdings(ticker: str) -> tuple:
        def _parse_fd(fd):
            sw = getattr(fd, 'sector_weightings', None) or {}
            th = getattr(fd, 'top_holdings', None)
            if th is None or (hasattr(th,'empty') and th.empty): th = pd.DataFrame()
            cw = {}
            eq_vals = {}
            eq = getattr(fd, 'equity_holdings', None)
            if eq is not None:
                try:
                    eq_d = eq if isinstance(eq, dict) else eq.to_dict()
                    cw = eq_d.get('countryWeights', {})
                    for _fld in ['priceToEarnings','priceToBook','priceToSales',
                                 'priceToCashflow','medianMarketCap','threeYearEarningsGrowth']:
                        _fv = eq_d.get(_fld)
                        if _fv is not None:
                            eq_vals[_fld] = _fv
                except Exception: pass
            ac = getattr(fd, 'asset_classes', None) or {}
            if hasattr(ac,'to_dict'): ac = ac.to_dict()
            return sw, th, cw, ac, eq_vals

        try:
            sw, th, cw, ac, eq_vals = _parse_fd(yf.Ticker(ticker).funds_data)

            # Fallback 1: US-Datenticker via yFinance (XETRA ETFs haben meist keine funds_data)
            _data_tkr = _ETF_DATA_TKR.get(ticker)
            if _data_tkr and (not sw or th.empty or not eq_vals):
                try:
                    sw2, th2, cw2, ac2, eq2 = _parse_fd(yf.Ticker(_data_tkr).funds_data)
                    if not sw and sw2: sw = sw2
                    if th.empty and not th2.empty: th = th2
                    if not cw and cw2: cw = cw2
                    if not eq_vals and eq2: eq_vals = eq2
                except Exception: pass

            # Fallback 2: FMP API (Sektor-Gewichte + Top-Holdings + Länder)
            _fmp_tkr = _ETF_DATA_TKR.get(ticker, ticker)
            if not sw and FMP_API_KEY:
                try:
                    _fr = requests.get(
                        f"https://financialmodelingprep.com/api/v3/etf-sector-weightings/{_fmp_tkr}",
                        params={'apikey': FMP_API_KEY}, timeout=5)
                    if _fr.ok and _fr.json():
                        sw = {s['sector']: float(s['weightPercentage'])/100
                              for s in _fr.json() if 'sector' in s and s.get('weightPercentage')}
                except Exception: pass

            if th.empty and FMP_API_KEY:
                try:
                    _fr = requests.get(
                        f"https://financialmodelingprep.com/api/v3/etf-holder/{_fmp_tkr}",
                        params={'apikey': FMP_API_KEY}, timeout=5)
                    if _fr.ok and _fr.json():
                        _hdata = _fr.json()[:20]
                        th = pd.DataFrame(_hdata)
                        if 'asset' in th.columns:
                            th = th.rename(columns={
                                'asset': 'holdingName',
                                'weightPercentage': 'holdingPercent',
                                'symbol': 'symbol'})
                except Exception: pass

            if not cw and FMP_API_KEY:
                try:
                    _fr = requests.get(
                        f"https://financialmodelingprep.com/api/v3/etf-country-weightings/{_fmp_tkr}",
                        params={'apikey': FMP_API_KEY}, timeout=5)
                    if _fr.ok and _fr.json():
                        cw = {row['country']: float(str(row.get('weightPercentage','0')).replace('%',''))
                              for row in _fr.json() if row.get('country') and row.get('weightPercentage')}
                except Exception: pass

            # Fallback 3: Statische Länderdaten (Fondsanbieter-Angaben)
            if not cw:
                cw = dict(_ETF_STATIC_CW.get(ticker, {}))

            # Fallback 4: supplement missing fields via yFinance .info (also runs when eq_vals is partial)
            _missing_val = lambda: not all(eq_vals.get(k) for k in ('priceToBook', 'priceToSales'))
            if _missing_val():
                _info_tkr = _data_tkr or ticker
                try:
                    _inf2 = yf.Ticker(_info_tkr).info
                    _field_map = {
                        'trailingPE':                    'priceToEarnings',
                        'priceToBook':                   'priceToBook',
                        'priceToSalesTrailing12Months':  'priceToSales',
                        'earningsGrowth':                'threeYearEarningsGrowth',
                        'enterpriseToEbitda':            'priceToCashflow',
                        'medianMarketCap':               'medianMarketCap',
                    }
                    for _yf_k, _eq_k in _field_map.items():
                        if _eq_k not in eq_vals:  # only fill missing fields
                            _v = _inf2.get(_yf_k)
                            if _v is not None:
                                eq_vals[_eq_k] = float(_v) * (100 if _yf_k == 'earningsGrowth' else 1)
                except Exception:
                    pass

            # Fallback 5: supplement missing via FMP key-metrics (also runs when eq_vals is partial)
            if _missing_val() and FMP_API_KEY:
                _fmp_val_tkr = _data_tkr or _fmp_tkr
                try:
                    _fr = requests.get(
                        f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{_fmp_val_tkr}",
                        params={'apikey': FMP_API_KEY}, timeout=5)
                    if _fr.ok and _fr.json():
                        _km = _fr.json()[0]
                        _fmap = {
                            'peRatioTTM':           'priceToEarnings',
                            'pbRatioTTM':           'priceToBook',
                            'priceToSalesRatioTTM': 'priceToSales',
                            'revenueGrowthTTM':     'threeYearEarningsGrowth',
                            'marketCapTTM':         'medianMarketCap',
                        }
                        for _fk, _ek in _fmap.items():
                            if _ek not in eq_vals:  # only fill missing fields
                                _v = _km.get(_fk)
                                if _v is not None:
                                    eq_vals[_ek] = float(_v)
                except Exception:
                    pass

            return sw, th, cw, ac, eq_vals
        except Exception:
            return {}, pd.DataFrame(), {}, {}, {}

    @st.cache_data(ttl=3600, show_spinner=False)
    def _etf_vs_bm(etf: str, bm: str, period: str) -> pd.DataFrame:
        try:
            raw = yf.download([etf, bm], period=period, interval='1wk',
                              progress=False, auto_adjust=True)
            if raw.empty: return pd.DataFrame()
            cl = raw['Close']
            if isinstance(cl, pd.Series): cl = cl.to_frame()
            cl = cl.dropna(how='all')
            for col in cl.columns:
                first = cl[col].dropna().iloc[0] if not cl[col].dropna().empty else 1
                cl[col] = cl[col] / first * 100
            return cl
        except Exception:
            return pd.DataFrame()

    # ── Issuer-Meta (Logo-URL + Farbe + Kurzname) ─────────────────────────
    _ISSUER_META = {
        'iShares':    {'logo':'https://www.blackrock.com/favicon.ico',   'color':'#00b347','abbr':'iS','bg':'#003d14'},
        'Vanguard':   {'logo':'https://www.vanguard.com/favicon.ico',    'color':'#cc0000','abbr':'VG','bg':'#3d0000'},
        'Xtrackers':  {'logo':'https://www.xtrackers.com/favicon.ico',   'color':'#1a6aff','abbr':'Xt','bg':'#001040'},
        'Amundi':     {'logo':'https://www.amundi.com/favicon.ico',      'color':'#ff6600','abbr':'AM','bg':'#3d1900'},
        'SPDR':       {'logo':'https://www.ssga.com/favicon.ico',        'color':'#ffd700','abbr':'SP','bg':'#2d2600'},
        'Invesco':    {'logo':'https://www.invesco.com/favicon.ico',      'color':'#0066cc','abbr':'IN','bg':'#001a33'},
        'WisdomTree': {'logo':'https://www.wisdomtree.eu/favicon.ico',   'color':'#009933','abbr':'WT','bg':'#001a0a'},
        'Lyxor':      {'logo':'https://www.amundi.com/favicon.ico',      'color':'#00a86b','abbr':'LY','bg':'#001a10'},
        'Franklin':   {'logo':'https://www.franklintempleton.de/favicon.ico','color':'#003087','abbr':'FT','bg':'#000d1f'},
        'HSBC':       {'logo':'https://www.hsbc.de/favicon.ico',         'color':'#db0011','abbr':'HB','bg':'#2d0003'},
        'BlackRock':  {'logo':'https://www.blackrock.com/favicon.ico',   'color':'#00b347','abbr':'BR','bg':'#003d14'},
    }

    # ── Ähnliche ETFs (nach Ticker) ───────────────────────────────────────
    _SIMILAR_ETF_MAP = {
        'SXR8.DE': [('VWCE.DE','Vanguard All-World'),('XDWD.DE','Xtrackers World'),('LCUW.DE','Amundi World')],
        'VWCE.DE': [('SXR8.DE','iShares MSCI World'),('XDWD.DE','Xtrackers World'),('FWRA.DE','Invesco All-World')],
        'SXR2.DE': [('XSPX.DE','Xtrackers S&P 500'),('VUSD.L','Vanguard S&P 500'),('CSPX.L','iShares S&P 500 USD')],
        'EQQQ.DE': [('XNAS.DE','Xtrackers NASDAQ-100'),('SXRV.DE','iShares NASDAQ EUR'),('CSNDX.L','iShares NASDAQ USD')],
        'EXS1.DE': [('DBXD.DE','Xtrackers DAX'),('DAXE.DE','Amundi DAX'),('XDDX.DE','Xtrackers DAX ESG')],
        'IS3N.DE': [('XMME.DE','Xtrackers MSCI EM'),('VFEM.L','Vanguard FTSE EM'),('PAEM.PA','SPDR MSCI EM')],
        'LCUW.DE': [('SXR8.DE','iShares MSCI World'),('VWCE.DE','Vanguard All-World'),('XDWD.DE','Xtrackers World')],
        'XDWD.DE': [('SXR8.DE','iShares MSCI World'),('VWCE.DE','Vanguard All-World'),('LCUW.DE','Amundi World')],
    }

    # ── Beliebte ETFs mit ISIN und WKN ───────────────────────────────────
    _POPULAR_ETFS = [
        ('SXR8.DE', 'iShares MSCI World',  'IE00B4L5Y983', 'A0RPWH',  '#00b347', 'iS'),
        ('VWCE.DE', 'Vanguard All-World',   'IE00B3RBWM25', 'A1JX52',  '#cc0000', 'VG'),
        ('SXR2.DE', 'iShares S&P 500',      'IE0031442068', '622391',  '#00b347', 'iS'),
        ('IS3N.DE', 'iShares MSCI EM',      'IE00B4L5YC18', 'A0HGWC',  '#00b347', 'iS'),
        ('XDWD.DE', 'Xtrackers World',      'IE00BJ0KDQ92', 'DBX1MW',  '#1a6aff', 'Xt'),
        ('EQQQ.DE', 'iShares NASDAQ-100',   'IE0032895942', 'A0YEDL',  '#00b347', 'iS'),
        ('EXS1.DE', 'iShares DAX',          'DE0005933931', '593393',  '#00b347', 'iS'),
        ('LCUW.DE', 'Amundi MSCI World',    'LU1781541179', 'ETF127',  '#ff6600', 'AM'),
    ]

    # ── Header ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:24px 0 14px 0;">
      <div style="font-size:2rem;font-weight:800;color:#fff;">🔎 ETF-Analyzer</div>
      <div style="color:{_C_ACCENT};font-size:0.88rem;margin-top:4px;">
        Ticker · ISIN · WKN · Name — Sektoren · Positionen · Benchmark
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Suchfeld ─────────────────────────────────────────────────────────
    _src1, _src2 = st.columns([4, 1])
    _etf_raw = _src1.text_input("ETF suchen", value=st.session_state["etf_ticker_input"],
                                 placeholder="Ticker (SXR8.DE) · ISIN (IE00B4L5Y983) · WKN (A0RPWH) · Name",
                                 label_visibility="collapsed")
    _etf_go  = _src2.button("Analysieren", use_container_width=True, type="primary")
    if _etf_go and _etf_raw.strip():
        st.session_state["etf_ticker_input"] = _etf_raw.strip()
        st.rerun()

    # ── Live-Vorschläge beim Tippen ───────────────────────────────────────
    _q_raw = _etf_raw.strip()
    _q_low = _q_raw.lower()
    if len(_q_raw) >= 2:
        _sug_hits = []
        for _stk, _snm, _sisin, _swkn, _ster in _ETF_SEARCH_DB:
            if (_q_low in _snm.lower() or _q_low in _stk.lower()
                    or _q_low in _sisin.lower() or _q_low in _swkn.lower()):
                _sug_hits.append((_stk, _snm, _sisin, _swkn, _ster))
            if len(_sug_hits) >= 6:
                break
        if _sug_hits and _q_raw.upper() not in [h[0].upper() for h in _sug_hits]:
            st.markdown(f"<div style='color:{_C_TEXT_MUTED};font-size:0.72rem;"
                        "margin:6px 0 4px 0;'>Vorschläge:</div>", unsafe_allow_html=True)
            _sug_cols = st.columns(min(len(_sug_hits), 3))
            for _si, (_stk, _snm, _sisin, _swkn, _ster) in enumerate(_sug_hits):
                with _sug_cols[_si % 3]:
                    _sug_label = f"**{_snm[:32]}**\n{_stk} · TER {_ster}"
                    if st.button(_sug_label, key=f"_sug_{_stk}_{_si}",
                                 use_container_width=True):
                        st.session_state["etf_ticker_input"] = _stk
                        st.rerun()

    # ── Beliebte ETFs als Cards ───────────────────────────────────────────
    st.markdown("<div style='color:#78909c;font-size:0.72rem;text-transform:uppercase;"
                "letter-spacing:.06em;margin:10px 0 6px 0;'>Beliebte ETFs</div>",
                unsafe_allow_html=True)
    _pc = st.columns(4)
    for _pi, (_ptkr, _pnm, _pisin, _pwkn, _pclr, _pabb) in enumerate(_POPULAR_ETFS):
        with _pc[_pi % 4]:
            _active = st.session_state["etf_ticker_input"].strip().upper() == _ptkr
            _border = f"2px solid {_pclr}" if _active else "1px solid #1a2740"
            st.markdown(
                f"<div style='background:{_C_CARD_BG};border:{_border};border-radius:8px;"
                f"padding:8px 10px;margin-bottom:4px;'>"
                f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:4px;'>"
                f"<span style='background:{_pclr}22;color:{_pclr};border:1px solid {_pclr}55;"
                f"border-radius:4px;padding:1px 6px;font-size:0.68rem;font-weight:700;'>{_pabb}</span>"
                f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.8rem;font-weight:600;'>{_ptkr}</span>"
                f"</div>"
                f"<div style='color:{_C_TEXT_MUTED2};font-size:0.72rem;white-space:nowrap;overflow:hidden;"
                f"text-overflow:ellipsis;'>{_pnm}</div>"
                f"<div style='color:{_C_TEXT_MUTED};font-size:0.65rem;margin-top:2px;'>ISIN {_pisin} · WKN {_pwkn}</div>"
                f"</div>", unsafe_allow_html=True)
            if st.button("▶", key=f"_pop_{_ptkr}", use_container_width=True,
                         type="primary" if _active else "secondary"):
                st.session_state["etf_ticker_input"] = _ptkr
                st.rerun()

    _etf_raw_resolved = st.session_state["etf_ticker_input"].strip()
    if not _etf_raw_resolved:
        st.stop()

    # ── Ticker auflösen ───────────────────────────────────────────────────
    with st.spinner("Ticker wird aufgelöst…"):
        _etf_tkr = _resolve_etf_input(_etf_raw_resolved)

    # ── Daten laden ───────────────────────────────────────────────────────
    with st.spinner(f"ETF-Daten für {_etf_tkr} werden geladen…"):
        _ei            = _etf_info(_etf_tkr)
        _perf          = _etf_perf_hist(_etf_tkr)
        _sw, _th, _cw, _ac, _eq_vals = _etf_holdings(_etf_tkr)

    _ei['ytd']    = _perf.get('ytd')    or _ei.get('ytd')
    _ei['ret_1y'] = _perf.get('ret_1y') or _ei.get('ret_1y')
    _ei['ret_3y'] = _perf.get('ret_3y') or _ei.get('ret_3y')
    _ei['ret_5y'] = _perf.get('ret_5y') or _ei.get('ret_5y')

    if not _ei or not _ei.get('name'):
        st.error(f"Keine Daten für '{_etf_tkr}' gefunden.\n\n"
                 "Bitte Ticker (z.B. SXR8.DE), ISIN (z.B. IE00B4L5Y983) oder WKN (z.B. A0RPWH) eingeben.")
        st.stop()

    # ── Issuer ermitteln + Logo/Badge ─────────────────────────────────────
    _ff = _ei.get('fund_family', '')
    _im = next(((_k, _v) for _k, _v in _ISSUER_META.items()
                if _k.lower() in _ff.lower()), None)
    _im_key, _im_val = (_im if _im else (None, None))

    def _issuer_badge(key, meta):
        if not key or not meta:
            return ""
        _logo = meta['logo']
        _clr  = meta['color']
        _abbr = meta['abbr']
        _bg   = meta.get('bg','#001a0a')
        return (
            f"<span style='display:inline-flex;align-items:center;gap:5px;"
            f"background:{_bg};border:1px solid {_clr}44;border-radius:6px;"
            f"padding:3px 8px;margin-right:8px;'>"
            f"<img src='{_logo}' style='height:16px;width:16px;border-radius:2px;' "
            f"onerror=\"this.outerHTML='<span style=\\'font-size:0.65rem;font-weight:700;"
            f"color:{_clr};padding:0 2px;\\'>{_abbr}</span>'\">"
            f"<span style='color:{_clr};font-size:0.72rem;font-weight:700;'>{key}</span></span>")

    # Faktor-/Sektor-Tags vorab berechnen (wird in Header + KI-Analyse genutzt)
    _nl_tags = (_ei.get('name', '') + ' ' + _ei.get('category', '')).lower()
    _factor_tags: list = []
    if any(x in _nl_tags for x in ['value', 'enhanced value', 'substanz']):
        _factor_tags.append(('📊 Value', '#ffd54f', '#1a1200'))
    if any(x in _nl_tags for x in [' growth', 'wachstum']):
        _factor_tags.append(('🚀 Growth', '#81c784', '#001a00'))
    if 'momentum' in _nl_tags:
        _factor_tags.append(('⚡ Momentum', '#ff8a65', '#1a0800'))
    if 'quality' in _nl_tags:
        _factor_tags.append(('💎 Quality', '#ce93d8', '#150020'))
    if any(x in _nl_tags for x in ['min vol', 'minimum vol', 'low vol', 'low volatil']):
        _factor_tags.append(('🛡 Low Vol', '#80cbc4', '#001a18'))
    if any(x in _nl_tags for x in ['dividend', 'high dividend', 'income', 'yield']):
        _factor_tags.append(('💰 Dividenden', _C_NEUTRAL, '#1a1000'))
    if any(x in _nl_tags for x in ['esg', ' sri', 'sustainable', 'socially responsible', 'climate', 'paris']):
        _factor_tags.append(('🌱 ESG/SRI', '#a5d6a7', '#001a05'))
    if any(x in _nl_tags for x in ['small cap', 'small-cap', 'smallcap', 'small company']):
        _factor_tags.append(('🔬 Small Cap', '#b0bec5', '#0d1f35'))
    if any(x in _nl_tags for x in ['multi-factor', 'multifactor', 'multi factor']):
        _factor_tags.append(('⚙ Multi-Faktor', '#ffab40', '#1a0e00'))
    _sector_map_tags = [
        (['technology', 'tech ', 'semiconductor', 'digital'], '💻 Technologie', '#29b6f6', '#001728'),
        (['healthcare', 'health care', 'medical', 'pharma', 'biotech'], '🏥 Gesundheit', '#66bb6a', '#001500'),
        (['financial', 'bank', 'insurance'], '🏦 Finanzen', '#ffa726', '#1a0a00'),
        (['energy', 'clean energy', 'renewable'], '⚡ Energie', '#ffee58', '#1a1800'),
        (['real estate', 'reit', 'property', 'immobil'], '🏠 Immobilien', '#ef5350', '#1a0000'),
        (['consumer', 'retail', 'staple', 'discretionary'], '🛒 Konsum', '#ab47bc', '#150015'),
        (['industrial', 'infrastructure', 'aerospace', 'defense'], '🏭 Industrie', '#78909c', '#0d1820'),
        (['material', 'commodit', 'gold', 'silver', 'mining'], '⛏ Rohstoffe', '#a1887f', '#1a1005'),
        (['water', 'environment', 'green'], '💧 Wasser/Umwelt', '#26c6da', '#001a1d'),
        (['cybersecurity', 'cyber'], '🔒 Cybersecurity', '#ef5350', '#200000'),
        (['artificial intellig', 'robotics', 'automation', ' ai ', 'machine learn'], '🤖 KI/Robotik', '#7e57c2', '#0e0015'),
    ]
    for _kws_t, _lbl_t, _clr_t, _bg_t in _sector_map_tags:
        if any(kw in _nl_tags for kw in _kws_t):
            _factor_tags.append((_lbl_t, _clr_t, _bg_t))
            break

    # ── Headerbereich ─────────────────────────────────────────────────────
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    _h1, _h2 = st.columns([5, 1])
    with _h1:
        _badge_html  = _issuer_badge(_im_key, _im_val)
        _name_html   = (f"<div style='font-size:1.3rem;font-weight:800;color:{_C_TEXT_PRIMARY};"
                        f"line-height:1.3;margin-bottom:6px;'>{_ei.get('name','')}</div>")
        def _pill(txt, clr, bg):
            return (f"<span style='background:{bg};color:{clr};border:1px solid {clr}44;"
                    f"border-radius:10px;padding:2px 9px;font-size:0.7rem;font-weight:600;"
                    f"margin-right:5px;white-space:nowrap;'>{txt}</span>")
        _pills = ""
        _pills += _pill(f"💱 {_ei.get('currency','EUR')}", '#64b5f6', '#0d2035')
        if _ei.get('distribution') and _ei['distribution'] != '—':
            _dc = _C_POSITIVE if 'Acc' in _ei['distribution'] else _C_NEUTRAL
            _pills += _pill(_ei['distribution'], _dc, '#0d1a2e')
        if _ei.get('domicile') and _ei['domicile'] != '—':
            _pills += _pill(f"🏛 {_ei['domicile']}", '#90a4ae', '#1a2740')
        if _ei.get('category'):
            _pills += _pill(_ei['category'][:28], '#b0bec5', '#161f30')
        # Faktor-/Sektor-Tags (vorab berechnet in _factor_tags)
        for _ft, _fc, _fb in _factor_tags:
            _pills += _pill(_ft, _fc, _fb)
        st.markdown(f"{_badge_html}{_name_html}"
                    f"<div style='display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px;'>"
                    f"{_pills}</div>", unsafe_allow_html=True)
        # ETF-Beschreibung
        _desc = _ei.get('description', '')
        if _desc:
            _sentences  = [s.strip() for s in _desc.replace('\n', ' ').split('. ') if s.strip()]
            _desc_short = '. '.join(_sentences[:3]) + ('.' if len(_sentences) > 3 else '')
            _desc_rest  = '. '.join(_sentences[3:]) + '.' if len(_sentences) > 3 else ''
            _desc_key   = f"etf_desc_exp_{_etf_tkr}"
            _desc_exp   = st.session_state.get(_desc_key, False)
            _shown_txt  = (_desc_short + ' ' + _desc_rest) if (_desc_rest and _desc_exp) else _desc_short
            st.markdown(
                f"<div style='background:{_C_CARD_BG};border:1px solid #1a2740;border-radius:8px;"
                f"padding:10px 14px;margin-top:4px;margin-bottom:2px;'>"
                f"<div style='color:#78909c;font-size:0.65rem;text-transform:uppercase;"
                f"letter-spacing:.08em;margin-bottom:5px;'>📋 Beschreibung</div>"
                f"<div style='color:#cfd8dc;font-size:0.82rem;line-height:1.55;'>{_shown_txt}</div>"
                f"</div>", unsafe_allow_html=True)
            if _desc_rest:
                if st.button(
                    "Weniger anzeigen ▴" if _desc_exp else "Mehr anzeigen ▾",
                    key=f"desc_btn_{_etf_tkr}",
                ):
                    st.session_state[_desc_key] = not _desc_exp
                    st.rerun()
    with _h2:
        if st.button("🔄 Ähnliche ETFs", use_container_width=True, key="btn_similar"):
            st.session_state["etf_show_similar"] = not st.session_state.get("etf_show_similar", False)

    # Ähnliche ETFs
    if st.session_state.get("etf_show_similar"):
        _sim = _SIMILAR_ETF_MAP.get(_etf_tkr, [])
        if not _sim:
            st.info("Keine Alternativen für diesen ETF hinterlegt.")
        else:
            st.markdown("<div class='section-header'>🔄 Ähnliche ETFs</div>", unsafe_allow_html=True)
            _sc = st.columns(len(_sim))
            for _si, (_stkr, _snm) in enumerate(_sim):
                with _sc[_si]:
                    st.markdown(
                        f"<div style='background:{_C_CARD_BG};border:1px solid #1a2740;"
                        f"border-radius:8px;padding:10px;text-align:center;'>"
                        f"<div style='color:{_C_ACCENT};font-size:0.88rem;font-weight:700;'>{_stkr}</div>"
                        f"<div style='color:{_C_TEXT_MUTED2};font-size:0.7rem;margin-top:3px;'>{_snm}</div>"
                        f"</div>", unsafe_allow_html=True)
                    if st.button("Analysieren", key=f"sim_{_stkr}", use_container_width=True):
                        st.session_state["etf_ticker_input"] = _stkr
                        st.session_state["etf_show_similar"] = False
                        st.rerun()

    # ── Kennzahlen (CSS-Grid, 2×4) ────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Kennzahlen</div>", unsafe_allow_html=True)
    def _kc(lbl, val, sub="", color="#eceff1"):
        _s = f"<div style='color:{_C_TEXT_MUTED};font-size:0.6rem;margin-top:2px;'>{sub}</div>" if sub else ""
        return (f"<div style='background:{_C_CARD_BG};border:1px solid #1a2740;border-radius:8px;"
                f"padding:10px 8px;text-align:center;'>"
                f"<div style='color:#78909c;font-size:0.62rem;text-transform:uppercase;"
                f"letter-spacing:.05em;margin-bottom:4px;'>{lbl}</div>"
                f"<div style='color:{color};font-size:1rem;font-weight:700;'>{val}</div>"
                f"{_s}</div>")
    _g = "display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:6px;"
    _rc = lambda v: _C_POSITIVE if (v or 0) >= 0 else _C_NEGATIVE
    _aum = (f"€ {_ei['aum']/1e9:.1f} Mrd" if (_ei.get('aum') or 0) > 1e9
            else f"€ {_ei['aum']/1e6:.0f} Mio" if _ei.get('aum') else "—")
    _ter = f"{_ei['ter']*100:.2f}%" if _ei.get('ter') else "—"
    _nav = f"{_ei.get('nav'):.2f} {_ei.get('currency','')}" if _ei.get('nav') else "—"
    _ytd = f"{_ei['ytd']*100:+.1f}%" if _ei.get('ytd') else "—"
    _r1y = f"{_ei.get('ret_1y',0)*100:+.1f}%" if _ei.get('ret_1y') else "—"
    _r3y = f"{_ei['ret_3y']*100:+.1f}% p.a." if _ei.get('ret_3y') else "—"
    _r5y = f"{_ei['ret_5y']*100:+.1f}% p.a." if _ei.get('ret_5y') else "—"
    _div = f"{_ei['div_yield']*100:.2f}%" if _ei.get('div_yield') else "—"
    _inc = "—"
    if _ei.get('inception'):
        try:
            import datetime as _dt2
            _inc = _dt2.datetime.fromtimestamp(_ei['inception']).strftime('%d.%m.%Y')
        except Exception: pass
    st.markdown(
        f"<div style='{_g}'>"
        + _kc("Fondsvolumen", _aum, "AUM")
        + _kc("TER Kosten p.a.", _ter, "Gesamtkostenquote")
        + _kc("Kurs / NAV", _nav)
        + _kc("Auflagedatum", _inc, "Fondsstart")
        + "</div>"
        + f"<div style='{_g}'>"
        + _kc("YTD", _ytd, "laufendes Jahr", _rc(_ei.get('ytd',0)))
        + _kc("1J-Rendite", _r1y, "letzte 12 Monate", _rc(_ei.get('ret_1y',0)))
        + _kc("3J p.a.", _r3y, "annualisiert 3 Jahre", _rc(_ei.get('ret_3y',0)))
        + _kc("5J p.a.", _r5y, "annualisiert 5 Jahre", _rc(_ei.get('ret_5y',0)))
        + "</div>",
        unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Fundamentaler ETF-Score ────────────────────────────────────────────
    st.markdown("<div class='section-header'>🏆 Fundamentaler ETF-Score</div>", unsafe_allow_html=True)

    # Statische Zusatzdaten: Replikation + Anzahl Positionen
    _ETF_REPLICATION = {
        # Physical full
        'VWCE.DE':'Vollständig','FWRA.DE':'Vollständig','VWRL.L':'Vollständig',
        'IS3N.DE':'Vollständig','IEMG':'Vollständig','VT':'Vollständig',
        'SXR8.DE':'Vollständig','EUNL.DE':'Vollständig','EXS1.DE':'Vollständig',
        'MEUD.DE':'Vollständig','EXW1.DE':'Vollständig','LYPS.DE':'Vollständig',
        'IQQY.DE':'Vollständig','SPYY.DE':'Vollständig','IEUA.DE':'Vollständig',
        'ISPA.DE':'Vollständig','QDIV.DE':'Vollständig','XDIV.DE':'Vollständig',
        'IDVY.L':'Vollständig','VHYL.L':'Vollständig','IUSN.DE':'Sampling',
        'IQQH.DE':'Vollständig','EQQQ.DE':'Vollständig','SPY5.DE':'Vollständig',
        'IMEA.DE':'Vollständig','IS3R.DE':'Vollständig','LCUW.DE':'Sampling',
        'EXV5.DE':'Vollständig','IQQC.DE':'Vollständig','IQQD.DE':'Sampling',
        # Swap-basiert (Synthethisch)
        'XDWD.DE':'Synthetisch','XMME.DE':'Synthetisch','XESC.DE':'Synthetisch',
        'XEUR.DE':'Synthetisch','XDJP.DE':'Synthetisch','XMWO.DE':'Synthetisch',
        'DBXD.DE':'Synthetisch','ZPRX.DE':'Synthetisch','IUSE.DE':'Sampling',
        # US tickers
        'SPY':'Vollständig','IVV':'Vollständig','QQQ':'Vollständig',
        'URTH':'Vollständig','VYM':'Vollständig','SCHD':'Vollständig',
        'FEZ':'Vollständig','EWG':'Vollständig','EWJ':'Vollständig',
        'MCHI':'Vollständig','EEM':'Sampling','IEMG':'Vollständig',
    }
    _ETF_HOLDINGS_COUNT = {
        'VWCE.DE':3700,'FWRA.DE':3700,'VWRL.L':3700,'SXR8.DE':1500,
        'EUNL.DE':1500,'XDWD.DE':2150,'XMWO.DE':1500,'IS3N.DE':1400,
        'IS3R.DE':1400,'IMEA.DE':1400,'XMME.DE':1400,'IQQD.DE':1400,
        'EXS1.DE':90,'MEUD.DE':290,'EXW1.DE':290,'LYPS.DE':290,
        'IQQY.DE':450,'SPYY.DE':450,'IEUA.DE':450,'XESC.DE':50,
        'XEUR.DE':290,'IQQE.DE':450,'IEMC.DE':450,'ZPRX.DE':450,
        'EXV5.DE':230,'XDJP.DE':230,'IQQJ.DE':230,'IQQC.DE':700,
        'IQQP.DE':900,'EQQQ.DE':100,'SPY5.DE':500,'LCUW.DE':500,
        'IUSN.DE':2000,'IUSE.DE':500,'VHYL.L':1800,'ISPA.DE':100,
        'QDIV.DE':100,'XDIV.DE':100,'IDVY.L':100,'IQQH.DE':50,
        'DBXD.DE':90,'SXR2.DE':500,'MEUD.DE':290,
    }

    # Scoring-Funktion
    def _calc_etf_score(ei, tkr, th_df):
        criteria = []

        # 1. TER / Kosten (30 Punkte)
        ter = ei.get('ter')
        if ter is not None:
            ter_pct = ter * 100 if ter < 1 else ter
            if   ter_pct <= 0.10: pts, label = 30, f"{ter_pct:.2f}% — Sehr günstig"
            elif ter_pct <= 0.20: pts, label = 24, f"{ter_pct:.2f}% — Günstig"
            elif ter_pct <= 0.35: pts, label = 15, f"{ter_pct:.2f}% — Durchschnittlich"
            elif ter_pct <= 0.50: pts, label = 8,  f"{ter_pct:.2f}% — Teuer"
            else:                  pts, label = 0,  f"{ter_pct:.2f}% — Sehr teuer"
        else:
            pts, label = 15, "Keine Daten (Ø angenommen)"
        criteria.append(('💰 TER / Kosten', pts, 30, label))

        # 2. Fondsvolumen / AUM (25 Punkte)
        aum = ei.get('aum') or 0
        if   aum >= 10e9:  pts, label = 25, f"€ {aum/1e9:.1f} Mrd — Sehr groß"
        elif aum >= 1e9:   pts, label = 20, f"€ {aum/1e9:.1f} Mrd — Groß"
        elif aum >= 500e6: pts, label = 14, f"€ {aum/1e6:.0f} Mio — Mittel"
        elif aum >= 100e6: pts, label = 8,  f"€ {aum/1e6:.0f} Mio — Klein"
        elif aum > 0:      pts, label = 2,  f"€ {aum/1e6:.0f} Mio — Sehr klein"
        else:              pts, label = 10, "Keine Daten (Ø angenommen)"
        criteria.append(('📦 Fondsvolumen', pts, 25, label))

        # 3. Fondsalter (20 Punkte)
        import datetime as _dt_sc
        inception = ei.get('inception')
        age_years = None
        if inception:
            try:
                age_years = (_dt_sc.date.today() - _dt_sc.datetime.fromtimestamp(inception).date()).days / 365.25
            except Exception: pass
        if age_years is None:
            pts, label = 10, "Keine Daten (Ø angenommen)"
        elif age_years >= 15: pts, label = 20, f"{age_years:.1f} Jahre — Sehr etabliert"
        elif age_years >= 10: pts, label = 17, f"{age_years:.1f} Jahre — Etabliert"
        elif age_years >= 5:  pts, label = 12, f"{age_years:.1f} Jahre — Solide"
        elif age_years >= 2:  pts, label = 6,  f"{age_years:.1f} Jahre — Jung"
        else:                  pts, label = 1,  f"{age_years:.1f} Jahre — Sehr jung"
        criteria.append(('📅 Fondsalter', pts, 20, label))

        # 4. Replikationsmethode (15 Punkte)
        repl = _ETF_REPLICATION.get(tkr)
        if not repl:
            _name_l = (ei.get('name') or '').lower()
            if 'swap' in _name_l or 'synthetic' in _name_l or 'synthetisch' in _name_l:
                repl = 'Synthetisch'
            elif 'sampling' in _name_l or 'optimiert' in _name_l:
                repl = 'Sampling'
            elif 'physical' in _name_l or 'physisch' in _name_l:
                repl = 'Vollständig'
        _REPL_PTS = {'Vollständig': (15, '— Vollständige Replikation (physisch)'),
                     'Sampling':    (10, '— Optimiertes Sampling'),
                     'Synthetisch': (4,  '— Swap-basiert (Kontrahentenrisiko)')}
        if repl and repl in _REPL_PTS:
            pts, sub = _REPL_PTS[repl]
            label = f"{repl} {sub}"
        else:
            pts, label = 10, "Unbekannt (Ø angenommen)"
        criteria.append(('🔬 Replikation', pts, 15, label))

        # 5. Streuung / Anzahl Positionen (10 Punkte)
        n_hold = _ETF_HOLDINGS_COUNT.get(tkr)
        if n_hold is None and not th_df.empty:
            n_hold = len(th_df) * 10  # grobe Schätzung aus Top-Holdings-Länge
        if n_hold is None:           pts, label = 5,  "Keine Daten"
        elif n_hold >= 1000:         pts, label = 10, f"{n_hold:,}+ Positionen — Sehr breit"
        elif n_hold >= 300:          pts, label = 8,  f"{n_hold} Positionen — Breit"
        elif n_hold >= 100:          pts, label = 5,  f"{n_hold} Positionen — Mittel"
        elif n_hold >= 30:           pts, label = 2,  f"{n_hold} Positionen — Konzentriert"
        else:                         pts, label = 0,  f"{n_hold} Positionen — Sehr konzentriert"
        criteria.append(('🌐 Streuung', pts, 10, label))

        total = sum(c[1] for c in criteria)
        max_total = sum(c[2] for c in criteria)
        return total, max_total, criteria

    _score, _score_max, _score_criteria = _calc_etf_score(_ei, _etf_tkr, _th)
    _score_pct = _score / _score_max * 100

    # Score-Farbe + Note
    if   _score_pct >= 85: _sc, _grade, _verdict = _C_POSITIVE, 'A+', 'Ausgezeichnet'
    elif _score_pct >= 75: _sc, _grade, _verdict = _C_POSITIVE, 'A',  'Sehr gut'
    elif _score_pct >= 65: _sc, _grade, _verdict = _C_POSITIVE_SFT, 'B+', 'Gut'
    elif _score_pct >= 55: _sc, _grade, _verdict = _C_NEUTRAL, 'B',  'Solide'
    elif _score_pct >= 45: _sc, _grade, _verdict = _C_NEUTRAL, 'C',  'Durchschnittlich'
    elif _score_pct >= 30: _sc, _grade, _verdict = _C_NEGATIVE, 'D',  'Schwach'
    else:                   _sc, _grade, _verdict = _C_NEGATIVE, 'F',  'Ungenügend'

    _sa, _sb = st.columns([1, 2])
    with _sa:
        st.markdown(
            f"<div style='background:{_C_CARD_BG};border:2px solid {_sc}44;border-radius:12px;"
            f"padding:20px 16px;text-align:center;'>"
            f"<div style='color:#78909c;font-size:0.68rem;text-transform:uppercase;"
            f"letter-spacing:.08em;margin-bottom:6px;'>Fundamentaler Score</div>"
            f"<div style='color:{_sc};font-size:3rem;font-weight:900;line-height:1;'>"
            f"{_score}</div>"
            f"<div style='color:{_C_TEXT_MUTED};font-size:0.8rem;margin:4px 0;'>von {_score_max} Punkten</div>"
            f"<div style='background:{_sc}22;border:1px solid {_sc}55;border-radius:20px;"
            f"display:inline-block;padding:3px 14px;margin-top:6px;'>"
            f"<span style='color:{_sc};font-size:1.1rem;font-weight:800;'>{_grade}</span>"
            f"<span style='color:{_sc};font-size:0.8rem;margin-left:6px;'>{_verdict}</span>"
            f"</div></div>",
            unsafe_allow_html=True)
    with _sb:
        for _cn, _cp, _cm, _cl in _score_criteria:
            _bar_pct = int(_cp / _cm * 100)
            _bar_clr = _C_POSITIVE if _bar_pct >= 75 else _C_NEUTRAL if _bar_pct >= 40 else _C_NEGATIVE
            st.markdown(
                f"<div style='margin-bottom:8px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:baseline;"
                f"margin-bottom:3px;'>"
                f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.8rem;font-weight:600;'>{_cn}</span>"
                f"<span style='color:{_bar_clr};font-size:0.78rem;font-weight:700;'>"
                f"{_cp}/{_cm}</span></div>"
                f"<div style='background:#1a2740;border-radius:4px;height:6px;'>"
                f"<div style='background:{_bar_clr};width:{_bar_pct}%;height:6px;"
                f"border-radius:4px;'></div></div>"
                f"<div style='color:{_C_TEXT_MUTED};font-size:0.68rem;margin-top:2px;'>{_cl}</div>"
                f"</div>",
                unsafe_allow_html=True)
    st.caption("Score basiert auf TER, Fondsvolumen, Fondsalter, Replikationsmethode und Streuung. "
               "Keine Anlageberatung. Quelle: yFinance, statische Fondsdaten.")

    # ── Bewertung der Positionen (KGV, P/B, Gewinnwachstum, Verklumpung) ──
    st.markdown("<div class='section-header'>📐 Bewertung der Positionen</div>",
                unsafe_allow_html=True)

    # Verklumpung (Konzentrations-Risiko) aus Top-Holdings
    _top10_pct = None
    _wgt_col_bw = next((c for c in ['holdingPercent','weight','Weight','Holding Percent']
                        if not _th.empty and c in _th.columns), None)
    if _wgt_col_bw and not _th.empty:
        _vals_bw = pd.to_numeric(_th[_wgt_col_bw], errors='coerce').dropna()
        if not _vals_bw.empty:
            _top10_sum = _vals_bw.head(10).sum()
            _top10_pct = _top10_sum * 100 if _top10_sum <= 1 else _top10_sum

    # KGV / Multiples aus equity_holdings
    def _fmt_mult(v, suffix="x"):
        if v is None: return "—"
        try:
            f = float(v)
            return f"{f:.1f}{suffix}" if f < 1000 else "—"
        except Exception: return "—"

    _kgv   = _eq_vals.get('priceToEarnings')
    _kbv   = _eq_vals.get('priceToBook')
    _ksv   = _eq_vals.get('priceToSales')
    _wachs = _eq_vals.get('threeYearEarningsGrowth')
    _mktcp = _eq_vals.get('medianMarketCap')

    # Verklumpungs-Farbe
    def _vklump_clr(pct):
        if pct is None: return '#78909c', '—'
        if pct <= 20:   return _C_POSITIVE, f"{pct:.1f}% — Gut gestreut"
        if pct <= 35:   return _C_NEUTRAL, f"{pct:.1f}% — Moderat"
        return _C_NEGATIVE, f"{pct:.1f}% — Hoch konzentriert"
    _vk_clr, _vk_lbl = _vklump_clr(_top10_pct)

    # KGV-Einschätzung
    def _kgv_clr(v):
        if v is None: return '#78909c'
        f = float(v)
        if f <= 15:  return _C_POSITIVE
        if f <= 25:  return _C_NEUTRAL
        return _C_NEGATIVE

    _g4 = "display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px;"
    st.markdown(
        f"<div style='{_g4}'>"
        + _kc("KGV (P/E)", _fmt_mult(_kgv), "Kurs-Gewinn-Verhältnis", _kgv_clr(_kgv))
        + _kc("P/B Ratio", _fmt_mult(_kbv), "Kurs-Buchwert")
        + _kc("P/S Ratio", _fmt_mult(_ksv), "Kurs-Umsatz")
        + _kc("3J Gewinnwachstum", _fmt_mult(_wachs, "%") if _wachs else "—",
              "Earnings Growth p.a.",
              _C_POSITIVE if (_wachs or 0) > 0 else _C_NEGATIVE)
        + "</div>"
        + f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px;'>"
        + _kc("Verklumpung Top 10",
              f"{_top10_pct:.1f}%" if _top10_pct else "—",
              _vk_lbl if _top10_pct else "Anteil der 10 größten Positionen",
              _vk_clr)
        + _kc("Median Marktkapitalisierung",
              (f"$ {_mktcp/1e9:.1f} Mrd" if (_mktcp or 0) > 1e9
               else f"$ {_mktcp/1e6:.0f} Mio" if _mktcp else "—"),
              "Typische Unternehmensgröße im ETF")
        + "</div>",
        unsafe_allow_html=True)
    if not _eq_vals:
        st.caption("⚠️ Valuation-Daten nicht verfügbar (yFinance liefert für XETRA-ETFs "
                   "oft keine equity_holdings). US-Datenticker wird als Näherung verwendet.")

    _col_a, _col_b = st.columns([1, 1.1])

    with _col_a:
        st.markdown("<div class='section-header'>🥧 Sektoraufteilung</div>", unsafe_allow_html=True)
        _SM = {'technology':'IT & Tech','financial_services':'Finanzen',
               'healthcare':'Gesundheit','consumer_cyclical':'Zyklischer Konsum',
               'industrials':'Industrie','communication_services':'Telekommunikation',
               'consumer_defensive':'Basis-Konsum','energy':'Energie',
               'basic_materials':'Rohstoffe','real_estate':'Immobilien','utilities':'Versorger'}
        _SC = {'IT & Tech':'#1565c0','Finanzen':'#00acc1','Gesundheit':'#43a047',
               'Zyklischer Konsum':'#f9a825','Industrie':'#6d4c41',
               'Telekommunikation':'#7b1fa2','Basis-Konsum':'#2e7d32','Energie':'#e65100',
               'Rohstoffe':'#546e7a','Immobilien':'#00838f','Versorger':'#558b2f'}
        if _sw:
            _sw2 = {_SM.get(k,k): round(v*100,2) for k,v in _sw.items() if v and v > 0}
            _sw2 = dict(sorted(_sw2.items(), key=lambda x: x[1], reverse=True))
            _sf  = go.Figure(go.Pie(
                labels=list(_sw2.keys()), values=list(_sw2.values()), hole=0.62,
                marker=dict(colors=[_SC.get(l,'#546e7a') for l in _sw2],
                            line=dict(color='#0a1628',width=2)),
                textinfo='none',
                hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'))
            _sf.update_layout(template=_C_CHART_THEME,paper_bgcolor=_C_CHART_BG,
                              plot_bgcolor=_C_CHART_BG,showlegend=False,height=240,
                              margin=dict(l=5,r=5,t=5,b=5))
            st.plotly_chart(_sf, use_container_width=True)
            for _sl, _sv in list(_sw2.items())[:10]:
                _sc2 = _SC.get(_sl,'#546e7a')
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;align-items:center;"
                    f"padding:3px 2px;border-bottom:1px solid #1a2740;'>"
                    f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.78rem;'><span style='color:{_sc2};'>●</span>"
                    f" {_sl}</span>"
                    f"<span style='color:{_C_TEXT_MUTED2};font-size:0.78rem;font-weight:600;'>{_sv:.1f}%</span>"
                    f"</div>", unsafe_allow_html=True)
        else:
            st.info("Keine Sektor-Daten verfügbar.")

    with _col_b:
        st.markdown("<div class='section-header'>🏆 Top-Positionen</div>", unsafe_allow_html=True)
        if not _th.empty:
            _th20 = _th.head(20).copy()
            # Spaltennamen ermitteln
            _name_col = next((c for c in ['holdingName','name','Symbol','symbol'] if c in _th20.columns), None)
            _wgt_col  = next((c for c in ['holdingPercent','Holding Percent','weight','Weight'] if c in _th20.columns), None)
            _names   = list(_th20[_name_col]) if _name_col else list(_th20.index)
            _weights = list(_th20[_wgt_col])  if _wgt_col  else [None]*len(_th20)
            for _hi, (_hn, _hw) in enumerate(zip(_names, _weights), 1):
                _hwp = (_hw*100) if isinstance(_hw,float) and _hw <= 1 else (_hw if isinstance(_hw,(int,float)) else 0)
                _bw  = min(int(_hwp*5), 100)
                _bc  = "#1565c0" if _hwp < 5 else _C_NEUTRAL if _hwp < 10 else _C_NEGATIVE
                _lbl = str(_hn)[:26]
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:7px;margin-bottom:5px;'>"
                    f"<div style='color:{_C_TEXT_MUTED};font-size:0.68rem;min-width:18px;text-align:right;'>{_hi}.</div>"
                    f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.78rem;flex:1;white-space:nowrap;"
                    f"overflow:hidden;text-overflow:ellipsis;'>{_lbl}</div>"
                    f"<div style='background:#1a2740;border-radius:3px;width:70px;height:6px;flex-shrink:0;'>"
                    f"<div style='background:{_bc};width:{_bw}%;height:6px;border-radius:3px;'></div></div>"
                    f"<div style='color:{_C_TEXT_PRIMARY};font-size:0.75rem;font-weight:600;min-width:36px;"
                    f"text-align:right;'>{_hwp:.2f}%</div></div>",
                    unsafe_allow_html=True)
        else:
            st.info("Keine Holdings-Daten verfügbar.")

    # ── Regionale Aufteilung ──────────────────────────────────────────────
    if _cw:
        st.markdown("<div class='section-header'>🌍 Regionale Aufteilung</div>",
                    unsafe_allow_html=True)
        # Farben pro Land
        _RC = {
            'USA':'#1565c0','United States':'#1565c0',
            'Deutschland':'#43a047','Germany':'#43a047',
            'Japan':'#e64a19',
            'UK':'#7b1fa2','United Kingdom':'#7b1fa2',
            'Frankreich':'#0097a7','France':'#0097a7',
            'Schweiz':'#c62828','Switzerland':'#c62828',
            'Kanada':'#f57f17','Canada':'#f57f17',
            'Australien':'#00695c','Australia':'#00695c',
            'China':'#d32f2f',
            'Indien':'#f9a825','India':'#f9a825',
            'Südkorea':'#1b5e20','South Korea':'#1b5e20',
            'Taiwan':'#880e4f',
            'Niederlande':'#e65100','Netherlands':'#e65100',
            'Schweden':'#37474f','Sweden':'#37474f',
            'Dänemark':'#006064','Denmark':'#006064',
            'Brasilien':'#bf360c','Brazil':'#bf360c',
            'Saudi-Arabien':'#5d4037','Saudi Arabia':'#5d4037',
            'Sonstige':'#455a64','Other':'#455a64',
        }
        # Werte normalisieren (0–100 %)
        _cw_norm = {}
        for _k, _v in _cw.items():
            try:
                _cw_norm[_k] = float(str(_v).replace('%','').replace(',','.'))
            except Exception:
                pass
        # Entscheidung Dezimal vs. Prozent anhand der Gesamtsumme (nicht pro Wert)
        _cw_sum = sum(_cw_norm.values())
        if _cw_sum < 5:          # Summe ≈ 1 → alle Werte sind Dezimalbrüche
            _cw_norm = {k: v * 100 for k, v in _cw_norm.items()}
        _cw2 = dict(sorted(_cw_norm.items(), key=lambda x: x[1], reverse=True)[:15])

        # Kontinent-Aggregation
        _cont_totals: dict = {}
        for _ck, _cv in _cw2.items():
            _cont = _CONTINENT.get(_ck, 'Sonstige')
            _cont_totals[_cont] = _cont_totals.get(_cont, 0) + _cv
        _cont_totals = dict(sorted(_cont_totals.items(), key=lambda x: x[1], reverse=True))
        _CONT_CLR = {
            'Nordamerika':'#1565c0','Europa':'#00695c','Asien/Pazifik':'#e64a19',
            'Lateinamerika':'#f57f17','Mittlerer Osten':'#5d4037',
            'Afrika':'#6d4c41','Sonstige':'#455a64',
        }

        # Layout: Länderliste links | Kontinent-Donut rechts
        _ra, _rb = st.columns([1.1, 1])
        with _ra:
            st.markdown(f"<div style='color:{_C_ACCENT};font-size:0.72rem;font-weight:600;"
                        "letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px;'>"
                        "Länder</div>", unsafe_allow_html=True)
            for _rk, _rv in list(_cw2.items()):
                _rc2  = _RC.get(_rk, '#546e7a')
                _rbar = min(int(_rv * 2), 100)
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:5px;'>"
                    f"<span style='color:{_rc2};font-size:0.72rem;'>●</span>"
                    f"<span style='color:{_C_TEXT_PRIMARY};font-size:0.76rem;flex:1;'>{_rk[:20]}</span>"
                    f"<div style='background:#1a2740;border-radius:3px;width:60px;height:6px;'>"
                    f"<div style='background:{_rc2};width:{_rbar}%;height:6px;border-radius:3px;'></div></div>"
                    f"<span style='color:{_C_TEXT_MUTED2};font-size:0.75rem;min-width:38px;text-align:right;'>"
                    f"{_rv:.1f}%</span></div>", unsafe_allow_html=True)
        with _rb:
            if len(_cont_totals) > 1:
                st.markdown(f"<div style='color:{_C_ACCENT};font-size:0.72rem;font-weight:600;"
                            "letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px;'>"
                            "Kontinente</div>", unsafe_allow_html=True)
                _rf2 = go.Figure(go.Pie(
                    labels=list(_cont_totals.keys()),
                    values=[round(v, 1) for v in _cont_totals.values()],
                    hole=0.58,
                    marker=dict(colors=[_CONT_CLR.get(k,'#546e7a') for k in _cont_totals],
                                line=dict(color='#0a1628', width=2)),
                    textinfo='none',
                    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'))
                _rf2.update_layout(template=_C_CHART_THEME, paper_bgcolor=_C_CHART_BG,
                                   plot_bgcolor=_C_CHART_BG, showlegend=False, height=210,
                                   margin=dict(l=5, r=5, t=5, b=5))
                st.plotly_chart(_rf2, use_container_width=True)
                for _ck2, _cv2 in list(_cont_totals.items())[:6]:
                    _cclr = _CONT_CLR.get(_ck2, '#546e7a')
                    st.markdown(
                        f"<div style='display:flex;justify-content:space-between;"
                        f"padding:2px 0;border-bottom:1px solid #1a2740;'>"
                        f"<span style='color:{_cclr};font-size:0.74rem;'>● {_ck2}</span>"
                        f"<span style='color:{_C_TEXT_MUTED2};font-size:0.74rem;font-weight:600;'>"
                        f"{_cv2:.1f}%</span></div>", unsafe_allow_html=True)
            else:
                # Einzelner Kontinent / einzelnes Land → einfache Karte
                _rfm = go.Figure(go.Pie(
                    labels=list(_cw2.keys()),
                    values=[round(v, 1) for v in _cw2.values()],
                    hole=0.58,
                    marker=dict(colors=[_RC.get(k,'#546e7a') for k in _cw2],
                                line=dict(color='#0a1628', width=2)),
                    textinfo='none',
                    hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>'))
                _rfm.update_layout(template=_C_CHART_THEME, paper_bgcolor=_C_CHART_BG,
                                   plot_bgcolor=_C_CHART_BG, showlegend=False, height=210,
                                   margin=dict(l=5, r=5, t=5, b=5))
                st.plotly_chart(_rfm, use_container_width=True)

    # ── Benchmark-Vergleich ───────────────────────────────────────────────
    st.markdown("<div class='section-header'>📈 Benchmark-Vergleich</div>", unsafe_allow_html=True)
    _BM_ALL = {
        "MSCI World (SXR8.DE)":"SXR8.DE","FTSE All-World (VWCE.DE)":"VWCE.DE",
        "S&P 500 (SXR2.DE)":"SXR2.DE","NASDAQ-100 (EQQQ.DE)":"EQQQ.DE",
        "DAX (EXS1.DE)":"EXS1.DE","MSCI EM (IS3N.DE)":"IS3N.DE",
    }
    _bm_opts = [k for k,v in _BM_ALL.items() if v != _etf_tkr]
    _bmc1, _bmc2 = st.columns([3,1])
    _bm_sel  = _bmc1.selectbox("Benchmark", _bm_opts, key="etf_bm_sel",
                                label_visibility="collapsed")
    _per_sel = _bmc2.selectbox("Zeitraum", ["1y","3y","5y","10y"], index=1,
                                key="etf_per_sel", label_visibility="collapsed")
    _bm_tkr  = _BM_ALL[_bm_sel]

    with st.spinner("Performance-Daten werden geladen…"):
        _cdf = _etf_vs_bm(_etf_tkr, _bm_tkr, _per_sel)

    if _cdf.empty:
        st.warning("Keine Vergleichsdaten verfügbar.")
    else:
        _fig = go.Figure()
        _clrs_bm = {"#42a5f5":"ETF",_C_NEUTRAL:"Benchmark"}
        _cols_av = [c for c in [_etf_tkr, _bm_tkr] if c in _cdf.columns]
        _lclrs   = ["#42a5f5",_C_NEUTRAL]
        for _ci, _col in enumerate(_cols_av):
            _lbl = (_ei.get('name','')[:28] if _col == _etf_tkr
                    else _bm_sel.split("(")[0].strip())
            _fig.add_trace(go.Scatter(
                x=_cdf.index, y=_cdf[_col].round(2),
                name=_lbl, mode='lines',
                line=dict(color=_lclrs[_ci%2], width=2),
                hovertemplate=f'<b>{_lbl}</b><br>%{{x|%d.%m.%Y}}<br>%{{y:.1f}}<extra></extra>'))
        _fig.update_layout(
            template=_C_CHART_THEME, paper_bgcolor=_C_CHART_BG, plot_bgcolor=_C_CHART_BG,
            height=340, margin=dict(l=10,r=10,t=10,b=10),
            legend=dict(orientation='h',yanchor='bottom',y=1.01,xanchor='right',x=1),
            xaxis=dict(showgrid=False,color='#546e7a'),
            yaxis=dict(showgrid=True,gridcolor='#1a2740',color='#546e7a',
                       title='Indexiert (Start=100)'),
            hovermode='x unified')
        st.plotly_chart(_fig, use_container_width=True)
        # Rendite-Karten
        _rc_cols = st.columns(len(_cols_av))
        for _ci, _col in enumerate(_cols_av):
            _lbl2 = (_ei.get('name','')[:22] if _col == _etf_tkr
                     else _bm_sel.split("(")[0].strip())
            _first = _cdf[_col].dropna().iloc[0] if not _cdf[_col].dropna().empty else 100
            _last  = _cdf[_col].dropna().iloc[-1] if not _cdf[_col].dropna().empty else 100
            _tot   = (_last/_first - 1)*100
            _clr2  = _C_POSITIVE if _tot >= 0 else _C_NEGATIVE
            _rc_cols[_ci].markdown(
                f"<div style='background:{_C_CARD_BG};border:1px solid #1a2740;border-radius:8px;"
                f"padding:12px;text-align:center;'>"
                f"<div style='color:#78909c;font-size:0.68rem;'>{_lbl2}</div>"
                f"<div style='color:{_clr2};font-size:1.3rem;font-weight:700;'>{_tot:+.1f}%</div>"
                f"<div style='color:{_C_TEXT_MUTED};font-size:0.66rem;'>Gesamtrendite ({_per_sel})</div>"
                f"</div>", unsafe_allow_html=True)

    # ── KI-Analyse ────────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🤖 KI-Analyse</div>", unsafe_allow_html=True)

    if not GEMINI_API_KEY:
        st.info("🔑 Kein GEMINI_API_KEY konfiguriert — KI-Analyse nicht verfügbar.")
    else:
        _etf_ki_key = f"etf_ki_{_etf_tkr}"
        _run_etf_ki = st.button("🤖 KI-Analyse starten",
                                key="btn_etf_ki", use_container_width=True, type="primary",
                                help="Gemini analysiert Strategie, Bewertung, Risiken und Marktkontext (~10–20 Sek.)")
        if _run_etf_ki:
            # ── Datenpunkt-Zusammenfassung für den Prompt ─────────────────
            _ki_name   = _ei.get('name', _etf_tkr)
            _ki_ter    = f"{_ei.get('ter',0)*100:.2f}%" if _ei.get('ter') else 'unbekannt'
            _ki_aum    = f"€{_ei.get('aum',0)/1e9:.1f} Mrd." if _ei.get('aum') else 'unbekannt'
            _ki_dist   = _ei.get('distribution', '—')
            _ki_dom    = _ei.get('domicile', '—')
            _ki_cat    = _ei.get('category', '—')
            _ki_ff     = _ei.get('fund_family', '—')
            _ki_ytd    = f"{_ei.get('ytd',0)*100:+.1f}%" if _ei.get('ytd') else '—'
            _ki_1y     = f"{_ei.get('ret_1y',0)*100:+.1f}%" if _ei.get('ret_1y') else '—'
            _ki_3y     = f"{_ei.get('ret_3y',0)*100:+.1f}%" if _ei.get('ret_3y') else '—'
            _ki_5y     = f"{_ei.get('ret_5y',0)*100:+.1f}%" if _ei.get('ret_5y') else '—'
            _ki_factors = ', '.join(t for t, *_ in _factor_tags) if _factor_tags else 'Keine erkannt'
            # Top-Holdings
            _ki_top = ''
            if _th is not None and not _th.empty:
                _ki_name_col = next((c for c in ['holdingName','name','Symbol','symbol'] if c in _th.columns), None)
                _ki_wgt_col  = next((c for c in ['holdingPercent','Holding Percent','weight','Weight'] if c in _th.columns), None)
                _ki_rows = []
                for _, _kirow in _th.head(8).iterrows():
                    _kin = str(_kirow[_ki_name_col])[:30] if _ki_name_col else '—'
                    _kiw = _kirow[_ki_wgt_col] if _ki_wgt_col else None
                    if _kiw is not None:
                        _kiwp = (_kiw * 100) if isinstance(_kiw, float) and _kiw <= 1 else _kiw
                        _ki_rows.append(f"  - {_kin}: {float(_kiwp):.1f}%")
                _ki_top = '\n'.join(_ki_rows)
            # Sektor-Gewichtung (yFinance liefert 0-1-Brüche → *100 für Prozent)
            _ki_sw = ''
            _ki_SM = {'technology':'IT & Tech','financial_services':'Finanzen',
                      'healthcare':'Gesundheit','consumer_cyclical':'Zyklischer Konsum',
                      'industrials':'Industrie','communication_services':'Telekommunikation',
                      'consumer_defensive':'Basis-Konsum','energy':'Energie',
                      'basic_materials':'Rohstoffe','real_estate':'Immobilien','utilities':'Versorger'}
            if _sw:
                _sw_pct = sorted(
                    [(_ki_SM.get(s, s), w * 100 if w <= 1.0 else w) for s, w in _sw.items() if w and w > 0],
                    key=lambda x: x[1], reverse=True
                )
                # Plausibilitäts-Check: Gesamtsumme muss >50% sein, sonst Daten verwerfen
                _sw_total = sum(w for _, w in _sw_pct)
                if _sw_total > 50:
                    _ki_sw = '\n'.join(f"  - {s}: {w:.1f}%" for s, w in _sw_pct[:8])
            # Länder-Gewichtung (kommt bereits als Prozent oder 0-1 — normalisieren)
            _ki_cw = ''
            if _cw:
                _cw_vals = list(_cw.items())
                _cw_scale = 100 if max((v for _, v in _cw_vals), default=1) <= 1.0 else 1
                _cw_sorted = sorted([(c, v * _cw_scale) for c, v in _cw_vals], key=lambda x: x[1], reverse=True)
                _ki_cw = '\n'.join(f"  - {c}: {w:.1f}%" for c, w in _cw_sorted[:8])
            # Bewertungskennzahlen der Positionen (KGV, KBV etc.) — aus _eq_vals (ETF equity_holdings)
            _ki_valuation = ''
            if _eq_vals:
                _pe = _eq_vals.get('priceToEarnings')
                _pb = _eq_vals.get('priceToBook')
                _ps = _eq_vals.get('priceToSales')
                _wg = _eq_vals.get('threeYearEarningsGrowth')
                if _pe and float(_pe) < 200:
                    _ki_valuation += f"  - Ø KGV der Positionen: {float(_pe):.1f}x\n"
                if _pb and float(_pb) < 50:
                    _ki_valuation += f"  - Ø KBV der Positionen: {float(_pb):.2f}x\n"
                if _ps and float(_ps) < 100:
                    _ki_valuation += f"  - Ø KUV der Positionen: {float(_ps):.2f}x\n"
                if _wg:
                    _ki_valuation += f"  - Ø Gewinnwachstum 3J: {float(_wg)*100:.1f}%\n"

            _sys_etf = (
                "Du bist ein unabhängiger ETF-Stratege und Fondsanalyst mit 20 Jahren Erfahrung "
                "in quantitativen Faktorstrategien und Portfoliokonstruktion. Du schreibst prägnant "
                "und verzichtest auf Marketing-Phrasen. Antworte auf Deutsch.\n\n"
                "PFLICHTFORMAT — antworte IMMER in genau diesen 7 Abschnitten in dieser Reihenfolge. "
                "Jeder Abschnitt beginnt mit der exakten Überschrift (ohne # oder *), "
                "gefolgt von 3–5 konkreten Punkten als Stichpunkte mit '- ':\n\n"
                "STRATEGIE & MARKTPHASE\n"
                "KOSTENEFFIZIENZ\n"
                "FUNDAMENTALE BEWERTUNG\n"
                "QUALITÄT & RISIKEN\n"
                "PERFORMANCE-ANALYSE\n"
                "PORTFOLIO-EIGNUNG\n"
                "GESAMTURTEIL\n\n"
                "Wichtig: Beziehe dich auf konkrete Zahlen aus den Datenpunkten. "
                "Wenn Sektor- oder Ländergewichtungen fehlen, nutze dein Wissen über den "
                "zugrundeliegenden Index (z.B. MSCI World, S&P 500) für die Analyse — "
                "weise kurz darauf hin dass Live-Daten nicht verfügbar waren. "
                "Sei kritisch wenn TER hoch, Konzentration groß oder Strategie im aktuellen "
                "Marktumfeld nachteilig ist. Kommentiere niemals Datenpunkte als 'fehlerhaft' — "
                "falls Daten fehlen, ergänze sie aus deinem Indexwissen."
            )
            _usr_etf = (
                f"ETF: {_ki_name} ({_etf_tkr})\n"
                f"Emittent: {_ki_ff} | Kategorie: {_ki_cat} | Domizil: {_ki_dom}\n"
                f"TER: {_ki_ter} | AUM: {_ki_aum} | Ausschüttung: {_ki_dist}\n"
                f"Erkannte Faktoren/Strategie: {_ki_factors}\n\n"
                f"PERFORMANCE:\n"
                f"  YTD: {_ki_ytd} | 1J: {_ki_1y} | 3J: {_ki_3y} | 5J: {_ki_5y}\n\n"
                + (f"FUNDAMENTALE KENNZAHLEN DER POSITIONEN:\n{_ki_valuation}\n" if _ki_valuation else "")
                + (f"TOP-HOLDINGS (bis 8):\n{_ki_top}\n\n" if _ki_top else "")
                + (f"SEKTORGEWICHTUNG:\n{_ki_sw}\n\n" if _ki_sw else "")
                + (f"LÄNDERGEWICHTUNG:\n{_ki_cw}\n\n" if _ki_cw else "")
                + (f"BESCHREIBUNG (Auszug): {_ei.get('description','')[:400]}\n" if _ei.get('description') else "")
                + "\nBitte analysiere diesen ETF anhand der 7 Pflichtabschnitte. "
                  "Gehe explizit auf die Bewertung der Positionen (KGV/KBV-Niveau), "
                  "die Faktorstrategie im aktuellen Marktkontext und die Kostenstruktur ein."
            )
            with st.spinner("KI analysiert ETF… (~10–20 Sek.)"):
                _etf_ki_text, _etf_ki_src = call_ki_api(_sys_etf, _usr_etf, GEMINI_API_KEY, max_tokens=3800)
            st.session_state[_etf_ki_key] = (_etf_ki_text, _etf_ki_src)

        # ── Ergebnis anzeigen ─────────────────────────────────────────────
        if st.session_state.get(_etf_ki_key):
            _etf_ki_text, _etf_ki_src = st.session_state[_etf_ki_key]
            if _etf_ki_src:
                st.caption(f"Analysiert mit {_etf_ki_src}")

            _ETF_KI_SECTIONS = {
                'STRATEGIE & MARKTPHASE':   ('📈', '#42a5f5', '#001a2e'),
                'KOSTENEFFIZIENZ':           ('💸', '#66bb6a', '#00150a'),
                'FUNDAMENTALE BEWERTUNG':    ('⚖️', '#ffd54f', '#1a1200'),
                'QUALITÄT & RISIKEN':        ('🛡', '#ef5350', '#1a0000'),
                'PERFORMANCE-ANALYSE':       ('📊', '#ab47bc', '#150015'),
                'PORTFOLIO-EIGNUNG':         ('🎯', '#26c6da', '#001a1d'),
                'GESAMTURTEIL':              ('🏆', _C_POSITIVE, '#001a0a'),
            }
            # Abschnitte parsen
            _ki_raw = _etf_ki_text.strip()
            _ki_parts: dict[str, str] = {}
            _ki_order = list(_ETF_KI_SECTIONS.keys())
            for _idx, _sec in enumerate(_ki_order):
                _next = _ki_order[_idx + 1] if _idx + 1 < len(_ki_order) else None
                import re as _re_ki
                _pat = _sec.replace('&', r'\&').replace('/', r'\/')
                _m = _re_ki.search(rf'(?:^|\n){_pat}', _ki_raw, _re_ki.IGNORECASE)
                if _m:
                    _start = _m.end()
                    _end   = len(_ki_raw)
                    if _next:
                        _nm = _re_ki.search(rf'(?:^|\n){_next}', _ki_raw[_start:], _re_ki.IGNORECASE)
                        if _nm:
                            _end = _start + _nm.start()
                    _body = _ki_raw[_start:_end].strip()
                    _body = _re_ki.sub(r'\*\*(.*?)\*\*', r'\1', _body)
                    _body = _re_ki.sub(r'#+\s*', '', _body)
                    _ki_parts[_sec] = _body
            if not _ki_parts:
                st.markdown(_ki_raw)
            else:
                for _sec, (_ico, _clr, _bg) in _ETF_KI_SECTIONS.items():
                    _body = _ki_parts.get(_sec, '')
                    if not _body:
                        continue
                    _lines_html = ''.join(
                        f"<div style='display:flex;gap:8px;margin-bottom:5px;'>"
                        f"<span style='color:{_clr};flex-shrink:0;'>•</span>"
                        f"<span style='color:#cfd8dc;font-size:0.84rem;line-height:1.5;'>"
                        f"{ln.lstrip('-•· ').strip()}</span></div>"
                        for ln in _body.splitlines() if ln.strip()
                    )
                    st.markdown(
                        f"<div style='background:{_bg};border:1px solid {_clr}33;"
                        f"border-radius:8px;padding:12px 14px;margin-bottom:8px;'>"
                        f"<div style='color:{_clr};font-size:0.72rem;font-weight:700;"
                        f"text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;'>"
                        f"{_ico} {_sec}</div>{_lines_html}</div>",
                        unsafe_allow_html=True)

            # Follow-up Chat
            st.markdown("---")
            st.caption("💬 Rückfragen zur Analyse:")
            _etf_chat_key = f"etf_chat_{_etf_tkr}"
            with st.form(f"etf_ki_form_{_etf_tkr}", clear_on_submit=True):
                _etf_q = st.text_input("Frage stellen", placeholder="z.B. Wie verhält sich dieser ETF in Rezessionen?",
                                       label_visibility="collapsed")
                if st.form_submit_button("Absenden", use_container_width=True) and _etf_q.strip():
                    _etf_ctx = st.session_state.get(_etf_chat_key, [])
                    _etf_ctx.append({"role": "user", "content": _etf_q.strip()})
                    _etf_reply = call_ki_chat(_sys_etf, _etf_ctx[-8:], GEMINI_API_KEY)
                    _etf_ctx.append({"role": "assistant", "content": _etf_reply})
                    st.session_state[_etf_chat_key] = _etf_ctx
            for _em in st.session_state.get(_etf_chat_key, []):
                if _em["role"] == "user":
                    st.markdown(f"**Du:** {_em['content']}")
                else:
                    st.markdown(f"**KI:** {_em['content']}")

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
    analyst_estimates    = load_analyst_estimates(ticker)
    a_rev, a_net, a_eps, a_fcf, a_shares, a_ebitda, a_capex, a_goodwill, a_debt, a_cash = load_annual_financials(ticker)
    # Segmentdaten: sec-api.io bevorzugt, FMP als Fallback
    _secapi_seg = load_secapi_segments(ticker) if SEC_API_KEY else {"product": [], "geo": []}
    _fmp_seg    = load_segment_data(ticker)
    seg_data = {
        "product": _secapi_seg["product"] or _fmp_seg["product"],
        "geo":     _secapi_seg["geo"]     or _fmp_seg["geo"],
    }

if hist.empty or not yf_info:
    st.markdown(f"""
    <div style="background:{_C_SURFACE}; border:1px solid #ff5252; border-radius:14px; padding:32px 36px; margin:32px 0; text-align:center;">
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
        st.session_state["show_stocks"] = False
        st.session_state["ticker"] = ""
        st.rerun()
    st.stop()

# ==================== DERIVED METRICS ====================
# regularMarketPrice / currentPrice sind bei yfinance ca. 15 Min. verzögert
# und spiegeln den aktuellen Handelstag wider — hist["Close"].iloc[-1] wäre
# nur der letzte gespeicherte Tagesschlusskurs (= Vortag während Handelszeit).
price = (yf_info.get("regularMarketPrice")
         or yf_info.get("currentPrice")
         or (float(hist["Close"].iloc[-1]) if not hist.empty else 0.0))
price_prev = (yf_info.get("regularMarketPreviousClose")
              or yf_info.get("previousClose")
              or (float(hist["Close"].iloc[-2]) if len(hist) > 1 else price))
price_change = price - price_prev
price_change_pct = (price_change / price_prev * 100) if price_prev != 0 else 0

fcf = yf_info.get("freeCashflow")
market_cap = yf_info.get("marketCap")
revenue = yf_info.get("totalRevenue")
fcf_yield = (fcf / market_cap * 100) if fcf and market_cap else None
# Cap extreme FCF Yield: auto/financial conglomerates include finance subsidiaries
# that distort FCF massively (e.g. Toyota Financial Services)
if fcf_yield is not None and abs(fcf_yield) > 100:
    fcf_yield = None
# FCF Margin = FCF / Umsatz (operative Unternehmenskennzahl für Rule of 40)
fcf_margin = (fcf / revenue * 100) if fcf and revenue else None

_rg_raw = yf_info.get("revenueGrowth")
_eg_raw = yf_info.get("earningsGrowth")
_pm_raw = yf_info.get("profitMargins")
_gm_raw = yf_info.get("grossMargins")
_om_raw = yf_info.get("operatingMargins")
rev_growth      = (_rg_raw * 100) if _rg_raw is not None else None
earnings_growth = (_eg_raw * 100) if _eg_raw is not None else None
profit_margin   = (_pm_raw * 100) if _pm_raw is not None else None
gross_margin    = (_gm_raw * 100) if _gm_raw is not None else None
operating_margin = (_om_raw * 100) if _om_raw is not None else None
# Rule of 40 = Rev Growth % + FCF Margin % (Branchenstandard für SaaS)
rule_of_40 = (rev_growth + fcf_margin) if (fcf_margin is not None and rev_growth is not None) else None

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

# ── Currency symbol (JPY, EUR, GBP, … → use correct symbol everywhere) ───
_currency = yf_info.get("currency", "USD") or "USD"
_cur_sym = {
    "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CNY": "¥",
    "CHF": "Fr.", "HKD": "HK$", "CAD": "CA$", "AUD": "A$",
    "KRW": "₩", "SEK": "kr", "NOK": "kr", "DKK": "kr",
    "TWD": "NT$", "SGD": "S$", "INR": "₹", "BRL": "R$",
    "MXN": "MX$", "ZAR": "R", "TRY": "₺", "ILS": "₪",
}.get(_currency, _currency + " ")

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
total_shareholder_yield = (fcf_yield + dividend_yield) if (fcf_yield is not None) else (dividend_yield if dividend_yield else None)
earnings_ts = yf_info.get("earningsTimestamp") or yf_info.get("earningsDate")
earnings_date_str = ""
earnings_days_until = None
try:
    from datetime import datetime, date as _date
    if isinstance(earnings_ts, (int, float)) and earnings_ts > 0:
        _edt = datetime.fromtimestamp(earnings_ts).date()
        earnings_date_str = _edt.strftime("%d.%m.%Y")
        _days = (_edt - _date.today()).days
        if 0 <= _days <= 90:
            earnings_days_until = _days
    elif isinstance(earnings_ts, list) and earnings_ts:
        _edt = pd.Timestamp(earnings_ts[0]).date()
        earnings_date_str = _edt.strftime("%d.%m.%Y")
        _days = (_edt - _date.today()).days
        if 0 <= _days <= 90:
            earnings_days_until = _days
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

# ── Pre-compute header badge HTML ───────────────────────────────────────────
_earnings_badge = ""
if earnings_date_str:
    if earnings_days_until is not None:
        if earnings_days_until == 0:
            _ed_label = "📅 Earnings heute"
        elif earnings_days_until == 1:
            _ed_label = "📅 Earnings morgen"
        else:
            _ed_label = f"📅 Earnings in {earnings_days_until} Tagen"
        _ed_txt_color = "#ff6f00" if earnings_days_until <= 7 else _C_NEUTRAL if earnings_days_until <= 14 else _C_POSITIVE
        _ed_bg_color  = "#2d1800" if earnings_days_until <= 7 else "#2d2600" if earnings_days_until <= 14 else "#1a2e1a"
        _earnings_badge = (
            f'<span style="background:{_ed_bg_color}; color:{_ed_txt_color}; border-radius:6px;'
            f' padding:3px 10px; font-size:0.78rem; font-weight:600;">'
            f'{_ed_label} ({earnings_date_str})</span>'
        )
    else:
        _earnings_badge = (
            f'<span style="background:#1a2e1a; color:#00e676; border-radius:6px;'
            f' padding:3px 10px; font-size:0.78rem; font-weight:600;">'
            f'📅 Earnings: {earnings_date_str}</span>'
        )

_target_badge = ""
if upside is not None and target_mean:
    _udir    = "+" if upside > 0 else ""
    _ucolor  = _C_POSITIVE if upside > 10 else _C_NEUTRAL if upside > 0 else _C_NEGATIVE
    _ubg     = "#1a2e1a" if upside > 10 else "#2a2200" if upside > 0 else "#2d1a1a"
    _target_badge = (
        f'<span style="background:{_ubg}; color:{_ucolor}; border-radius:6px;'
        f' padding:3px 10px; font-size:0.78rem; font-weight:600;">'
        f'🎯 Kursziel {_cur_sym}{target_mean:.2f} ({_udir}{upside:.1f}%)</span>'
    )

# ==================== HEADER ====================
change_class = "header-change-pos" if price_change >= 0 else "header-change-neg"
change_arrow = "▲" if price_change >= 0 else "▼"
company_name = yf_info.get("longName", ticker)

# HTML-escape user-visible strings to prevent rendering raw HTML from yfinance data
def _he(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;") if s else ""
_company_name_h = _he(company_name)
_sector_h       = _he(sector)
_industry_h     = _he(industry)

# Logo HTML — FMP Image-Endpoint direkt einbinden
initials = "".join(w[0] for w in company_name.split()[:2]).upper() if company_name else ticker[:2]
logo_html = f"""
<div style="position:relative;height:52px;width:52px;margin-right:16px;flex-shrink:0;">
    <div style="position:absolute;inset:0;background:#1a3a5c;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:700;color:{_C_ACCENT};">{initials}</div>
    <img src="{logo_url}" style="position:absolute;inset:0;height:52px;width:52px;border-radius:8px;background:#fff;padding:4px;object-fit:contain;"
         onerror="this.style.visibility='hidden'">
</div>"""

st.markdown(f"""
<div class="header-wrap">
    <div style="display:flex; align-items:center; flex:1; min-width:0;">
        {logo_html}
        <div style="min-width:0; flex:1;">
            <div class="header-title" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{_company_name_h}</div>
            <div class="header-sub">{ticker} · {_sector_h} · {_industry_h}</div>
            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                <span style="background:#1a2744; color:{_C_ACCENT}; border-radius:6px; padding:3px 10px; font-size:0.8rem; font-weight:600;">{recommendation}</span>
                {_earnings_badge}
                {_target_badge}
            </div>
            <div style="margin-top:12px;">
                <div class="header-price" style="font-size:1.8rem; text-align:left;">{_cur_sym}{price:.2f}</div>
                <div class="{change_class}">{change_arrow} {_cur_sym}{abs(price_change):.2f} ({abs(price_change_pct):.2f}%)</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

import datetime as _dtnow
_now_str = _dtnow.datetime.now().strftime("%H:%M Uhr")
st.markdown(
    f"<div style='color:#37474f;font-size:0.7rem;margin:-8px 0 10px 0;'>"
    f"⏱ Kursdaten via Yahoo Finance · ca. 15–20 Min. verzögert · Keine Echtzeitkurse · "
    f"Geladen: {_now_str} · Cache max. 5 Min.</div>",
    unsafe_allow_html=True)

# ── Quick Links: Homepage + IR + Geschäftsbericht ─────────────────
_hdr_website  = yf_info.get("website", "") or ""
_hdr_exchange = (yf_info.get("exchange", "") or "").upper()
_hdr_is_us    = _hdr_exchange in ("NYQ", "NMS", "NGM", "NCM", "ASE", "PCX", "NYS", "NASDAQ", "NYSE")
_hdr_links    = []
_btn_base     = ("text-decoration:none;font-weight:600;font-size:0.8rem;"
                 "padding:4px 11px;border-radius:7px;white-space:nowrap;display:inline-block;")
if _hdr_website:
    _hdr_links.append(
        f"<a href='{_hdr_website}' target='_blank' rel='noopener' "
        f"style='color:{_C_ACCENT};background:rgba(100,181,246,0.12);"
        f"border:1px solid rgba(100,181,246,0.28);{_btn_base}'>🌐 Homepage</a>"
    )
    _hdr_ir = _hdr_website.rstrip("/") + "/investor-relations"
    _hdr_links.append(
        f"<a href='{_hdr_ir}' target='_blank' rel='noopener' "
        f"style='color:{_C_POSITIVE_SFT};background:rgba(105,240,174,0.10);"
        f"border:1px solid rgba(105,240,174,0.25);{_btn_base}'>📊 Investor Relations</a>"
    )
if _hdr_is_us:
    _hdr_cik = _sec_cik(ticker)
    if _hdr_cik:
        _hdr_edgar = (f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
                      f"&CIK={_hdr_cik}&type=10-K&dateb=&owner=include&count=5")
        _hdr_links.append(
            f"<a href='{_hdr_edgar}' target='_blank' rel='noopener' "
            f"style='color:{_C_NEUTRAL};background:rgba(255,214,0,0.10);"
            f"border:1px solid rgba(255,214,0,0.28);{_btn_base}'>📄 SEC 10-K</a>"
        )
else:
    # Non-US: link to Yahoo Finance filings page as annual report fallback
    _hdr_links.append(
        f"<a href='https://finance.yahoo.com/quote/{ticker}/financials/' target='_blank' rel='noopener' "
        f"style='color:{_C_NEUTRAL};background:rgba(255,214,0,0.10);"
        f"border:1px solid rgba(255,214,0,0.28);{_btn_base}'>📄 Finanzdaten</a>"
    )
if _hdr_links:
    st.markdown(
        "<div style='display:flex;flex-wrap:wrap;gap:7px;margin:4px 0 12px 0;'>"
        + "".join(_hdr_links) + "</div>",
        unsafe_allow_html=True,
    )

# ── Watchlist-Button + Refresh ─────────────────────────────────────
_wl_curr = st.session_state.get("watchlist", [])
_in_wl   = any(w["ticker"] == ticker for w in _wl_curr)
_wl_b1, _wl_b2, _ = st.columns([1, 1, 5])
with _wl_b1:
    if _in_wl:
        if st.button("✅ Gemerkt", key="wl_rm", help="Aus Watchlist entfernen"):
            st.session_state["watchlist"] = [w for w in _wl_curr if w["ticker"] != ticker]
            _wl_save_file(st.session_state["watchlist"])
            st.rerun()
    else:
        if st.button("⭐ Merken", key="wl_add", help="Zur Watchlist hinzufügen"):
            st.session_state["watchlist"] = _wl_curr + [{"ticker": ticker, "name": company_name}]
            _wl_save_file(st.session_state["watchlist"])
            st.rerun()
with _wl_b2:
    if st.button("🔄 Aktualisieren", key="refresh_data",
                 help="Kurs und Daten sofort neu laden (Cache leeren)"):
        load_yfinance.clear()
        load_fmp_metrics.clear()
        load_analyst_estimates.clear()
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

def mini_card(label, value, good, ok, fmt=".1f", suffix="", inverse=False, tooltip=None, bench=None):
    b = badge(value, good, ok, fmt, inverse)
    val_str = f"{value:{fmt}}{suffix}" if value is not None else "N/A"
    tip = tooltip or _METRIC_TOOLTIPS.get(label, "")
    tip_html = ""
    if tip:
        tip_safe = tip.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        tip_html = (
            f'<div class="mcard-tip-wrap">'
            f'<span class="mcard-tip-icon" tabindex="0">?</span>'
            f'<div class="mcard-tip-bubble">{tip_safe}</div>'
            f'</div>'
        )
    bench_html = ""
    if bench is not None and value is not None:
        _bdiff = value - bench
        _bdir  = "+" if _bdiff >= 0 else ""
        _bc    = _C_POSITIVE if _bdiff >= 0 else _C_NEGATIVE
        bench_html = (
            f'<div style="margin-top:3px; font-size:0.67rem; color:{_C_TEXT_MUTED};">'
            f'Sektor ∅ {bench:{fmt}}{suffix}'
            f' <span style="color:{_bc};">({_bdir}{_bdiff:{fmt}})</span>'
            f'</div>'
        )
    return (
        f'<div class="metric-card" style="position:relative;">'
        f'{tip_html}'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{val_str}</div>'
        f'<div style="margin-top:6px;">{b}</div>'
        f'{bench_html}'
        f'</div>'
    )

_sb = SECTOR_BENCHMARKS.get(sector, {})
if show_rule_of_40:
    with col_r40:
        st.markdown(mini_card("Rule of 40", rule_of_40, 40, 20, ".1f", "%"), unsafe_allow_html=True)
with col_roic:
    st.markdown(mini_card("ROIC", roic_val, 20, 10, ".1f", "%", bench=_sb.get("ROIC")), unsafe_allow_html=True)
with col_fcf:
    st.markdown(mini_card("FCF Yield", fcf_yield, 5, 2, ".1f", "%", bench=_sb.get("FCF Yield")), unsafe_allow_html=True)
with col_gm:
    st.markdown(mini_card("Gross Margin", gross_margin, 60, 40, ".1f", "%", bench=_sb.get("Bruttomarge")), unsafe_allow_html=True)
if not show_rule_of_40:
    with col_rev:
        st.markdown(mini_card("Rev. Growth", rev_growth, 15, 5, ".1f", "%", bench=_sb.get("Umsatzwachstum")), unsafe_allow_html=True)

# ==================== SCORE-BREAKDOWN ====================
with st.expander("📊 Score-Breakdown — Warum dieser Score?", expanded=False):
    _bd_items = []
    if show_rule_of_40:
        _bd_items.append(("Rule of 40", rule_of_40, 40, 20, 20, "%", False))
    _bd_items += [
        ("Bruttomarge",   gross_margin,     60,  40, 15, "%", False),
        ("ROIC",          roic_val,         20,  10, 15, "%", False),
        ("Umsatzwachstum",rev_growth,       15,   5, 12, "%", False),
        ("FCF Yield",     fcf_yield,         5,   2, 12, "%", False),
        ("Gewinnmarge",   profit_margin,    15,   5, 10, "%", False),
        ("Op. Marge",     operating_margin, 20,  10,  8, "%", False),
        ("PEG Ratio",     peg_ratio,       1.5, 2.5,  8, "x", True),
    ]
    _bd_rows = []
    for _lbl, _val, _good, _ok, _w, _sfx, _inv in _bd_items:
        if _val is None:
            _icon, _pts, _rc = "➖", 0, "#546e7a"
            _val_str = "N/A"
        elif (_inv and _val <= _good) or (not _inv and _val >= _good):
            _icon, _pts, _rc = "✅", _w, _C_POSITIVE
            _val_str = f"{_val:.1f}{_sfx}"
        elif (_inv and _val <= _ok) or (not _inv and _val >= _ok):
            _icon, _pts, _rc = "🟡", _w // 2, _C_NEUTRAL
            _val_str = f"{_val:.1f}{_sfx}"
        else:
            _icon, _pts, _rc = "❌", 0, _C_NEGATIVE
            _val_str = f"{_val:.1f}{_sfx}"
        _thresh_str = (f"≤{_good}{_sfx}" if _inv else f"≥{_good}{_sfx}")
        _bd_rows.append((_icon, _lbl, _val_str, _thresh_str, _pts, _w, _rc))
    _bd_html = (
        '<table style="width:100%;border-collapse:collapse;font-size:0.82rem;">'
        '<tr style="color:{_C_TEXT_MUTED};border-bottom:1px solid #1e3a5f;">'
        '<th style="text-align:left;padding:4px 6px;"></th>'
        '<th style="text-align:left;padding:4px 6px;">Kriterium</th>'
        '<th style="text-align:right;padding:4px 6px;">Wert</th>'
        '<th style="text-align:right;padding:4px 6px;">Ziel</th>'
        '<th style="text-align:right;padding:4px 6px;">Punkte</th>'
        '</tr>'
    )
    for _icon, _lbl, _val_str, _thresh_str, _pts, _w, _rc in _bd_rows:
        _bd_html += (
            f'<tr style="border-bottom:1px solid #0d1526;">'
            f'<td style="padding:5px 6px;">{_icon}</td>'
            f'<td style="padding:5px 6px;color:{_C_TEXT_PRIMARY};">{_lbl}</td>'
            f'<td style="padding:5px 6px;text-align:right;color:{_rc};font-weight:600;">{_val_str}</td>'
            f'<td style="padding:5px 6px;text-align:right;color:{_C_TEXT_MUTED};">{_thresh_str}</td>'
            f'<td style="padding:5px 6px;text-align:right;color:{_rc};">{_pts}/{_w}</td>'
            f'</tr>'
        )
    _bd_html += f'</table><div style="margin-top:8px;color:{_C_TEXT_MUTED};font-size:0.75rem;">Score = erzielte Punkte / max. Punkte × 100 — aktuell: {quality_score}/100</div>'
    st.markdown(_bd_html, unsafe_allow_html=True)

# ==================== 52-WEEK BAR ====================
if week52_pos is not None:
    bar_color = _C_POSITIVE if week52_pos > 70 else _C_NEUTRAL if week52_pos > 30 else _C_NEGATIVE
    _dist_to_high_pct = ((week52_high - price) / price * 100) if week52_high and price else None
    if week52_pos >= 90:
        _52w_label, _52w_label_color = "Nahe Jahreshoch", "#ff6f00"
    elif week52_pos >= 70:
        _52w_label, _52w_label_color = "Oberes Drittel", _C_POSITIVE
    elif week52_pos >= 30:
        _52w_label, _52w_label_color = "Mid-Range", _C_NEUTRAL
    elif week52_pos >= 10:
        _52w_label, _52w_label_color = "Unteres Drittel", "#ff7043"
    else:
        _52w_label, _52w_label_color = "Nahe Jahrestief", _C_NEGATIVE
    _dist_html = (f' · <span style="color:#78909c;">noch {_dist_to_high_pct:.1f}% bis Jahreshoch</span>'
                  if _dist_to_high_pct and _dist_to_high_pct > 0.5 else "")
    st.markdown(f"""
    <div style="background:{_C_SURFACE}; border:1px solid #1e3a5f; border-radius:14px; padding:16px 22px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="color:#78909c; font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:1px;">52-Wochen Range</span>
            <span style="font-size:0.82rem;">
                <span style="color:{_52w_label_color}; font-weight:700;">{_52w_label}</span>
                <span style="color:{_C_ACCENT}; font-weight:600;"> · {week52_pos:.0f}% vom Tief</span>
                {_dist_html}
            </span>
        </div>
        <div style="background:#1e2d45; border-radius:8px; height:8px; position:relative;">
            <div style="background:{bar_color}; width:{week52_pos:.0f}%; height:100%; border-radius:8px;"></div>
            <div style="position:absolute; top:-4px; left:{week52_pos:.0f}%; transform:translateX(-50%);">
                <div style="background:{bar_color}; width:16px; height:16px; border-radius:50%; border:2px solid #080d18;"></div>
            </div>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:8px;">
            <span style="color:{_C_TEXT_MUTED}; font-size:0.78rem;">{_cur_sym}{week52_low:.2f} Tief</span>
            <span style="color:{_C_TEXT_PRIMARY}; font-size:0.85rem; font-weight:600;">{_cur_sym}{price:.2f}</span>
            <span style="color:{_C_TEXT_MUTED}; font-size:0.78rem;">Hoch {_cur_sym}{week52_high:.2f}</span>
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
            "Kurs":         f"{_cur_sym}{_d['price']:.2f}" if _d.get("price") else "—",
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
    _cmp_colors  = ["#00e5ff", "#a78bfa", _C_POSITIVE, _C_NEUTRAL, "#ff9100",
                    _C_NEGATIVE, "#64b5f6", _C_POSITIVE_SFT, "#ff80ab"]
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
        template=_C_CHART_THEME,
        paper_bgcolor=_C_CHART_PAPER,
        plot_bgcolor=_C_CHART_PLOT,
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
            "BULL CASE":        ("🟢", _C_POSITIVE),
            "BEAR CASE":        ("🔴", _C_NEGATIVE),
            "INVESTMENT THESE": ("💡", _C_NEUTRAL),
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
            f"<div style='color:{_C_TEXT_MUTED};font-size:0.75rem;'>Powered by {_provider_label}</div>"
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
                                  min(max(rev_growth or 3, 3), 30), 2.5, 10, 10)

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
        fv_color = _C_POSITIVE if dcf_fair_val > price else _C_NEGATIVE
        fig.add_hline(y=dcf_fair_val, line_dash="dot", line_color=fv_color, line_width=2,
                      annotation_text=f"DCF Fair Value {_cur_sym}{dcf_fair_val:.0f}",
                      annotation_font_color=fv_color, row=1, col=1)

    # Analyst target line
    if target_mean:
        fig.add_hline(y=target_mean, line_dash="dot", line_color=_C_NEUTRAL, line_width=1.5,
                      annotation_text=f"Analyst Ziel ${target_mean:.0f}",
                      annotation_font_color=_C_NEUTRAL, row=1, col=1)

    # Volume
    colors_vol = [_C_POSITIVE if c >= o else _C_NEGATIVE
                  for c, o in zip(hist_plot["Close"], hist_plot["Open"])]
    fig.add_trace(go.Bar(
        x=hist_plot.index, y=hist_plot["Volume"],
        name="Volumen", marker_color=colors_vol, opacity=0.6,
        showlegend=False
    ), row=2, col=1)

    fig.update_layout(
        template=_C_CHART_THEME,
        paper_bgcolor=_C_CHART_PAPER,
        plot_bgcolor=_C_CHART_PLOT,
        height=580,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor=_C_CHART_PLOT,
            bordercolor=_C_BORDER, borderwidth=1,
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

    dcf_text = f" | DCF Fair Value: <strong style='color:{_C_POSITIVE if dcf_fair_val and dcf_fair_val > price else _C_NEGATIVE}'>{_cur_sym}{dcf_fair_val:.2f}</strong>" if dcf_fair_val else ""
    st.markdown(f"""
    <div class="insight-box">
        <strong>📊 Chart-Analyse:</strong> {ticker} notiert aktuell
        <strong style="color:{_C_NEGATIVE if pos_sigma > 1 else _C_POSITIVE if pos_sigma < -1 else _C_NEUTRAL}">
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
        "eps":            (_ex_eps,    lambda v: f"{_cur_sym}{v:.2f}",  ""),
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
    line_colors = [_C_POSITIVE if v >= 0 else _C_NEGATIVE for v in growth_clean.values]

    _note = f" · {len(labels_abs)} Jahre" + ("" if FMP_API_KEY else " (ohne FMP_API_KEY: max. 4–5 Jahre)")
    st.caption(f"**{title}** — {tkr}{_note}")

    if metric == "price":
        fig = go.Figure(go.Bar(
            x=labels_abs, y=s.values,
            marker_color=[_C_POSITIVE if v >= 0 else _C_NEGATIVE for v in s.values],
            text=[f"{v:+.1f}%" for v in s.values],
            textposition="outside", textfont=dict(size=12, color="#90a4ae"),
        ))
        fig.add_hline(y=0, line_color="#1e3a5f", line_width=1)
        fig.update_layout(
            template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
            plot_bgcolor=_C_CHART_PLOT, height=420,
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
            mode="lines+markers+text", line=dict(color=_C_NEUTRAL, width=2.5),
            marker=dict(size=8, color=line_colors, line=dict(color=_C_NEUTRAL, width=1.5)),
            text=[f"{v:+.1f}%" for v in growth_clean.values],
            textposition="top center", textfont=dict(size=10, color=_C_NEUTRAL),
        ), secondary_y=True)
    fig.add_hline(y=0, line_color="#1e3a5f", line_width=1, secondary_y=False)
    fig.update_layout(
        template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
        plot_bgcolor=_C_CHART_PLOT, height=460,
        margin=dict(l=10, r=60, t=30, b=10),
        legend=dict(orientation="h", y=1.08, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False),
    )
    fig.update_yaxes(showgrid=True, gridcolor="#1e2d45", secondary_y=False)
    fig.update_yaxes(ticksuffix="%", showgrid=False, title_text="YoY Wachstum %",
                     title_font=dict(color=_C_NEUTRAL), tickfont=dict(color=_C_NEUTRAL),
                     secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)


# ==================== NAVIGATION ====================
# Session-state-basierte Navigation (immun gegen st.rerun() und WebSocket-Reconnects)
_TABS = [
    "📊 Kennzahlen", "📈 Wachstum", "🔮 Prognose", "📋 Fundamental", "⚖️ Bewertung",
    "🔬 Piotroski", "🏰 Burggraben", "📉 Chart", "🔍 Insider", "📰 News",
]
_at = st.session_state.get("active_tab", 0)
_nav_cols = st.columns(len(_TABS))
_tab_clicked = False
for _ni, (_nc, _nl) in enumerate(zip(_nav_cols, _TABS)):
    if _nc.button(_nl, key=f"_nav_{_ni}", use_container_width=True,
                  type="primary" if _at == _ni else "secondary"):
        if _at != _ni:
            st.session_state["active_tab"] = _ni
            _tab_clicked = True
if _tab_clicked:
    st.rerun()
_at = st.session_state.get("active_tab", 0)
st.markdown(f"<div style='border-top:2px solid {_C_BORDER};margin:-6px 0 12px 0;'></div>",
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
        _ebitda_str = fmt_large(ebitda, _cur_sym) if ebitda else "N/A"
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

    # ── Dividenden-Scorecard ──────────────────────────────────────────
    _payout_ratio = (yf_info.get("payoutRatio") or 0) * 100
    _annual_div   = yf_info.get("trailingAnnualDividendRate") or 0
    _ex_div_ts    = yf_info.get("exDividendDate")
    _ex_div_str   = ""
    try:
        if isinstance(_ex_div_ts, (int, float)) and _ex_div_ts > 0:
            from datetime import datetime as _dtx
            _ex_div_str = _dtx.fromtimestamp(_ex_div_ts).strftime("%d.%m.%Y")
    except Exception:
        pass
    _div_streak = _DIVIDEND_POOL.get(ticker.upper())  # (desc, years) or None

    if dividend_yield > 0 or _annual_div > 0:
        st.markdown("<div class='section-header'>💰 Dividenden-Scorecard</div>", unsafe_allow_html=True)
        _dsc1, _dsc2, _dsc3, _dsc4 = st.columns(4)
        _dy_label = "Dividend Yield ⚠️" if _div_yield_suspicious else "Dividend Yield"
        _dy_tooltip = "Wert >15 % — bitte manuell prüfen (möglicher Datenfehler)" if _div_yield_suspicious else None
        with _dsc1:
            st.markdown(mini_card(_dy_label, dividend_yield, 3, 1, ".2f", "%", tooltip=_dy_tooltip), unsafe_allow_html=True)
        with _dsc2:
            st.markdown(mini_card("Payout Ratio", _payout_ratio if _payout_ratio > 0 else None,
                                  0, 60, ".0f", "%", inverse=True,
                                  tooltip="Ausschüttungsquote: <60% = nachhaltig, >90% = potenziell gefährdet."), unsafe_allow_html=True)
        with _dsc3:
            _ann_str = f"{_cur_sym}{_annual_div:.2f}" if _annual_div else "N/A"
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">Jährl. Dividende</div>'
                f'<div class="metric-value">{_ann_str}</div>'
                f'<div style="margin-top:6px;"><span class="metric-badge-gray">je Aktie</span></div>'
                f'</div>', unsafe_allow_html=True)
        with _dsc4:
            if _div_streak:
                _streak_years = _div_streak[1]
                _streak_title = "Dividend King" if _streak_years >= 50 else "Dividend Aristocrat" if _streak_years >= 25 else "Wachstums-Dividende"
                _streak_color = _C_NEUTRAL if _streak_years >= 50 else _C_POSITIVE if _streak_years >= 25 else "#64b5f6"
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Dividenden-Serie</div>'
                    f'<div class="metric-value" style="color:{_streak_color};">{_streak_years}J</div>'
                    f'<div style="margin-top:6px;"><span style="color:{_streak_color};font-size:0.75rem;font-weight:700;">{_streak_title}</span></div>'
                    f'</div>', unsafe_allow_html=True)
            elif _ex_div_str:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Ex-Dividende</div>'
                    f'<div class="metric-value" style="font-size:1rem;">{_ex_div_str}</div>'
                    f'<div style="margin-top:6px;"><span class="metric-badge-gray">letztes Datum</span></div>'
                    f'</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">Ex-Dividende</div>'
                    f'<div class="metric-value" style="font-size:1rem;">N/A</div>'
                    f'<div style="margin-top:6px;"><span class="metric-badge-gray">–</span></div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        _dy_c1, _dy_c2 = st.columns([1, 4])
        with _dy_c1:
            st.markdown(mini_card("Dividend Yield", None, 3, 1, ".2f", "%",
                                  tooltip="Keine Dividende bekannt."), unsafe_allow_html=True)

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
                _colors.append(_C_POSITIVE)
            elif _sv >= _bv * 0.85:
                _colors.append(_C_NEUTRAL)
            else:
                _colors.append(_C_NEGATIVE)

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
            template=_C_CHART_THEME,
            paper_bgcolor=_C_CHART_PAPER,
            plot_bgcolor=_C_CHART_PLOT,
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
            st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">{fallback_msg}</div>',
                        unsafe_allow_html=True)

    # Growth sparkline (if hist available)
    if len(hist) > 252:
        annual = hist["Close"].resample("YE").last().pct_change().dropna() * 100
        if len(annual) >= 2:
            fig_g = go.Figure(go.Bar(
                x=[str(y.year) for y in annual.index],
                y=annual.values,
                marker_color=[_C_POSITIVE if v >= 0 else _C_NEGATIVE for v in annual.values],
                text=[f"{v:.1f}%" for v in annual.values],
                textposition="outside",
            ))
            fig_g.update_layout(
                template=_C_CHART_THEME,
                paper_bgcolor=_C_CHART_PAPER,
                plot_bgcolor=_C_CHART_PLOT,
                height=280,
                margin=dict(l=0, r=0, t=20, b=0),
                showlegend=False,
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=True, zerolinecolor="#1e2d45"),
                xaxis=dict(showgrid=False),
                title=dict(text="Jährliche Kursperformance", font=dict(color="#64b5f6", size=13)),
            )
            st.plotly_chart(fig_g, use_container_width=True)
            if st.button("📊 Detailansicht", key="exp_price", use_container_width=False):
                st.session_state["wachstum_expanded"] = ("price", ticker, "Jährliche Kursperformance", _C_POSITIVE, _C_NEGATIVE)

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
            template=_C_CHART_THEME,
            paper_bgcolor=_C_CHART_PAPER,
            plot_bgcolor=_C_CHART_PLOT,
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
        _show_chart(_bar_chart(a_rev, "Umsatzwachstum YoY", _C_POSITIVE, _C_NEGATIVE),
                    "revenue_growth", "Umsatzwachstum YoY", _C_POSITIVE, _C_NEGATIVE,
                    "Keine Jahres-Umsatzdaten verfügbar.")
    with _gc2:
        _show_chart(_bar_chart(a_net, "Nettogewinnwachstum YoY", _C_POSITIVE, _C_NEGATIVE),
                    "net_growth", "Nettogewinnwachstum YoY", _C_POSITIVE, _C_NEGATIVE,
                    "Keine Jahres-Gewinndaten verfügbar.")

    _gc3, _gc4 = st.columns(2)
    with _gc3:
        _show_chart(_bar_chart(a_rev, "Umsatz absolut", "#1565c0", "#1565c0",
                               is_growth=False, value_fmt=lambda v: fmt_large(v)),
                    "revenue", "Umsatz absolut", "#1565c0", "#1565c0")
    with _gc4:
        if not a_eps.empty and len(a_eps) >= 2:
            _show_chart(_bar_chart(a_eps, "EPS (Diluted) — Trend", "#00e5ff", _C_NEGATIVE,
                                   is_growth=False, value_fmt=lambda v: f"{_cur_sym}{v:.2f}"),
                        "eps", "EPS (Diluted)", "#00e5ff", _C_NEGATIVE)
        elif not a_net.empty:
            _show_chart(_bar_chart(a_net, "Nettogewinn absolut", "#64b5f6", _C_NEGATIVE,
                                   is_growth=False, value_fmt=lambda v: fmt_large(v)),
                        "net", "Nettogewinn absolut", "#64b5f6", _C_NEGATIVE)

    _gc5, _gc6 = st.columns(2)
    with _gc5:
        _show_chart(_bar_chart(a_fcf, "Free Cash Flow absolut", "#26a69a", "#ef5350",
                               is_growth=False, value_fmt=lambda v: fmt_large(v)),
                    "fcf", "Free Cash Flow absolut", "#26a69a", "#ef5350",
                    "Keine FCF-Daten verfügbar.")
    with _gc6:
        _show_chart(_bar_chart(a_fcf, "Free Cash Flow Wachstum YoY", _C_POSITIVE, _C_NEGATIVE),
                    "fcf_growth", "FCF Wachstum YoY", _C_POSITIVE, _C_NEGATIVE)

    # EBITDA-Zeile
    _gc7, _gc8 = st.columns(2)
    with _gc7:
        _show_chart(_bar_chart(a_ebitda, "EBITDA absolut", "#7986cb", "#ef5350",
                               is_growth=False, value_fmt=lambda v: fmt_large(v)),
                    "ebitda", "EBITDA absolut", "#7986cb", "#ef5350",
                    "Keine EBITDA-Daten verfügbar.")
    with _gc8:
        _show_chart(_bar_chart(a_ebitda, "EBITDA Wachstum YoY", _C_POSITIVE, _C_NEGATIVE),
                    "ebitda_growth", "EBITDA Wachstum YoY", _C_POSITIVE, _C_NEGATIVE)

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
                f"<h4 style='color:{_C_ACCENT};margin:4px 0;'>📊 {_exp_title} — Detailansicht</h4>",
                unsafe_allow_html=True)
        _render_expanded_chart(_exp_ticker, _exp_metric, _exp_title, _exp_cp, _exp_cn)
        st.markdown("---")

    # ── Segment-Aufschlüsselung ────────────────────────────────────────
    st.markdown("<div class='section-header'>🥧 Umsatz nach Segment</div>", unsafe_allow_html=True)
    _seg_colors = ["#00e5ff","#a78bfa",_C_POSITIVE,_C_NEUTRAL,_C_NEGATIVE,
                   "#f59e0b","#64b5f6","#f48fb1",_C_POSITIVE_SFT,"#ce93d8",
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
                template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
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
                    barmode="stack", template=_C_CHART_THEME,
                    paper_bgcolor=_C_CHART_PAPER, plot_bgcolor=_C_CHART_PLOT,
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
                    f"<h4 style='color:{_C_ACCENT};margin:4px 0;'>🥧 {_seg_label} — alle {len(_seg_all)} Jahre</h4>",
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
        st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">ℹ️ Keine Segmentdaten gefunden — das Unternehmen rapportiert möglicherweise keine separaten Segmente in seinen XBRL-Filings.</div>', unsafe_allow_html=True)
    elif FMP_API_KEY:
        st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">ℹ️ FMP Segmentdaten nicht verfügbar — FMP Paid Plan oder SEC_API_KEY benötigt.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">ℹ️ Segmentdaten: SEC_API_KEY in Railway-Umgebungsvariablen setzen (sec-api.io).</div>', unsafe_allow_html=True)

# ==================== TAB 2: PROGNOSE ====================
elif _at == 2:
    st.markdown("<div class='section-header'>🔮 Analysten-Prognosen</div>", unsafe_allow_html=True)

    # ── Rohdaten ─────────────────────────────────────────────────────────────
    _rec_key   = yf_info.get("recommendationKey", "")
    _rec_mean  = yf_info.get("recommendationMean")   # 1=Strong Buy … 5=Strong Sell
    _n_anal    = yf_info.get("numberOfAnalystOpinions") or 0
    _t_low     = yf_info.get("targetLowPrice")
    _t_mean    = yf_info.get("targetMeanPrice")
    _t_median  = yf_info.get("targetMedianPrice")
    _t_high    = yf_info.get("targetHighPrice")
    _fwd_pe    = yf_info.get("forwardPE")
    _fwd_eps   = yf_info.get("forwardEps")
    _trail_eps = yf_info.get("trailingEps")

    _eps_est = analyst_estimates.get("eps", [])
    _rev_est = analyst_estimates.get("rev", [])

    _rec_label_map = {
        "strong_buy":  ("Strong Buy",  "#26a69a"),
        "buy":         ("Kaufen",      "#66bb6a"),
        "hold":        ("Halten",      "#ffa726"),
        "sell":        ("Verkaufen",   "#ef5350"),
        "strong_sell": ("Strong Sell", "#b71c1c"),
    }
    _rec_label, _rec_color = _rec_label_map.get(
        _rec_key, ((_rec_key.replace("_", " ").title() if _rec_key else "—"), "#546e7a")
    )
    _upside      = ((_t_mean  / price - 1) * 100) if (_t_mean  and price > 0) else None
    _upside_low  = ((_t_low   / price - 1) * 100) if (_t_low   and price > 0) else None
    _upside_high = ((_t_high  / price - 1) * 100) if (_t_high  and price > 0) else None

    # Beat-Statistik
    _beats     = sum(1 for s in earnings_surprises if s["verdict"] == "Beat")
    _n_es      = len(earnings_surprises)
    _beat_rate = (_beats / _n_es * 100) if _n_es else None
    _surp_vals = [s["surp_pct"] for s in earnings_surprises if s.get("surp_pct") is not None]
    _avg_surp  = sum(_surp_vals) / len(_surp_vals) if _surp_vals else None

    # ── ABSCHNITT 1: Vier Kennzahl-Karten ────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _score_pct = ((5 - float(_rec_mean)) / 4 * 100) if _rec_mean else 0
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid {_rec_color};">
            <div class="metric-label">Analysten-Konsens</div>
            <div class="metric-value" style="color:{_rec_color};font-size:1.25rem;">{_rec_label}</div>
            <div style="background:#1e2d45;border-radius:4px;height:6px;margin:8px 0 4px 0;">
                <div style="background:{_rec_color};width:{_score_pct:.0f}%;height:6px;border-radius:4px;"></div></div>
            <div style="color:{_C_TEXT_MUTED};font-size:0.75rem;">{_n_anal} Analysten · Score {f"{float(_rec_mean):.1f}" if _rec_mean else "—"} / 5</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        _up_color = "#26a69a" if (_upside and _upside > 10) else "#ffa726" if (_upside and _upside > 0) else "#ef5350"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ø Kursziel (Upside)</div>
            <div class="metric-value" style="color:{_up_color};">{f"{_cur_sym}{_t_mean:.2f}" if _t_mean else "—"}</div>
            <div style="color:{_up_color};font-size:0.9rem;font-weight:600;margin-top:4px;">{f"{_upside:+.1f}%" if _upside is not None else ""}</div>
            <div style="color:{_C_TEXT_MUTED};font-size:0.75rem;">{f"Spanne: {_cur_sym}{_t_low:.0f}–{_cur_sym}{_t_high:.0f}" if (_t_low and _t_high) else ""}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        _fpe_color = "#26a69a" if (_fwd_pe and _fwd_pe < 20) else "#ffa726" if (_fwd_pe and _fwd_pe < 35) else "#ef5350"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Forward KGV</div>
            <div class="metric-value" style="color:{_fpe_color};">{f"{_fwd_pe:.1f}×" if _fwd_pe else "—"}</div>
            <div style="color:{_C_TEXT_MUTED};font-size:0.75rem;margin-top:4px;">Trailing KGV: {f"{trailing_pe:.1f}×" if trailing_pe else "—"}</div>
            <div style="color:{_C_TEXT_MUTED};font-size:0.75rem;">Forward EPS: {f"{_cur_sym}{_fwd_eps:.2f}" if _fwd_eps else "—"}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        _br_color = "#26a69a" if (_beat_rate and _beat_rate >= 70) else "#ffa726" if (_beat_rate and _beat_rate >= 50) else "#ef5350"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">EPS-Beat-Rate</div>
            <div class="metric-value" style="color:{_br_color};">{f"{_beat_rate:.0f}%" if _beat_rate else "—"}</div>
            <div style="color:{_C_TEXT_MUTED};font-size:0.75rem;margin-top:4px;">{f"{_beats}/{_n_es} Quartale" if _n_es else "Keine Daten"}</div>
            <div style="color:{_C_TEXT_MUTED};font-size:0.75rem;">{f"Ø Überraschung: {_avg_surp:+.1f}%" if _avg_surp is not None else ""}</div>
        </div>""", unsafe_allow_html=True)

    # ── ABSCHNITT 2: Kursziel-Spanne ─────────────────────────────────────────
    if _t_low and _t_high and price:
        _trange = _t_high - _t_low
        def _tp(val):
            if not val or not _trange: return 50
            return max(2, min(98, (val - _t_low) / _trange * 100))
        _pp  = _tp(price)
        _mp  = _tp(_t_mean)   if _t_mean   else None
        _medp = _tp(_t_median) if _t_median else None

        st.markdown(f"""
        <div style="background:{_C_SURFACE};border:1px solid #1e2d45;border-radius:14px;padding:22px 28px;margin:20px 0 6px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <span style="color:{_C_TEXT_SEC};font-weight:700;font-size:0.85rem;letter-spacing:0.05em;">KURSZIEL-SPANNE DER ANALYSTEN</span>
                <span style="color:{_C_TEXT_MUTED};font-size:0.78rem;">{_n_anal} Analysten · {_currency}</span>
            </div>
            <div style="position:relative;height:14px;border-radius:7px;
                background:linear-gradient(90deg,#ef5350 0%,#ffa726 35%,#26a69a 100%);margin-bottom:36px;">
                <div style="position:absolute;left:{_pp:.1f}%;top:-8px;transform:translateX(-50%);
                    width:10px;height:30px;background:#ffffff;border-radius:3px;
                    box-shadow:0 0 10px rgba(255,255,255,0.6);" title="Aktueller Kurs"></div>
                {f'<div style="position:absolute;left:{_mp:.1f}%;top:-5px;transform:translateX(-50%);width:3px;height:24px;background:#26a69a;border-radius:2px;opacity:0.9;" title="Ø Kursziel"></div>' if _mp else ""}
            </div>
            <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
                <div style="text-align:center;">
                    <div style="color:#ef5350;font-weight:700;font-size:0.95rem;">{_cur_sym}{_t_low:.2f}</div>
                    <div style="color:{_C_TEXT_MUTED};font-size:0.7rem;">Bear-Ziel</div>
                    <div style="color:#ef5350;font-size:0.78rem;">{f"{_upside_low:+.0f}%" if _upside_low else ""}</div>
                </div>
                <div style="text-align:center;background:rgba(255,255,255,0.05);border-radius:8px;padding:4px 14px;">
                    <div style="color:{_C_TEXT_PRIMARY};font-weight:700;font-size:1.0rem;">{_cur_sym}{price:.2f}</div>
                    <div style="color:{_C_TEXT_MUTED2};font-size:0.7rem;">Kurs heute</div>
                </div>
                {f'<div style="text-align:center;"><div style="color:#90caf9;font-weight:700;font-size:0.95rem;">{_cur_sym}{_t_median:.2f}</div><div style="color:{_C_TEXT_MUTED};font-size:0.7rem;">Median-Ziel</div></div>' if _t_median else ""}
                <div style="text-align:center;">
                    <div style="color:#26a69a;font-weight:700;font-size:0.95rem;">{_cur_sym}{_t_mean:.2f}</div>
                    <div style="color:{_C_TEXT_MUTED};font-size:0.7rem;">Ø Kursziel</div>
                    <div style="color:#26a69a;font-size:0.78rem;">{f"{_upside:+.0f}%" if _upside else ""}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#26a69a;font-weight:700;font-size:0.95rem;">{_cur_sym}{_t_high:.2f}</div>
                    <div style="color:{_C_TEXT_MUTED};font-size:0.7rem;">Bull-Ziel</div>
                    <div style="color:#26a69a;font-size:0.78rem;">{f"{_upside_high:+.0f}%" if _upside_high else ""}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── ABSCHNITT 3: Multi-Jahres-Prognose-Tabelle ────────────────────────────
    _est_by_year: dict = {}
    for _e in _eps_est:
        _yr = _e["year"]
        _est_by_year.setdefault(_yr, {})["eps"] = _e["estimate"]
        _est_by_year[_yr]["eps_an"] = _e.get("analysts")
    for _e in _rev_est:
        _yr = _e["year"]
        _est_by_year.setdefault(_yr, {})["rev"] = _e["estimate"]
        _est_by_year[_yr]["rev_an"] = _e.get("analysts")

    _years_sorted = sorted(_est_by_year.keys())

    if _years_sorted:
        st.markdown(
            "<div style='color:{_C_TEXT_SEC};font-weight:700;font-size:0.88rem;"
            "letter-spacing:0.05em;margin:26px 0 10px 0;'>JAHRES-PROGNOSEN IM ÜBERBLICK</div>",
            unsafe_allow_html=True)

        _prev_eps = _trail_eps
        _prev_rev = yf_info.get("totalRevenue")
        _tbl_rows = ""

        def _gc(v):   # growth color
            if v is None: return "#546e7a"
            return "#26a69a" if v > 10 else "#66bb6a" if v > 0 else "#ef5350"
        def _pec(v):  # P/E color
            if v is None: return "#78909c"
            return "#26a69a" if v < 15 else "#ffa726" if v < 30 else "#ef5350"

        for _yr in _years_sorted:
            _d = _est_by_year[_yr]
            _eps_e = _d.get("eps")
            _rev_e = _d.get("rev")
            _eps_an = _d.get("eps_an") or _d.get("rev_an")
            _eps_gr = ((_eps_e / _prev_eps - 1) * 100) if (_eps_e and _prev_eps and _prev_eps > 0) else None
            _rev_gr = ((_rev_e / _prev_rev - 1) * 100) if (_rev_e and _prev_rev and _prev_rev > 0) else None
            _fpe_i  = (price / _eps_e) if (_eps_e and _eps_e > 0 and price) else None
            _fps_i  = (market_cap / _rev_e) if (_rev_e and _rev_e > 0 and market_cap) else None
            _an_txt = f'<span style="color:#37474f;font-size:0.7rem">({_eps_an} An.)</span>' if _eps_an else ""
            _tbl_rows += f"""
            <tr style="border-bottom:1px solid #1a2744;">
                <td style="padding:11px 14px;font-weight:700;color:{_C_TEXT_PRIMARY};white-space:nowrap;">{_yr}E&nbsp;{_an_txt}</td>
                <td style="padding:11px 14px;text-align:right;color:{_C_TEXT_SEC};">{fmt_large(_rev_e) if _rev_e else "—"}</td>
                <td style="padding:11px 14px;text-align:right;font-weight:600;color:{_gc(_rev_gr)};">{f"{_rev_gr:+.1f}%" if _rev_gr is not None else "—"}</td>
                <td style="padding:11px 14px;text-align:right;color:{_C_TEXT_SEC};">{f"{_cur_sym}{_eps_e:.2f}" if _eps_e is not None else "—"}</td>
                <td style="padding:11px 14px;text-align:right;font-weight:600;color:{_gc(_eps_gr)};">{f"{_eps_gr:+.1f}%" if _eps_gr is not None else "—"}</td>
                <td style="padding:11px 14px;text-align:right;color:{_pec(_fpe_i)};">{f"{_fpe_i:.1f}×" if _fpe_i else "—"}</td>
                <td style="padding:11px 14px;text-align:right;color:#78909c;">{f"{_fps_i:.1f}×" if _fps_i else "—"}</td>
            </tr>"""
            _prev_eps = _eps_e or _prev_eps
            _prev_rev = _rev_e or _prev_rev

        st.markdown(f"""
        <div style="overflow-x:auto;margin-bottom:6px;">
        <table style="width:100%;border-collapse:collapse;font-size:0.84rem;
            background:{_C_SURFACE};border-radius:12px;overflow:hidden;">
        <thead><tr style="background:#1a2744;">
            <th style="padding:10px 14px;text-align:left;color:{_C_TEXT_MUTED};">Jahr</th>
            <th style="padding:10px 14px;text-align:right;color:{_C_TEXT_MUTED};">Umsatz (E)</th>
            <th style="padding:10px 14px;text-align:right;color:{_C_TEXT_MUTED};">Umsatz-Wachstum</th>
            <th style="padding:10px 14px;text-align:right;color:{_C_TEXT_MUTED};">EPS (E)</th>
            <th style="padding:10px 14px;text-align:right;color:{_C_TEXT_MUTED};">EPS-Wachstum</th>
            <th style="padding:10px 14px;text-align:right;color:{_C_TEXT_MUTED};">Fwd. KGV</th>
            <th style="padding:10px 14px;text-align:right;color:{_C_TEXT_MUTED};">Fwd. KUV</th>
        </tr></thead>
        <tbody style="color:{_C_TEXT_PRIMARY};">{_tbl_rows}</tbody>
        </table>
        </div>
        <div style="color:#37474f;font-size:0.71rem;">
        E = Analystenschätzung. KGV/KUV basiert auf Kurs {_cur_sym}{price:.2f} / MarketCap {fmt_large(market_cap, _cur_sym)}.
        </div>""", unsafe_allow_html=True)
    elif not _eps_est and not _rev_est:
        st.markdown(
            '<div class="insight-box" style="color:{_C_TEXT_MUTED};margin-top:16px;">'
            'ℹ️ Keine Forward-Schätzungen verfügbar — FMP_API_KEY setzen oder Ticker hat keine Analystencoverage.</div>',
            unsafe_allow_html=True)

    # ── ABSCHNITT 4: Investmentthese (auto-generiert) ─────────────────────────
    _thesis = []

    if _rec_label and _rec_label != "—":
        _thesis.append(
            f"<strong>{_n_anal} Analysten</strong> empfehlen aktuell "
            f"<strong style='color:{_rec_color}'>{_rec_label}</strong>.")

    if _upside is not None:
        _thesis.append(
            f"Das durchschnittliche Kursziel von <strong>{_cur_sym}{_t_mean:.2f}</strong> "
            f"impliziert <strong style='color:{'#26a69a' if _upside > 0 else '#ef5350'}'>"
            f"{_upside:+.1f}% Upside-Potenzial</strong> zum aktuellen Kurs.")

    if len(_eps_est) >= 2 and _trail_eps and _trail_eps > 0:
        _eps_last = _eps_est[-1].get("estimate")
        _n_fwd = len(_eps_est)
        if _eps_last and _eps_last > 0:
            _eps_cagr = ((_eps_last / _trail_eps) ** (1 / _n_fwd) - 1) * 100
            _eg_color = "#26a69a" if _eps_cagr > 10 else "#ffa726" if _eps_cagr > 0 else "#ef5350"
            _thesis.append(
                f"Über {_n_fwd} Jahr{'e' if _n_fwd > 1 else ''} wird ein EPS-Wachstum von "
                f"<strong style='color:{_eg_color}'>{_eps_cagr:.1f}% p.a.</strong> erwartet "
                f"(von {_cur_sym}{_trail_eps:.2f} auf {_cur_sym}{_eps_last:.2f}).")

    if len(_rev_est) >= 2 and yf_info.get("totalRevenue"):
        _rev_base = yf_info["totalRevenue"]
        _rev_last_e = _rev_est[-1].get("estimate")
        if _rev_last_e and _rev_base > 0:
            _rev_cagr = ((_rev_last_e / _rev_base) ** (1 / len(_rev_est)) - 1) * 100
            _rg_color = "#26a69a" if _rev_cagr > 8 else "#ffa726" if _rev_cagr > 0 else "#ef5350"
            _thesis.append(
                f"Der Umsatz soll mit <strong style='color:{_rg_color}'>{_rev_cagr:.1f}% p.a.</strong> wachsen.")

    if _fwd_pe:
        _pe_v = ("günstig (<20×)" if _fwd_pe < 20 else "fair (20–30×)" if _fwd_pe < 30
                 else "ambitioniert (30–50×)" if _fwd_pe < 50 else "sehr hoch (>50×)")
        _pe_c = "#26a69a" if _fwd_pe < 20 else "#66bb6a" if _fwd_pe < 30 else "#ffa726" if _fwd_pe < 50 else "#ef5350"
        _thesis.append(
            f"Das Forward-KGV von <strong style='color:{_pe_c}'>{_fwd_pe:.1f}×</strong> "
            f"gilt als <strong style='color:{_pe_c}'>{_pe_v}</strong>.")

    if _beat_rate is not None and _n_es >= 4:
        _br_v = ("übertrifft die Erwartungen konsistent" if _beat_rate >= 75
                 else "trifft die Erwartungen meist" if _beat_rate >= 50
                 else "verfehlt die Erwartungen häufig")
        _thesis.append(
            f"Das Management <strong>{_br_v}</strong> "
            f"({_beat_rate:.0f}% Beat-Rate, Ø {_avg_surp:+.1f}% Überraschung).")

    if _thesis:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0b1e10 0%,#0d1526 100%);
            border:1px solid #1b3d20;border-radius:14px;padding:20px 26px;margin:22px 0;">
            <div style="color:#81c784;font-weight:700;font-size:0.8rem;
                letter-spacing:0.08em;margin-bottom:12px;">📋 INVESTMENTTHESE — ANALYSTENKONSENS</div>
            <div style="color:#cfd8dc;font-size:0.88rem;line-height:1.8;">
                {"&nbsp; ".join(_thesis)}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── ABSCHNITT 5: EPS-Überraschungen (Beat/Miss-History) ─────────────────
    if earnings_surprises:
        _bi = "✅" if (_beat_rate and _beat_rate >= 70) else "⚠️" if (_beat_rate and _beat_rate >= 50) else "❌"
        st.markdown(
            f"<div style='color:{_C_TEXT_SEC};font-weight:700;font-size:0.85rem;"
            f"letter-spacing:0.05em;margin:24px 0 10px 0;'>"
            f"EPS-ÜBERRASCHUNGEN — LETZTE {_n_es} QUARTALE&nbsp;&nbsp;"
            f"{f'{_bi} {_beats}/{_n_es} Beat ({_beat_rate:.0f}%)' if _beat_rate else ''}</div>",
            unsafe_allow_html=True)
        _surp_rows = ""
        for _s in earnings_surprises[:8]:
            _vc   = "#26a69a" if _s["verdict"] == "Beat" else "#ef5350" if _s["verdict"] == "Miss" else "#ffa726"
            _sval = _s.get("surp_pct") or 0
            _bw   = min(abs(_sval) * 2.5, 100)
            _surp_rows += f"""
            <tr style="border-bottom:1px solid #0d1526;">
                <td style="padding:9px 12px;color:{_C_TEXT_MUTED2};">{_s['date']}</td>
                <td style="padding:9px 12px;text-align:right;color:{_C_TEXT_MUTED};">
                    {f"{_cur_sym}{_s['estimate']:.2f}" if _s.get("estimate") is not None else "—"}</td>
                <td style="padding:9px 12px;text-align:right;color:{_C_TEXT_PRIMARY};font-weight:600;">
                    {_cur_sym}{_s['actual']:.2f}</td>
                <td style="padding:9px 12px;">
                    <div style="display:flex;align-items:center;gap:6px;">
                        <div style="background:#1e2d45;border-radius:3px;height:7px;width:70px;flex-shrink:0;">
                            <div style="background:{_vc};width:{_bw:.0f}%;height:7px;border-radius:3px;"></div></div>
                        <span style="color:{_vc};font-weight:600;font-size:0.8rem;">
                            {f"{_sval:+.1f}%" if _sval else "—"}</span>
                    </div>
                </td>
                <td style="padding:9px 12px;text-align:center;">
                    <span style="color:{_vc};font-weight:700;font-size:0.78rem;">{_s['verdict']}</span>
                </td>
            </tr>"""
        st.markdown(f"""
        <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-size:0.82rem;
            background:{_C_SURFACE};border-radius:12px;overflow:hidden;">
        <thead><tr style="background:#1a2744;">
            <th style="padding:9px 12px;text-align:left;color:{_C_TEXT_MUTED};">Quartal</th>
            <th style="padding:9px 12px;text-align:right;color:{_C_TEXT_MUTED};">Schätzung</th>
            <th style="padding:9px 12px;text-align:right;color:{_C_TEXT_MUTED};">Actual EPS</th>
            <th style="padding:9px 12px;color:{_C_TEXT_MUTED};">Überraschung</th>
            <th style="padding:9px 12px;text-align:center;color:{_C_TEXT_MUTED};">Ergebnis</th>
        </tr></thead>
        <tbody style="color:{_C_TEXT_PRIMARY};">{_surp_rows}</tbody>
        </table></div>""", unsafe_allow_html=True)

elif _at == 3:
    st.markdown("<div class='section-header'>Fundamental</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Cap</div>
            <div class="metric-value">{fmt_large(market_cap, _cur_sym)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Enterprise Value</div>
            <div class="metric-value">{fmt_large(enterprise_value, _cur_sym)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Free Cash Flow</div>
            <div class="metric-value">{fmt_large(fcf, _cur_sym)}</div>
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
        dil_color = _C_NEGATIVE if dilution_pct and dilution_pct > 5 else _C_NEUTRAL if dilution_pct and dilution_pct > 2 else _C_POSITIVE
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
        ncp_color = _C_POSITIVE if net_cash_per_share and net_cash_per_share > 0 else _C_NEGATIVE
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
        short_color = _C_NEGATIVE if short_pct_float and short_pct_float > 0.15 else _C_NEUTRAL if short_pct_float and short_pct_float > 0.07 else _C_POSITIVE
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
            _sh_colors = [_C_NEGATIVE if d > 0.5 else _C_POSITIVE if d < -0.5 else _C_NEUTRAL for d in _sh_delta]
            fig_sh = go.Figure(go.Bar(
                x=_sh_years, y=_sh_vals,
                marker_color=_sh_colors,
                text=[f"{v:.2f}B" for v in _sh_vals],
                textposition="outside",
                textfont=dict(size=10, color="#90a4ae"),
            ))
            fig_sh.update_layout(
                title=dict(text="Aktienanzahl (Diluted) — Jahresverlauf", font=dict(size=12, color="#90a4ae"), x=0),
                template=_C_CHART_THEME,
                paper_bgcolor=_C_CHART_PAPER,
                plot_bgcolor=_C_CHART_PLOT,
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
            _clr = _C_POSITIVE if _v == "Beat" else _C_NEGATIVE if _v == "Miss" else _C_NEUTRAL
            _bg  = "rgba(0,230,118,0.08)" if _v == "Beat" else "rgba(255,82,82,0.08)" if _v == "Miss" else "rgba(255,214,0,0.08)"
            _icon = "✅" if _v == "Beat" else "❌" if _v == "Miss" else "➖"
            _surp_str = f"{_es['surp_pct']:+.1f}%"
            _col.markdown(f"""
            <div style='background:{_bg};border:1px solid {_clr}33;border-top:3px solid {_clr};
                 border-radius:12px;padding:12px 14px;text-align:center;'>
              <div style='color:{_C_TEXT_MUTED};font-size:0.72rem;margin-bottom:4px;'>{_es["date"]}</div>
              <div style='color:{_clr};font-size:1.1rem;font-weight:800;'>{_icon} {_v}</div>
              <div style='color:{_C_TEXT_PRIMARY};font-size:0.88rem;font-weight:700;margin:4px 0;'>{_surp_str}</div>
              <div style='color:{_C_TEXT_MUTED};font-size:0.7rem;'>
                {'Est: $' + f"{_es['estimate']:.2f} · " if _es['estimate'] is not None else ''}Act: ${_es["actual"]:.2f}
              </div>
            </div>""", unsafe_allow_html=True)

        # Surprise % bar chart (all 8 quarters)
        if len(earnings_surprises) > 1:
            _dates  = [e["date"]     for e in reversed(earnings_surprises)]
            _surps  = [e["surp_pct"] for e in reversed(earnings_surprises)]
            _colors = [_C_POSITIVE if s > 2 else _C_NEGATIVE if s < -2 else _C_NEUTRAL for s in _surps]
            _fig_es = go.Figure(go.Bar(
                x=_dates, y=_surps,
                marker_color=_colors,
                text=[f"{s:+.1f}%" for s in _surps],
                textposition="outside",
                textfont=dict(size=10, color="#90a4ae"),
            ))
            _fig_es.add_hline(y=0, line_color="#1e3a5f", line_width=1)
            _fig_es.update_layout(
                template=_C_CHART_THEME,
                paper_bgcolor=_C_CHART_PAPER,
                plot_bgcolor=_C_CHART_PLOT,
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
            _rev_cl = [_C_POSITIVE if i == 0 or v >= _rev_b[i-1] else _C_NEGATIVE
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
            _net_cl  = [_C_POSITIVE if v >= 0 else _C_NEGATIVE for v in _net_b]
            _qfig.add_trace(go.Bar(
                x=_labels2, y=_net_b,
                marker_color=_net_cl, name="Nettogewinn",
                text=[f"${v:.2f}B" for v in _net_b],
                textposition="outside", textfont=dict(size=9, color="#90a4ae"),
            ), row=1, col=2)
        _qfig.update_layout(
            template=_C_CHART_THEME,
            paper_bgcolor=_C_CHART_PAPER,
            plot_bgcolor=_C_CHART_PLOT,
            height=300,
            showlegend=False,
            margin=dict(l=0, r=0, t=36, b=0),
            font=dict(color="#90a4ae", size=10),
        )
        _qfig.update_yaxes(showgrid=True, gridcolor="#1e2d45", zeroline=True,
                           zerolinecolor="#1e3a5f", ticksuffix="B")
        st.plotly_chart(_qfig, use_container_width=True)
    else:
        st.markdown(f'<div class="metric-card" style="color:{_C_TEXT_MUTED};text-align:center;">'
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
            template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
            plot_bgcolor=_C_CHART_PLOT, height=260,
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
                '<div style="font-size:0.68rem;color:{_C_TEXT_MUTED};margin-top:-8px;">'
                '⬆ Hohe CapEx = starke Investitionen (Hyperscaler, Industrie) · '
                'Als % des Umsatzes oder FCF einordnen</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">Keine CapEx-Daten verfügbar</div>',
                        unsafe_allow_html=True)

    with _cx2:
        _fig_gw = _simple_bar(a_goodwill, "Goodwill", "#7986cb", fmt_fn=fmt_large)
        if _fig_gw:
            st.plotly_chart(_fig_gw, use_container_width=True)
            st.markdown(
                '<div style="font-size:0.68rem;color:{_C_TEXT_MUTED};margin-top:-8px;">'
                '⚠ Stark steigender Goodwill = viele Akquisitionen · '
                'Abschreibungsrisiko (Impairment) beachten</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">Keine Goodwill-Daten verfügbar</div>',
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
                    marker_color=["#ff8f00" if v > 15 else _C_NEUTRAL if v > 8 else "#64b5f6"
                                  for v in _capex_pct.values],
                    text=[f"{v:.1f}%" for v in _capex_pct.values],
                    textposition="outside", textfont=dict(size=10, color="#90a4ae"),
                ))
                _fig_cp.update_layout(
                    template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
                    plot_bgcolor=_C_CHART_PLOT, height=220,
                    margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
                    yaxis=dict(showgrid=True, gridcolor="#1e2d45", ticksuffix="%"),
                    xaxis=dict(showgrid=False),
                    title=dict(text="CapEx als % des Umsatzes",
                               font=dict(color="#64b5f6", size=13)),
                )
                st.plotly_chart(_fig_cp, use_container_width=True)
                st.markdown(
                    '<div style="font-size:0.68rem;color:{_C_TEXT_MUTED};margin-top:-8px;">'
                    'Benchmark: Hyperscaler (AWS/Azure/GCP) >10% · Industrie 5–10% · '
                    'Software/Asset-light &lt;3%</div>',
                    unsafe_allow_html=True)

    # ── Verschuldung & Cash-Position ──────────────────────────────────────
    st.markdown("<div class='section-header'>🏦 Verschuldung & Cash-Position</div>", unsafe_allow_html=True)

    _has_debt = not a_debt.empty and len(a_debt) >= 2
    _has_cash = not a_cash.empty and len(a_cash) >= 2

    if _has_debt or _has_cash:
        _dc1, _dc2 = st.columns(2)

        # ── Linke Spalte: Schulden vs. Cash (gruppierter Balken) ──
        with _dc1:
            if _has_debt or _has_cash:
                _idx = sorted(set(
                    (a_debt.index.tolist() if _has_debt else []) +
                    (a_cash.index.tolist() if _has_cash else [])
                ))
                _idx = _idx[-6:]
                _labels_dc = [str(d.year) if hasattr(d, "year") else str(d)[:4] for d in _idx]
                _fig_dc = go.Figure()
                if _has_debt:
                    _dv = [a_debt.get(d, None) for d in _idx]
                    _fig_dc.add_trace(go.Bar(
                        name="Gesamtschulden", x=_labels_dc, y=_dv,
                        marker_color="#ef5350",
                        text=[fmt_large(v) if v else "" for v in _dv],
                        textposition="outside", textfont=dict(size=9, color="#90a4ae"),
                    ))
                if _has_cash:
                    _cv = [a_cash.get(d, None) for d in _idx]
                    _fig_dc.add_trace(go.Bar(
                        name="Cash & Äquivalente", x=_labels_dc, y=_cv,
                        marker_color=_C_POSITIVE,
                        text=[fmt_large(v) if v else "" for v in _cv],
                        textposition="outside", textfont=dict(size=9, color="#90a4ae"),
                    ))
                _fig_dc.update_layout(
                    template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
                    plot_bgcolor=_C_CHART_PLOT, height=280,
                    margin=dict(l=0, r=0, t=30, b=0),
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                xanchor="left", x=0, font=dict(size=10)),
                    yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
                    xaxis=dict(showgrid=False),
                    title=dict(text="Schulden vs. Cash (absolut)",
                               font=dict(color="#64b5f6", size=13)),
                )
                st.plotly_chart(_fig_dc, use_container_width=True)
                st.markdown(
                    '<div style="font-size:0.68rem;color:{_C_TEXT_MUTED};margin-top:-8px;">'
                    '🔴 Hohe Schulden bei niedrigem Cash = Refinanzierungsrisiko · '
                    '🟢 Cash > Schulden = Nettocash-Position</div>',
                    unsafe_allow_html=True)

        # ── Rechte Spalte: Nettoverschuldung + Debt/EBITDA ──
        with _dc2:
            if _has_debt and _has_cash:
                _common = sorted(a_debt.index.intersection(a_cash.index))[-6:]
                if len(_common) >= 2:
                    _net_debt = (a_debt[_common] - a_cash[_common])
                    _labels_nd = [str(d.year) if hasattr(d, "year") else str(d)[:4]
                                  for d in _common]
                    _colors_nd = [_C_POSITIVE if v < 0 else "#ef5350" for v in _net_debt.values]
                    _fig_nd = go.Figure(go.Bar(
                        x=_labels_nd, y=_net_debt.values,
                        marker_color=_colors_nd,
                        text=[fmt_large(v) for v in _net_debt.values],
                        textposition="outside", textfont=dict(size=9, color="#90a4ae"),
                    ))
                    _fig_nd.add_hline(y=0, line_color="#546e7a", line_width=1)
                    _fig_nd.update_layout(
                        template=_C_CHART_THEME, paper_bgcolor=_C_CHART_PAPER,
                        plot_bgcolor=_C_CHART_PLOT, height=280,
                        margin=dict(l=0, r=0, t=30, b=0), showlegend=False,
                        yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False),
                        xaxis=dict(showgrid=False),
                        title=dict(text="Nettoverschuldung (Schulden − Cash)",
                                   font=dict(color="#64b5f6", size=13)),
                    )
                    st.plotly_chart(_fig_nd, use_container_width=True)
                    _last_nd = _net_debt.iloc[-1]
                    _nd_hint = ("🟢 Nettocash-Position" if _last_nd < 0
                                else "🔴 Nettoverschuldet" if _last_nd > 0 else "")
                    st.markdown(
                        f'<div style="font-size:0.68rem;color:{_C_TEXT_MUTED};margin-top:-8px;">'
                        f'Negativ = mehr Cash als Schulden (gut) · {_nd_hint}</div>',
                        unsafe_allow_html=True)
            elif _has_debt:
                _fig_donly = _simple_bar(a_debt, "Gesamtschulden", "#ef5350", fmt_fn=fmt_large)
                if _fig_donly:
                    st.plotly_chart(_fig_donly, use_container_width=True)

        # ── Debt/EBITDA Tabelle ──
        _common_de = sorted(a_debt.index.intersection(a_ebitda.index))[-6:] if (_has_debt and not a_ebitda.empty) else []
        if len(_common_de) >= 2:
            _de_ratios = (a_debt[_common_de] / a_ebitda[_common_de].abs()).replace([float('inf'), float('-inf')], None).dropna()
            if not _de_ratios.empty:
                st.markdown("**Debt / EBITDA** (Faustregel: &lt;2× konservativ · 2–4× moderat · &gt;4× riskant)")
                _de_cols = st.columns(len(_de_ratios))
                for _di, ((_dk, _dv), _dcol) in enumerate(zip(_de_ratios.items(), _de_cols)):
                    _yr = str(_dk.year) if hasattr(_dk, "year") else str(_dk)[:4]
                    _col_de = _C_POSITIVE if _dv < 2 else _C_NEUTRAL if _dv < 4 else "#ef5350"
                    _dcol.markdown(
                        f"<div style='text-align:center;padding:6px 4px;background:{_C_CARD_BG};"
                        f"border-radius:6px;border:1px solid #1a2740;'>"
                        f"<div style='color:#78909c;font-size:0.65rem;'>{_yr}</div>"
                        f"<div style='color:{_col_de};font-size:1rem;font-weight:700;'>{_dv:.1f}×</div>"
                        f"</div>", unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="insight-box" style="color:{_C_TEXT_MUTED};">Keine Bilanzdaten für Verschuldung verfügbar</div>',
                    unsafe_allow_html=True)

elif _at == 4:
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
        pfcf_color = _C_POSITIVE if price_to_fcf and price_to_fcf < 20 else _C_NEUTRAL if price_to_fcf and price_to_fcf < 35 else _C_NEGATIVE
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
        tsy_color = _C_POSITIVE if total_shareholder_yield and total_shareholder_yield > 5 else _C_NEUTRAL if total_shareholder_yield and total_shareholder_yield > 2 else "#78909c"
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
        up_color = _C_POSITIVE if upside_val > 0 else _C_NEGATIVE
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
        st.markdown(f"""
        <div class="insight-box" style="margin-bottom:16px; line-height:1.7;">
            <strong>Was ist der DCF Fair Value?</strong>
            Der Discounted-Cashflow-Wert ist der heutige Barwert aller zukünftig erwarteten Free Cashflows —
            diskontiert mit einem Zinssatz, der Risiko und Opportunitätskosten widerspiegelt.
            Er beantwortet: <em>„Was wäre die Aktie wert, wenn ich alle künftigen Cashflows heute ausbezahlt bekäme?"</em><br><br>
            <strong>Wie einordnen?</strong>
            <ul style="margin:4px 0 0 16px; padding:0;">
                <li>Der Wert ist <strong>kein Kursziel</strong>, sondern ein Anker für die Bewertungsdiskussion.</li>
                <li>Liegt der Kurs <em>unter</em> dem Bear-Szenario → mögliche <strong>Margin of Safety</strong> (Benjamin Graham).</li>
                <li>Liegt der Kurs <em>über</em> dem Bull-Szenario → Markt preist starkes Wachstum ein — Enttäuschungspotenzial hoch.</li>
                <li>Die Berechnung steht und fällt mit den Annahmen (GIGO). Kleines Delta bei der Wachstumsrate = grosser Effekt auf den Endwert.</li>
            </ul>
            <span style="color:{_C_TEXT_MUTED}; font-size:0.78rem;">
                Akt. FCF: <strong>{fmt_large(fcf, _cur_sym) if fcf else "N/A"}</strong> ·
                Rev. Growth: <strong>{f"{rev_growth:.1f}%" if rev_growth is not None else "N/A"}</strong> ·
                Alle Werte in {_currency} · Keine Anlageberatung.
            </span>
        </div>
        """, unsafe_allow_html=True)
        _rg = rev_growth or 5
        _scenarios = {
            "🐻 Bear": {
                "growth": max(2.0,  round(_rg * 0.35, 1)),
                "terminal": 1.5, "discount": 11.0,
                "accent": _C_NEGATIVE, "bg": "rgba(255,82,82,0.07)",
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
                "accent": _C_POSITIVE, "bg": "rgba(0,230,118,0.07)",
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
                _mg_clr   = _sc["accent"] if _mg > 0 else _C_NEGATIVE
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
              <div style='color:{_C_TEXT_PRIMARY};font-size:1.9rem;font-weight:800;'>
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
            _bar_clrs   = [_scenarios[n]["accent"] for n in _sc_vals] + [_C_NEUTRAL]
            _fig_dcf = go.Figure(go.Bar(
                x=_bar_labels, y=_bar_vals,
                marker_color=_bar_clrs,
                text=[f"${v:,.0f}" for v in _bar_vals],
                textposition="outside",
                textfont=dict(size=11, color="#90a4ae"),
            ))
            _fig_dcf.add_hline(y=price, line_dash="dot", line_color=_C_NEUTRAL,
                               line_width=1.5,
                               annotation_text=f"Kurs {_cur_sym}{price:.0f}",
                               annotation_font_color=_C_NEUTRAL)
            _fig_dcf.update_layout(
                template=_C_CHART_THEME,
                paper_bgcolor=_C_CHART_PAPER,
                plot_bgcolor=_C_CHART_PLOT,
                height=260, showlegend=False,
                margin=dict(l=0, r=0, t=30, b=0),
                yaxis=dict(showgrid=True, gridcolor="#1e2d45", zeroline=False,
                           tickprefix="$"),
                xaxis=dict(showgrid=False),
            )
            st.plotly_chart(_fig_dcf, use_container_width=True)
            _fv_min = min(_fv_values)
            _fv_max = max(_fv_values)
            if price < _fv_min:
                _dcf_interp = f"✅ Kurs liegt <strong>unter allen 3 Szenarien</strong> — breite Margin of Safety, sofern die Cashflow-Annahmen realistisch sind."
                _dcf_interp_bg = "rgba(0,230,118,0.07)"
            elif price > _fv_max:
                _dcf_interp = f"⚠️ Kurs liegt <strong>über allen 3 Szenarien</strong> — Markt preist starkes Wachstum ein, das über dem Bull-Case liegt. Hohes Enttäuschungspotenzial."
                _dcf_interp_bg = "rgba(255,82,82,0.07)"
            else:
                _dcf_interp = f"ℹ️ Kurs liegt <strong>innerhalb der Szenario-Spanne</strong> — die Bewertung hängt davon ab, welches Szenario du für realistisch hältst."
                _dcf_interp_bg = "rgba(100,181,246,0.07)"
            st.markdown(
                f'<div style="background:{_dcf_interp_bg};border-radius:10px;padding:10px 16px;'
                f'font-size:0.83rem;color:{_C_TEXT_SEC};margin:-8px 0 12px 0;">{_dcf_interp}</div>',
                unsafe_allow_html=True)

        # ── Manueller Rechner (aufklappbar) ────────────────────────────
        with st.expander("⚙️ Eigenes Szenario berechnen", expanded=False):
            st.markdown(f"""
            <div class="insight-box" style="margin-bottom:12px;">
                <strong>ℹ️ DCF Hinweis:</strong> Der Wert reagiert stark auf Eingaben.
                Konservative Wachstumsrate (10–20%) und höherer Diskontsatz (10–12%)
                vermeiden Euphorie-Prämien. Akt. Rev. Growth: <strong>{f"{rev_growth:.1f}%" if rev_growth is not None else "N/A"}</strong>.
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
                m_color = _C_POSITIVE if margin > 0 else _C_NEGATIVE
                m_label = "Margin of Safety" if margin > 0 else "Überbewertung"
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0d2137,#0a1a2e);border:1px solid #1e3a5f;
                     border-radius:16px;padding:22px;margin-top:10px;text-align:center;">
                    <div style="color:#78909c;font-size:0.8rem;text-transform:uppercase;
                         letter-spacing:1px;margin-bottom:8px;">Eigenes Szenario</div>
                    <div style="color:{_C_TEXT_PRIMARY};font-size:2.5rem;font-weight:800;">${fair_val:.2f}</div>
                    <div style="color:{m_color};font-size:1rem;margin-top:6px;font-weight:600;">
                        {'▲' if margin > 0 else '▼'} {abs(margin):.1f}% {m_label}
                    </div>
                    <div style="color:{_C_TEXT_MUTED};font-size:0.78rem;margin-top:6px;">
                        Kurs: {_cur_sym}{price:.2f} | FCF: {fmt_large(fcf, _cur_sym)}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("Nicht genug Daten für DCF-Berechnung (FCF oder Shares fehlen).")

# ==================== TAB 5: CHART ANALYSE ====================
elif _at == 7:
    st.markdown("<div class='section-header'>📉 Technische Chart-Analyse</div>", unsafe_allow_html=True)

    # ── Controls row ──────────────────────────────────────────────────
    _c1, _c2, _c3 = st.columns([2, 2, 2])
    with _c1:
        chart_mode = st.radio("Zeitrahmen", ["Täglich (5J)", "Wöchentlich (2J)", "Monatlich (5J)"],
                              horizontal=True, key="chart_mode")
    with _c2:
        chart_type = st.radio("Chart-Typ", ["Candlestick", "Linie"], horizontal=True, key="ctype")
    with _c3:
        _lcol, _mcol, _rcol = st.columns(3)
        with _lcol:
            show_sp500 = st.checkbox("vs. S&P 500", value=False, key="show_sp500")
        with _mcol:
            show_nasdaq = st.checkbox("vs. NASDAQ", value=False, key="show_nasdaq")
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
        ema_colors  = {"EMA 20": _C_NEUTRAL, "EMA 50": "#00e5ff", "EMA 100": "#ff9100", "EMA 200": "#ef5350"}

        if chart_type == "Candlestick":
            fig_ta.add_trace(go.Candlestick(
                x=chart_data.index,
                open=chart_data["Open"], high=chart_data["High"],
                low=chart_data["Low"],  close=close,
                name=ticker,
                increasing_line_color=_C_POSITIVE, decreasing_line_color=_C_NEGATIVE,
                increasing_fillcolor=_C_POSITIVE,  decreasing_fillcolor=_C_NEGATIVE,
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

        # ── NASDAQ (QQQ) comparison ────────────────────────────────────
        if show_nasdaq:
            if chart_type == "Candlestick":
                st.caption("ℹ️ NASDAQ Vergleich nur im Linie-Modus verfügbar")
            else:
                try:
                    _nq_days = 2*365+10 if "Wöchentlich" in chart_mode else 5*365+10
                    _nq_start = (_dt.date.today() - _dt.timedelta(days=_nq_days)).strftime("%Y-%m-%d")
                    _nq_end   = _dt.date.today().strftime("%Y-%m-%d")
                    _nq_hist  = yf.Ticker("QQQ").history(
                        start=_nq_start, end=_nq_end,
                        interval="1wk" if "Wöchentlich" in chart_mode else
                                 "1mo" if "Monatlich"   in chart_mode else "1d"
                    )
                    if not _nq_hist.empty:
                        _nq_close = _nq_hist["Close"].copy()
                        _nq_close.index = pd.to_datetime(_nq_close.index).normalize().tz_localize(None)
                        _cd_index_norm2 = pd.to_datetime(chart_data.index).normalize().tz_localize(None)
                        _nq_reindexed   = _nq_close.reindex(_cd_index_norm2, method="ffill").dropna()
                        if not _nq_reindexed.empty and not close.empty:
                            _stock_start2 = float(close.iloc[0])
                            _nq_start_val = float(_nq_reindexed.iloc[0])
                            _nq_scaled    = _nq_reindexed * (_stock_start2 / _nq_start_val)
                            _valid_mask2  = _cd_index_norm2.isin(_nq_reindexed.index)
                            _x_dates2     = chart_data.index[_valid_mask2]
                            fig_ta.add_trace(go.Scatter(
                                x=_x_dates2, y=_nq_scaled.values,
                                name="NASDAQ (relativ)",
                                line=dict(color="#7c4dff", width=1.5, dash="dot"),
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
            fig_ta.add_hline(y=target_mean, line_dash="dot", line_color=_C_NEUTRAL, line_width=1.5,
                             annotation_text=f"Analyst Ziel ${target_mean:.0f}",
                             annotation_font_color=_C_NEUTRAL, row=1, col=1)

        # ── Volume ──────────────────────────────────────────────────────
        vol_colors = [_C_POSITIVE if c >= o else _C_NEGATIVE
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
            hist_colors = [_C_POSITIVE if v >= 0 else _C_NEGATIVE for v in macd_hist]
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
                name="Signal", line=dict(color=_C_NEUTRAL, width=1.2), showlegend=False,
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
            template=_C_CHART_THEME,
            paper_bgcolor=_C_CHART_PAPER,
            plot_bgcolor=_C_CHART_PLOT,
            height=_height,
            legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
                        bgcolor=_C_CHART_PLOT, bordercolor=_C_BORDER, borderwidth=1,
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
elif _at == 8:
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
                        <span style="color:{_C_TEXT_SEC};">{str(name)[:20]}</span>
                        <span class="{tx_class}">{tx}</span>
                        <span style="color:{_C_ACCENT};">{val_str}</span>
                        <span style="color:{_C_TEXT_MUTED};">{date}</span>
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
        _ins_clr = _C_POSITIVE if _ins_pct and _ins_pct > 0.05 else _C_NEUTRAL if _ins_pct else "#546e7a"
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
        _roic_clr = _C_POSITIVE if roic_val and roic_val > 15 else _C_NEUTRAL if roic_val and roic_val > 8 else _C_NEGATIVE if roic_val else "#546e7a"
        st.markdown(f"""<div class="metric-card" style="text-align:center;">
            <div class="metric-label">ROIC</div>
            <div class="metric-value" style="color:{_roic_clr};">{f"{roic_val:.1f}%" if roic_val else "N/A"}</div>
            <div class="metric-sub">Kapitalallokation</div>
        </div>""", unsafe_allow_html=True)
    with _om4:
        _dil_str = f"{dilution_pct:+.1f}%" if dilution_pct is not None else "N/A"
        _dil_clr = _C_POSITIVE if dilution_pct is not None and dilution_pct < 0 else \
                   _C_NEUTRAL if dilution_pct is not None and dilution_pct < 3 else \
                   _C_NEGATIVE if dilution_pct is not None else "#546e7a"
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
            col.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.72rem; font-weight:600; padding:4px 0;'>{hdr}</div>",
                         unsafe_allow_html=True)
        for _name, _title, _age_s, _pay_s in _mgmt_rows:
            c1, c2, c3, c4 = st.columns([3, 4, 1, 2])
            c1.markdown(f"<div style='color:{_C_TEXT_PRIMARY}; font-size:0.82rem; padding:3px 0;'>{_name}</div>", unsafe_allow_html=True)
            c2.markdown(f"<div style='color:{_C_TEXT_MUTED2}; font-size:0.78rem; padding:3px 0;'>{_title}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='color:{_C_TEXT_MUTED}; font-size:0.78rem; padding:3px 0;'>{_age_s}</div>", unsafe_allow_html=True)
            c4.markdown(f"<div style='color:{_C_ACCENT}; font-size:0.78rem; padding:3px 0;'>{_pay_s}</div>", unsafe_allow_html=True)

    st.markdown("""<div style='color:#37474f; font-size:0.72rem; margin-top:10px;'>
        ℹ️ Managementqualität lässt sich nicht allein aus Zahlen ableiten — Insider-Ownership >5% und
        sinkende Aktienanzahl sind starke positive Signale. Für eine vollständige Einschätzung: Shareholder Letters,
        Glassdoor-Bewertungen und Track Record bei Kapitalallokation prüfen.
    </div>""", unsafe_allow_html=True)

# ==================== TAB 9: NEWS ====================
elif _at == 9:
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
                                <span style="color:{_C_ACCENT}; font-size:0.75rem; font-weight:600;">{source}</span>
                                <span style="color:{_C_TEXT_MUTED}; font-size:0.72rem;">{pub_at}</span>
                            </div>
                            <a href="{url_a}" target="_blank" style="color:{_C_TEXT_PRIMARY}; font-size:0.9rem; font-weight:600; text-decoration:none; line-height:1.4;">
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
                            <span style="color:{_C_ACCENT}; font-size:0.75rem; font-weight:600;">{p['publisher']}</span>
                            <span style="color:{_C_TEXT_MUTED}; font-size:0.72rem;">{p['pub_str']}</span>
                        </div>
                        <a href="{p['link']}" target="_blank" style="color:{_C_TEXT_PRIMARY}; font-size:0.9rem; font-weight:600; text-decoration:none; line-height:1.4;">
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
elif _at == 6:
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
                <span style="color:{_C_TEXT_SEC}; font-size:0.9rem; line-height:1.6;">{moat['moat_desc']}</span>
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
        mc_str = fmt_large(market_cap, _cur_sym) if market_cap else "N/A"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Marktkapitalisierung</div>
            <div class="metric-value" style="font-size:1.1rem;">{mc_str}</div>
            <div class="metric-sub">Market Cap</div>
        </div>""", unsafe_allow_html=True)
    with oc4:
        rev_str = fmt_large(yf_info.get("totalRevenue"), _cur_sym) if yf_info.get("totalRevenue") else "N/A"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Umsatz (TTM)</div>
            <div class="metric-value" style="font-size:1.1rem;">{rev_str}</div>
            <div class="metric-sub">Total Revenue</div>
        </div>""", unsafe_allow_html=True)

    # ── Externe Links: Homepage + Geschäftsbericht ──────────────────────
    _link_parts = []
    if _website:
        _link_parts.append(
            f"<a href='{_website}' target='_blank' rel='noopener' "
            f"style='color:{_C_ACCENT};text-decoration:none;font-weight:600;font-size:0.85rem;"
            f"background:rgba(100,181,246,0.1);padding:5px 12px;border-radius:8px;"
            f"border:1px solid rgba(100,181,246,0.25);white-space:nowrap;'>"
            f"🌐 Homepage</a>"
        )
        _ir_url = _website.rstrip("/") + "/investor-relations"
        _link_parts.append(
            f"<a href='{_ir_url}' target='_blank' rel='noopener' "
            f"style='color:#69f0ae;text-decoration:none;font-weight:600;font-size:0.85rem;"
            f"background:rgba(105,240,174,0.1);padding:5px 12px;border-radius:8px;"
            f"border:1px solid rgba(105,240,174,0.25);white-space:nowrap;'>"
            f"📊 Investor Relations</a>"
        )
    _exchange = yf_info.get("exchange", "") or ""
    _is_us = _exchange.upper() in ("NYQ", "NMS", "NGM", "NCM", "ASE", "PCX", "NYS", "NASDAQ", "NYSE")
    if _is_us:
        _cik = _sec_cik(ticker)
        if _cik:
            _edgar_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={_cik}&type=10-K&dateb=&owner=include&count=5"
            _link_parts.append(
                f"<a href='{_edgar_url}' target='_blank' rel='noopener' "
                f"style='color:#ffd600;text-decoration:none;font-weight:600;font-size:0.85rem;"
                f"background:rgba(255,214,0,0.1);padding:5px 12px;border-radius:8px;"
                f"border:1px solid rgba(255,214,0,0.25);white-space:nowrap;'>"
                f"📄 SEC Jahresberichte (10-K)</a>"
            )
    if _link_parts:
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 14px 0;'>"
            + "".join(_link_parts)
            + "</div>",
            unsafe_allow_html=True,
        )

    if _summary:
        # Kürze auf ~4 Sätze
        _sentences = _summary.replace("  ", " ").split(". ")
        _short = ". ".join(_sentences[:4]) + ("." if len(_sentences) > 4 else "")
        st.markdown(f"""
        <div class="insight-box" style="line-height:1.7; color:{_C_TEXT_SEC}; font-size:0.92rem;">
            {_short}
            {'<details style="margin-top:8px;"><summary style="color:{_C_ACCENT};cursor:pointer;font-size:0.82rem;">Vollständige Beschreibung</summary><div style="margin-top:8px;">' + _summary + '</div></details>' if len(_sentences) > 4 else ''}
        </div>""", unsafe_allow_html=True)

    # ── Moat-Treiber ──────────────────────────────────────────────────
    if moat["moat_types"]:
        st.markdown("<div class='section-header'>⚙️ Erkannte Moat-Treiber</div>", unsafe_allow_html=True)
        tcols = st.columns(min(len(moat["moat_types"]), 3))
        for col, (title, desc) in zip(tcols, moat["moat_types"]):
            col.markdown(f"""
            <div class="metric-card" style="height:100%;">
                <div style="font-size:1.1rem; font-weight:700; color:#00e5ff; margin-bottom:10px;">{title}</div>
                <div style="color:{_C_TEXT_MUTED2}; font-size:0.83rem; line-height:1.6;">{desc}</div>
            </div>""", unsafe_allow_html=True)
        # Wenn mehr als 3 Treiber
        if len(moat["moat_types"]) > 3:
            tcols2 = st.columns(len(moat["moat_types"]) - 3)
            for col, (title, desc) in zip(tcols2, moat["moat_types"][3:]):
                col.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:1.1rem; font-weight:700; color:#00e5ff; margin-bottom:10px;">{title}</div>
                    <div style="color:{_C_TEXT_MUTED2}; font-size:0.83rem; line-height:1.6;">{desc}</div>
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
                background:{_C_CARD_BG}; border-radius:8px; border-left:3px solid #1e3a5f;">
        ⚠️ <em>Hinweis: Diese Einschätzung basiert auf quantitativen Finanzkennzahlen und Branchenheuristiken.
        Eine vollständige Moat-Analyse erfordert qualitative Recherche (Geschäftsberichte, Patente,
        Kundenbindung, Managementqualität). Keine Anlageberatung.</em>
    </div>""", unsafe_allow_html=True)

# ==================== TAB 9: PIOTROSKI F-SCORE ====================
elif _at == 5:
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
            fs_color = _C_POSITIVE; fs_label = "Starke Bilanzqualität 🏆"
            fs_text  = "Hohe operative Qualität und finanzielle Substanz. Die Fundamentaldaten stützen das Investment-Narrativ. Klassischer Buffett/Piotroski-Favorit."
        elif fs >= 6:
            fs_color = _C_POSITIVE_SFT; fs_label = "Solide Substanz ✅"
            fs_text  = "Gute finanzielle Gesundheit mit einzelnen Schwächen. Unternehmen zeigt mehrheitlich positive Bilanzsignale."
        elif fs >= 4:
            fs_color = _C_NEUTRAL; fs_label = "Gemischte Signale ⚠️"
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
                <div class="score-num" style="color:{fs_color};">{fs}<span style="font-size:1.5rem; color:{_C_TEXT_MUTED};">/{fa}</span></div>
                <div class="score-label">{fs_label}</div>
                <div style="color:{_C_TEXT_MUTED}; font-size:0.75rem; margin-top:8px;">
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
            <div class="insight-box" style="font-size:0.88rem; line-height:1.6; color:{_C_TEXT_SEC};">{fs_text}</div>
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
                    bdr   = _C_POSITIVE
                    badge = '<span class="metric-badge-green">✓ Erfüllt</span>'
                elif c["passed"] is False:
                    dot   = "❌"
                    bdr   = _C_NEGATIVE
                    badge = '<span class="metric-badge-red">✗ Nicht erfüllt</span>'
                else:
                    dot   = "⬜"
                    bdr   = "#37474f"
                    badge = '<span class="metric-badge-gray">N/A</span>'

                col.markdown(f"""
                <div class="metric-card" style="border-left:3px solid {bdr};">
                    <div class="metric-label">{c['name']}</div>
                    <div style="font-size:1.15rem; font-weight:700; color:{_C_TEXT_PRIMARY}; margin:8px 0;">{c['value']}</div>
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
                    background:{_C_CARD_BG}; border-radius:8px; border-left:3px solid #1e3a5f;">
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
            <div style="color:{_C_ACCENT}; font-size:1.0rem; font-weight:700; margin-bottom:4px;">📈 StocksMB</div>
            <div style="color:#37474f; font-size:0.75rem;">Aktienanalyse Tool · v7</div>
        </div>
        <div style="color:#37474f; font-size:0.75rem; line-height:1.6; max-width:480px; text-align:right;">
            Datenquellen: <span style="color:{_C_TEXT_MUTED};">Yahoo Finance (yFinance) · Financial Modeling Prep (FMP)</span>
        </div>
    </div>
    <div style="background:{_C_SURFACE}; border:1px solid #1e2d45; border-radius:10px; padding:14px 18px;">
        <div style="color:#ff8f00; font-size:0.75rem; font-weight:700; margin-bottom:6px; text-transform:uppercase; letter-spacing:1px;">⚠️ Disclaimer — Keine Anlageberatung</div>
        <div style="color:{_C_TEXT_MUTED}; font-size:0.75rem; line-height:1.6;">
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
