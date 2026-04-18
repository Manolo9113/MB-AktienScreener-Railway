#!/usr/bin/env python3
"""
StocksMB Trading API  v1.0
FastAPI — als zweiter Railway-Service deployen.
Start: uvicorn api:app --host 0.0.0.0 --port $PORT

Endpoints:
  GET /                      Health-Check
  GET /screener/quality      Top-Quality-Picks (Score ≥ 65, unter Fair Value)
  GET /screener/value        Value-Picks (niedrige Bewertung, Dividende, FCF)
  GET /screener/tradeable    Gut handelbare Aktien (Liquidität, Volumen, Beta)
  GET /score/{ticker}        Alle Scores für einen Ticker
  GET /signals               Kombiniertes Signal für Trading-Bot (Regime + Picks)
"""

import os
import time
import threading
from datetime import datetime, date
from typing import Optional

import requests
import yfinance as yf
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# ── Shared logic aus screener.py ──────────────────────────────────────────────
from screener import calc_score, calc_fair_value, WATCHLIST, send_telegram

app = FastAPI(
    title="StocksMB API",
    description="REST-API für StocksMB Screener & Trading Bot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("STOCKSMB_API_KEY", "")  # optional: einfacher Schlüsselschutz

# ── Value-Watchlist (~60 klassische Value-Titel) ──────────────────────────────
VALUE_WATCHLIST = [
    # Financials
    "BRK-B", "JPM", "BAC", "C", "WFC", "GS", "MS", "USB", "TFC",
    # Energie
    "XOM", "CVX", "COP", "EOG", "PSX", "VLO", "MPC", "OXY",
    # Healthcare / Pharma
    "JNJ", "PFE", "ABBV", "MRK", "BMY", "GILD", "CVS", "CI",
    # Consumer Staples
    "KO", "PEP", "PG", "WMT", "TGT", "CL", "GIS", "MO", "PM",
    # Industrie
    "GE", "CAT", "HON", "MMM", "EMR", "RTX", "LMT", "NOC",
    # Auto / Mobil
    "F", "GM", "STLA",
    # Telecom / Media
    "T", "VZ", "CMCSA", "DIS", "WBD",
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP",
    # REITs
    "SPG", "O", "VTR", "PLD", "AMT",
    # Tech Value
    "INTC", "CSCO", "IBM", "QCOM", "TXN", "HPQ",
]

# ── Tradeable-Watchlist (hohe Liquidität, gut handelbar) ─────────────────────
TRADEABLE_WATCHLIST = [
    # Mega-Cap Tech (Volumen >10M/Tag)
    "AAPL", "MSFT", "NVDA", "AMD", "INTC", "AMZN", "GOOGL", "META", "TSLA",
    # Financials liquid
    "BAC", "C", "JPM", "WFC", "GS",
    # Consumer / Industrie
    "F", "GM", "T", "GE", "XOM", "CVX",
    # Healthcare
    "PFE", "MRNA", "JNJ", "ABBV",
    # Wachstum / aktiv gehandelt
    "PLTR", "COIN", "SOFI", "HOOD", "RIVN", "NIO",
    # ETFs (höchste Liquidität)
    "SPY", "QQQ", "IWM", "XLF", "XLE", "XLK", "GLD",
]

# ── Einfacher TTL-Cache (thread-safe) ────────────────────────────────────────
_cache: dict = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 3600  # 1 Stunde


def _cache_get(key: str):
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() - entry["ts"] < _CACHE_TTL:
            return entry["data"]
    return None


def _cache_set(key: str, data):
    with _cache_lock:
        _cache[key] = {"data": data, "ts": time.time()}


# ── Value-Score (0–100): niedrige Bewertung, FCF, Dividende ──────────────────
def calc_value_score(info: dict) -> int:
    score = 0

    # P/E Ratio — Kernkennzahl für Value
    pe = info.get("trailingPE") or 0
    if 0 < pe < 10:    score += 25
    elif pe < 14:      score += 18
    elif pe < 18:      score += 10
    elif pe < 22:      score += 4

    # FCF Yield — Cashgenerierung relativ zur Marktkapitalisierung
    fcf = info.get("freeCashflow") or 0
    mkt = info.get("marketCap") or 1
    fcy = fcf / mkt if mkt else 0
    if fcy > 0.08:    score += 20
    elif fcy > 0.05:  score += 14
    elif fcy > 0.03:  score += 8
    elif fcy > 0.01:  score += 3

    # Price-to-Book — Substanzwert
    pb = info.get("priceToBook") or 0
    if 0 < pb < 1.0:  score += 15
    elif pb < 1.8:    score += 11
    elif pb < 2.8:    score += 6
    elif pb < 4.0:    score += 2

    # EV/EBITDA — Gesamtunternehmensbewertung
    ev    = info.get("enterpriseValue") or 0
    ebitda= info.get("ebitda") or 0
    if ev > 0 and ebitda > 0:
        ev_eb = ev / ebitda
        if ev_eb < 6:    score += 15
        elif ev_eb < 9:  score += 10
        elif ev_eb < 13: score += 5

    # Verschuldung — Sicherheitspuffer
    de = info.get("debtToEquity") or 0
    if de < 20:    score += 10
    elif de < 60:  score += 7
    elif de < 100: score += 3

    # Dividendenrendite — Einkommenskomponente
    dy = (info.get("dividendYield") or 0) * 100
    if dy > 5:     score += 10
    elif dy > 3:   score += 7
    elif dy > 1.5: score += 4
    elif dy > 0:   score += 1

    # Positives Umsatzwachstum (modest für Value)
    rg = info.get("revenueGrowth") or 0
    if rg > 0.08:  score += 5
    elif rg >= 0:  score += 2

    return min(score, 100)


# ── Tradeable-Score (0–100): Liquidität, Volumen, Handelbarkeit ───────────────
def calc_tradeable_score(info: dict) -> int:
    score = 0

    # Marktkapitalisierung — größere Unternehmen = liquider
    mkt = info.get("marketCap") or 0
    if mkt > 500e9:    score += 25  # Mega Cap
    elif mkt > 100e9:  score += 20  # Large Cap
    elif mkt > 20e9:   score += 13  # Mid-Large Cap
    elif mkt > 5e9:    score += 6   # Mid Cap

    # Durchschnittliches Tagesvolumen (Shares) — Hauptliquiditätsindikator
    vol = info.get("averageVolume") or 0
    if vol > 30e6:    score += 30
    elif vol > 10e6:  score += 23
    elif vol > 3e6:   score += 14
    elif vol > 1e6:   score += 6
    elif vol > 300e3: score += 2

    # Beta — Volatilität für Trading-Chancen
    beta = abs(info.get("beta") or 1)
    if 0.8 <= beta <= 1.5:   score += 20  # ideal
    elif 1.5 < beta <= 2.5:  score += 15  # hohe Volatilität
    elif 0.5 <= beta < 0.8:  score += 10  # niedrige Volatilität
    elif beta > 2.5:          score += 8   # zu volatil

    # Kurs — keine Penny Stocks
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    if price > 50:   score += 15
    elif price > 20: score += 10
    elif price > 10: score += 5

    # Short-Float — zu hoher Short könnte auf Probleme hindeuten
    si = (info.get("shortPercentOfFloat") or 0) * 100
    if si < 3:    score += 10
    elif si < 8:  score += 7
    elif si < 15: score += 3

    return min(score, 100)


# ── Hilfsfunktion: Ticker-Daten laden ────────────────────────────────────────
def _fetch_ticker(tkr: str) -> dict:
    cached = _cache_get(f"ticker_{tkr}")
    if cached:
        return cached
    info = yf.Ticker(tkr).info
    _cache_set(f"ticker_{tkr}", info)
    return info


# ── Screener-Kern ─────────────────────────────────────────────────────────────
def _run_screener(watchlist: list, score_fn, min_score: int,
                  require_fv: bool = False, top_n: int = 10) -> list:
    results = []
    for tkr in watchlist:
        try:
            info  = _fetch_ticker(tkr)
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            if not price:
                continue
            sc = score_fn(info)
            fv = calc_fair_value(info)
            if sc < min_score:
                continue
            if require_fv and (not fv or price >= fv * 0.95):
                continue
            entry = {
                "ticker":   tkr,
                "name":     (info.get("shortName") or tkr)[:30],
                "price":    round(price, 2),
                "score":    sc,
                "currency": info.get("currency", "USD"),
                "sector":   info.get("sector", ""),
                "mktcap_b": round((info.get("marketCap") or 0) / 1e9, 1),
            }
            if fv:
                entry["fair_value"] = fv
                entry["discount_pct"] = round((fv - price) / fv * 100, 1)
            results.append(entry)
            time.sleep(0.5)
        except Exception:
            continue
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


# ═══════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "app": "StocksMB API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoints": [
            "/screener/quality", "/screener/value", "/screener/tradeable",
            "/score/{ticker}", "/signals",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok", "ts": datetime.utcnow().isoformat() + "Z"}


@app.get("/screener/quality")
def screener_quality(
    top_n: int = Query(5, ge=1, le=20),
    min_score: int = Query(65, ge=0, le=100),
):
    """Top-Qualitätsaktien unter ihrem Fair Value (bestehende Screener-Logik)."""
    cached = _cache_get(f"quality_{top_n}_{min_score}")
    if cached:
        return cached
    results = _run_screener(WATCHLIST, calc_score, min_score,
                            require_fv=True, top_n=top_n)
    out = {
        "type": "quality",
        "date": date.today().isoformat(),
        "count": len(results),
        "picks": results,
        "criteria": f"Quality-Score ≥ {min_score}, Kurs ≥ 5% unter Fair Value",
    }
    _cache_set(f"quality_{top_n}_{min_score}", out)
    return out


@app.get("/screener/value")
def screener_value(
    top_n: int = Query(10, ge=1, le=30),
    min_score: int = Query(55, ge=0, le=100),
):
    """Value-Aktien: niedrige Bewertung (P/E, P/B, EV/EBITDA), FCF, Dividende."""
    cached = _cache_get(f"value_{top_n}_{min_score}")
    if cached:
        return cached
    results = _run_screener(VALUE_WATCHLIST, calc_value_score, min_score,
                            require_fv=False, top_n=top_n)
    # Felder anreichern
    for r in results:
        try:
            info = _fetch_ticker(r["ticker"])
            r["pe"]        = round(info.get("trailingPE") or 0, 1)
            r["pb"]        = round(info.get("priceToBook") or 0, 2)
            r["div_yield"] = round((info.get("dividendYield") or 0) * 100, 2)
            ev    = info.get("enterpriseValue") or 0
            ebitda= info.get("ebitda") or 1
            r["ev_ebitda"] = round(ev / ebitda, 1) if ebitda else None
            fcf   = info.get("freeCashflow") or 0
            mkt   = info.get("marketCap") or 1
            r["fcf_yield"] = round(fcf / mkt * 100, 2)
        except Exception:
            pass
    out = {
        "type": "value",
        "date": date.today().isoformat(),
        "count": len(results),
        "picks": results,
        "criteria": f"Value-Score ≥ {min_score} (P/E, P/B, EV/EBITDA, FCF-Yield, Div.)",
    }
    _cache_set(f"value_{top_n}_{min_score}", out)
    return out


@app.get("/screener/tradeable")
def screener_tradeable(top_n: int = Query(15, ge=1, le=30)):
    """Gut handelbare Aktien: hohes Volumen, gute Liquidität, nützliche Volatilität."""
    cached = _cache_get(f"tradeable_{top_n}")
    if cached:
        return cached
    results = []
    for tkr in TRADEABLE_WATCHLIST:
        try:
            info  = _fetch_ticker(tkr)
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            sc    = calc_tradeable_score(info)
            results.append({
                "ticker":      tkr,
                "name":        (info.get("shortName") or tkr)[:30],
                "price":       round(price, 2),
                "score":       sc,
                "volume_m":    round((info.get("averageVolume") or 0) / 1e6, 1),
                "beta":        round(info.get("beta") or 1, 2),
                "mktcap_b":    round((info.get("marketCap") or 0) / 1e9, 1),
                "currency":    info.get("currency", "USD"),
                "sector":      info.get("sector", ""),
            })
            time.sleep(0.4)
        except Exception:
            continue
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_n]
    out = {
        "type": "tradeable",
        "date": date.today().isoformat(),
        "count": len(results),
        "picks": results,
        "criteria": "Tradeable-Score (Marktkapitalisierung, Volumen, Beta, Kurs)",
    }
    _cache_set(f"tradeable_{top_n}", out)
    return out


@app.get("/score/{ticker}")
def get_score(ticker: str):
    """Alle Scores (Quality, Value, Tradeable) + Fair Value für einen Ticker."""
    tkr = ticker.upper()
    cached = _cache_get(f"score_{tkr}")
    if cached:
        return cached
    try:
        info  = yf.Ticker(tkr).info
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        if not price:
            raise HTTPException(status_code=404, detail=f"Kein Kurs für {tkr} gefunden")

        fv    = calc_fair_value(info)
        q_sc  = calc_score(info)
        v_sc  = calc_value_score(info)
        t_sc  = calc_tradeable_score(info)
        fcf   = info.get("freeCashflow") or 0
        mkt   = info.get("marketCap") or 1

        out = {
            "ticker":        tkr,
            "name":          info.get("shortName", tkr),
            "price":         round(price, 2),
            "currency":      info.get("currency", "USD"),
            "sector":        info.get("sector", ""),
            "mktcap_b":      round(mkt / 1e9, 1),
            "scores": {
                "quality":   q_sc,
                "value":     v_sc,
                "tradeable": t_sc,
                "composite": round((q_sc * 0.4 + v_sc * 0.35 + t_sc * 0.25), 1),
            },
            "fair_value":    fv,
            "discount_pct":  round((fv - price) / fv * 100, 1) if fv else None,
            "metrics": {
                "pe":          round(info.get("trailingPE") or 0, 1),
                "fwd_pe":      round(info.get("forwardPE") or 0, 1),
                "pb":          round(info.get("priceToBook") or 0, 2),
                "fcf_yield":   round(fcf / mkt * 100, 2),
                "roe":         round((info.get("returnOnEquity") or 0) * 100, 1),
                "div_yield":   round((info.get("dividendYield") or 0) * 100, 2),
                "gross_margin":round((info.get("grossMargins") or 0) * 100, 1),
                "op_margin":   round((info.get("operatingMargins") or 0) * 100, 1),
                "revenue_growth": round((info.get("revenueGrowth") or 0) * 100, 1),
                "debt_equity": round(info.get("debtToEquity") or 0, 1),
                "beta":        round(info.get("beta") or 1, 2),
                "volume_m":    round((info.get("averageVolume") or 0) / 1e6, 1),
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        _cache_set(f"score_{tkr}", out)
        return out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals")
def get_signals(top_n: int = Query(5, ge=1, le=10)):
    """
    Kombiniertes Trading-Signal für den Bot.
    Gibt Macro-Regime + Top-Picks beider Screener zurück.
    """
    cached = _cache_get(f"signals_{top_n}")
    if cached:
        return cached

    # Makro-Regime: Zinskurve (T10Y2Y) als einfaches Signal
    macro_signal = "Neutral"
    macro_note   = ""
    try:
        r = requests.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T10Y2Y",
            timeout=8,
        )
        if r.ok:
            lines = [l for l in r.text.strip().split("\n")[1:]
                     if l.split(",")[1].strip() not in (".", "")]
            if lines:
                spread = float(lines[-1].split(",")[1])
                if spread > 0.5:
                    macro_signal, macro_note = "Risk-On",  f"Zinskurve normal (+{spread:.2f}%)"
                elif spread > -0.2:
                    macro_signal, macro_note = "Neutral",  f"Zinskurve flach ({spread:.2f}%)"
                else:
                    macro_signal, macro_note = "Risk-Off", f"Zinskurve invertiert ({spread:.2f}%)"
    except Exception:
        macro_note = "Makro-Daten nicht verfügbar"

    # HY Spreads als zweites Risikosignal
    hy_signal = "OK"
    try:
        r2 = requests.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLH0A0HYM2",
            timeout=8,
        )
        if r2.ok:
            lines2 = [l for l in r2.text.strip().split("\n")[1:]
                      if l.split(",")[1].strip() not in (".", "")]
            if lines2:
                hy_spread = float(lines2[-1].split(",")[1])
                if hy_spread > 600:
                    hy_signal = "STRESS"
                    if macro_signal == "Risk-On":
                        macro_signal = "Neutral"
                elif hy_spread > 400:
                    hy_signal = "ELEVATED"
    except Exception:
        pass

    # Quality + Value Picks
    q_picks = _run_screener(WATCHLIST,       calc_score,       65, require_fv=True,  top_n=top_n)
    v_picks = _run_screener(VALUE_WATCHLIST, calc_value_score, 55, require_fv=False, top_n=top_n)

    # Bot-Empfehlung
    if macro_signal == "Risk-On" and hy_signal == "OK":
        action = "BUY"
        reason = "Makro Risk-On, Kreditmärkte stabil"
    elif macro_signal == "Risk-Off" or hy_signal == "STRESS":
        action = "HOLD/SELL"
        reason = "Makro Risk-Off oder Kreditstress — defensiv bleiben"
    else:
        action = "SELECTIVE"
        reason = "Neutrales Umfeld — nur Top-Scorer kaufen"

    out = {
        "date":         date.today().isoformat(),
        "timestamp":    datetime.utcnow().isoformat() + "Z",
        "macro": {
            "regime":    macro_signal,
            "note":      macro_note,
            "hy_signal": hy_signal,
        },
        "bot_action":   action,
        "bot_reason":   reason,
        "quality_picks": q_picks,
        "value_picks":   v_picks,
    }
    _cache_set(f"signals_{top_n}", out)
    return out
