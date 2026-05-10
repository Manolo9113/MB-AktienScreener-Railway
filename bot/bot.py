#!/usr/bin/env python3
"""
StocksMB Paper-Trading Bot  v2.0
Pollt die StocksMB API während Handelszeiten (Mo–Fr, 15:30–22:00 MEZ).

Umgebungsvariablen:
  STOCKSMB_API_URL      z.B. https://stocksmb-api.railway.app
  STOCKSMB_API_KEY      optional
  TELEGRAM_BOT_TOKEN    für Trade-Notifications
  TELEGRAM_CHAT_ID      Ziel-Chat

Strategie — zwei Modi parallel:

  DAYTRADING (Priorität, bis 3 Slots):
    BUY:  DT-Score ≥ 60, ATR% ≥ 2.5%, Macro ≠ Risk-Off
          15% des Portfolios pro Position, Polling alle 5 Min
    SELL: Stop-Loss −3% · Take-Profit +8% · Zwangs-Close 21:45 MEZ

  QUALITY/SWING (bis 2 Slots):
    BUY:  Quality-Score ≥ 70, Discount ≥ 6%, Macro = Risk-On
          20% des Portfolios pro Position, Polling alle 15 Min
    SELL: Stop-Loss −5% · Take-Profit +15% · Macro Risk-Off → alles verkaufen
"""

import os
import json
import time
import schedule
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# ── Konfiguration ─────────────────────────────────────────────────────────────
API_URL    = os.environ.get("STOCKSMB_API_URL", "http://localhost:8000").rstrip("/")
API_KEY    = os.environ.get("STOCKSMB_API_KEY", "")
TG_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), "portfolio.json")
INITIAL_CASH   = 100_000.0
MEZ            = ZoneInfo("Europe/Berlin")
HEADERS        = {"X-API-Key": API_KEY} if API_KEY else {}

# Daytrading-Slots
MAX_DT_POSITIONS  = 3
DT_POSITION_SIZE  = 0.15     # 15% pro DT-Position
DT_STOP_LOSS      = -0.03    # −3%
DT_TAKE_PROFIT    = +0.08    # +8%
MIN_DT_SCORE      = 60
MIN_ATR_PCT       = 2.5

# Quality/Swing-Slots
MAX_QU_POSITIONS  = 2
QU_POSITION_SIZE  = 0.20     # 20% pro Quality-Position
QU_STOP_LOSS      = -0.05    # −5%
QU_TAKE_PROFIT    = +0.15    # +15%
MIN_QU_SCORE      = 70
MIN_DISCOUNT      = 6.0


# ── Telegram ──────────────────────────────────────────────────────────────────
def _telegram(msg: str) -> None:
    if not TG_TOKEN or not TG_CHAT_ID:
        print(f"[Telegram] {msg}")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception as e:
        print(f"[Telegram-Fehler] {e}")


# ── Portfolio ─────────────────────────────────────────────────────────────────
def _load_portfolio() -> dict:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {
        "cash":      INITIAL_CASH,
        "positions": {},  # ticker → {shares, entry_price, entry_date, score, mode}
        "trades":    [],
        "created":   datetime.now(MEZ).isoformat(),
    }


def _save_portfolio(pf: dict) -> None:
    pf["updated"] = datetime.now(MEZ).isoformat()
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(pf, f, indent=2, ensure_ascii=False)


# ── API-Aufrufe ───────────────────────────────────────────────────────────────
def _api_signals() -> dict:
    r = requests.get(f"{API_URL}/signals", headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def _api_daytrading(top_n: int = 6) -> list:
    r = requests.get(
        f"{API_URL}/screener/daytrading",
        params={"top_n": top_n, "min_atr_pct": MIN_ATR_PCT, "min_score": MIN_DT_SCORE},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("results", [])


def _current_price(ticker: str) -> float:
    r = requests.get(f"{API_URL}/score/{ticker}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json().get("price", 0.0)


# ── Portfolio-Kennzahlen ──────────────────────────────────────────────────────
def _portfolio_value(pf: dict) -> float:
    total = pf["cash"]
    for tkr, pos in pf["positions"].items():
        try:
            total += pos["shares"] * _current_price(tkr)
        except Exception:
            total += pos["shares"] * pos["entry_price"]
    return total


def _count_by_mode(pf: dict, mode: str) -> int:
    return sum(1 for p in pf["positions"].values() if p.get("mode") == mode)


def _open_pnl(pf: dict) -> dict:
    result = {}
    for tkr, pos in pf["positions"].items():
        try:
            price = _current_price(tkr)
            pnl   = (price - pos["entry_price"]) / pos["entry_price"] * 100
            result[tkr] = {"current_price": price, "pnl_pct": round(pnl, 2), "mode": pos.get("mode", "?")}
        except Exception:
            result[tkr] = {"current_price": None, "pnl_pct": None, "mode": pos.get("mode", "?")}
    return result


# ── Handelsstunden ─────────────────────────────────────────────────────────────
def _is_market_open() -> bool:
    now = datetime.now(MEZ)
    if now.weekday() >= 5:
        return False
    h = now.hour + now.minute / 60
    return 15.5 <= h < 22.0


def _is_dt_window() -> bool:
    """Daytrading nur während aktiver US-Session, nicht in letzten 15 Minuten."""
    now = datetime.now(MEZ)
    if now.weekday() >= 5:
        return False
    h = now.hour + now.minute / 60
    return 15.5 <= h < 21.75  # bis 21:45 neue DT-Positionen öffnen


# ── BUY — Daytrading ──────────────────────────────────────────────────────────
def _try_buy_daytrading(pf: dict, regime: str) -> None:
    if regime == "Risk-Off":
        print("[DT-Bot] Risk-Off — kein Daytrading")
        return
    if not _is_dt_window():
        return

    slots_free = MAX_DT_POSITIONS - _count_by_mode(pf, "daytrading")
    if slots_free <= 0:
        print(f"[DT-Bot] Alle {MAX_DT_POSITIONS} Daytrading-Slots belegt")
        return

    try:
        dt_picks = _api_daytrading(top_n=slots_free + 3)
    except Exception as e:
        print(f"[DT-Bot] Screener-Fehler: {e}")
        return

    pf_val = _portfolio_value(pf)

    for pick in dt_picks:
        if slots_free <= 0:
            break
        tkr      = pick["ticker"]
        score    = pick.get("score", 0)
        atr_pct  = pick.get("atr_pct", 0)
        price    = pick.get("price", 0)

        if tkr in pf["positions"]:
            continue
        if score < MIN_DT_SCORE or atr_pct < MIN_ATR_PCT or price <= 0:
            continue

        position_cash = pf_val * DT_POSITION_SIZE
        shares        = int(position_cash / price)
        if shares <= 0:
            continue
        cost = shares * price
        if cost > pf["cash"]:
            continue

        pf["cash"] -= cost
        pf["positions"][tkr] = {
            "shares":      shares,
            "entry_price": price,
            "entry_date":  datetime.now(MEZ).isoformat(),
            "score":       score,
            "atr_pct":     atr_pct,
            "mode":        "daytrading",
        }
        pf["trades"].append({
            "action": "BUY", "mode": "daytrading",
            "ticker": tkr, "shares": shares,
            "price": price, "cost": round(cost, 2),
            "score": score, "atr_pct": atr_pct,
            "regime": regime, "ts": datetime.now(MEZ).isoformat(),
        })

        _telegram(
            f"⚡ <b>PAPER BUY [DT] — {tkr}</b>\n"
            f"   Kurs: {price:.2f} USD · {shares} Stk · {cost:,.0f} USD\n"
            f"   DT-Score: {score}/100 · ATR: {atr_pct:.1f}%\n"
            f"   SL: −{abs(DT_STOP_LOSS)*100:.0f}% · TP: +{DT_TAKE_PROFIT*100:.0f}%"
        )
        print(f"[DT-BUY] {tkr} @ {price:.2f} × {shares} = {cost:,.0f} USD")
        slots_free -= 1


# ── BUY — Quality/Swing ───────────────────────────────────────────────────────
def _try_buy_quality(pf: dict, signals: dict) -> None:
    regime = signals.get("macro", {}).get("regime", "Neutral")
    if regime == "Risk-Off":
        return

    slots_free = MAX_QU_POSITIONS - _count_by_mode(pf, "quality")
    if slots_free <= 0:
        print(f"[QU-Bot] Alle {MAX_QU_POSITIONS} Quality-Slots belegt")
        return

    pf_val = _portfolio_value(pf)
    picks  = signals.get("quality_picks", [])

    for pick in picks:
        if slots_free <= 0:
            break
        tkr      = pick["ticker"]
        score    = pick.get("score", 0)
        discount = pick.get("discount_pct", 0) or 0
        price    = pick.get("price", 0)

        if tkr in pf["positions"]:
            continue
        if score < MIN_QU_SCORE or discount < MIN_DISCOUNT or price <= 0:
            continue

        position_cash = pf_val * QU_POSITION_SIZE
        shares        = int(position_cash / price)
        if shares <= 0:
            continue
        cost = shares * price
        if cost > pf["cash"]:
            continue

        pf["cash"] -= cost
        pf["positions"][tkr] = {
            "shares":      shares,
            "entry_price": price,
            "entry_date":  datetime.now(MEZ).isoformat(),
            "score":       score,
            "fair_value":  pick.get("fair_value"),
            "mode":        "quality",
        }
        pf["trades"].append({
            "action": "BUY", "mode": "quality",
            "ticker": tkr, "shares": shares,
            "price": price, "cost": round(cost, 2),
            "score": score, "discount_pct": discount,
            "regime": regime, "ts": datetime.now(MEZ).isoformat(),
        })

        _telegram(
            f"🟢 <b>PAPER BUY [Quality] — {tkr}</b>\n"
            f"   Kurs: {price:.2f} USD · {shares} Stk · {cost:,.0f} USD\n"
            f"   Score: {score}/100 · Discount: {discount:.1f}%\n"
            f"   SL: −{abs(QU_STOP_LOSS)*100:.0f}% · TP: +{QU_TAKE_PROFIT*100:.0f}%"
        )
        print(f"[QU-BUY] {tkr} @ {price:.2f} × {shares} = {cost:,.0f} USD")
        slots_free -= 1


# ── SELL — SL/TP je Mode ──────────────────────────────────────────────────────
def _check_sells(pf: dict, regime: str) -> None:
    to_sell = []

    for tkr, pos in pf["positions"].items():
        mode = pos.get("mode", "quality")
        sl   = DT_STOP_LOSS  if mode == "daytrading" else QU_STOP_LOSS
        tp   = DT_TAKE_PROFIT if mode == "daytrading" else QU_TAKE_PROFIT

        try:
            price = _current_price(tkr)
        except Exception:
            continue
        pnl = (price - pos["entry_price"]) / pos["entry_price"]

        reason = None
        if pnl <= sl:
            reason = f"Stop-Loss ({pnl*100:.1f}%)"
        elif pnl >= tp:
            reason = f"Take-Profit ({pnl*100:.1f}%)"
        elif regime == "Risk-Off" and mode == "quality":
            reason = f"Macro Risk-Off (P&L: {pnl*100:.1f}%)"

        if reason:
            to_sell.append((tkr, price, pnl, reason, mode))

    for tkr, price, pnl, reason, mode in to_sell:
        _execute_sell(pf, tkr, price, pnl, reason, mode)


def _close_daytrading_positions(pf: dict) -> None:
    """Schließt alle offenen Daytrading-Positionen zum Handelsschluss (21:45 MEZ)."""
    dt_tickers = [t for t, p in pf["positions"].items() if p.get("mode") == "daytrading"]
    if not dt_tickers:
        return
    print(f"[DT-Close] Schließe {len(dt_tickers)} DT-Positionen zum Tagesende …")
    for tkr in dt_tickers:
        pos = pf["positions"].get(tkr)
        if not pos:
            continue
        try:
            price = _current_price(tkr)
        except Exception:
            price = pos["entry_price"]
        pnl = (price - pos["entry_price"]) / pos["entry_price"]
        _execute_sell(pf, tkr, price, pnl, "Tagesschluss-Close", "daytrading")
    _save_portfolio(pf)


def _execute_sell(pf: dict, tkr: str, price: float, pnl: float, reason: str, mode: str) -> None:
    pos      = pf["positions"].pop(tkr, None)
    if not pos:
        return
    proceeds = pos["shares"] * price
    profit   = proceeds - pos["shares"] * pos["entry_price"]
    pf["cash"] += proceeds

    pf["trades"].append({
        "action": "SELL", "mode": mode,
        "ticker": tkr, "shares": pos["shares"],
        "price": price, "proceeds": round(proceeds, 2),
        "profit": round(profit, 2), "pnl_pct": round(pnl * 100, 2),
        "reason": reason, "ts": datetime.now(MEZ).isoformat(),
    })

    tag   = "⚡" if mode == "daytrading" else ("🔴" if pnl < 0 else "🟡")
    label = "DT" if mode == "daytrading" else "Quality"
    _telegram(
        f"{tag} <b>PAPER SELL [{label}] — {tkr}</b>\n"
        f"   Kurs: {price:.2f} USD · Erlös: {proceeds:,.0f} USD\n"
        f"   P&L: {profit:+,.0f} USD ({pnl*100:+.1f}%)\n"
        f"   Grund: {reason}"
    )
    print(f"[{label}-SELL] {tkr} @ {price:.2f} — {reason} — P&L: {profit:+,.0f}")


# ── Täglicher Status-Report ───────────────────────────────────────────────────
def _daily_report(pf: dict) -> None:
    pf_val  = _portfolio_value(pf)
    total_r = (pf_val - INITIAL_CASH) / INITIAL_CASH * 100
    pnl_map = _open_pnl(pf)

    dt_trades  = [t for t in pf["trades"] if t.get("mode") == "daytrading" and t["action"] == "SELL"]
    qu_trades  = [t for t in pf["trades"] if t.get("mode") == "quality"    and t["action"] == "SELL"]
    dt_profit  = sum(t.get("profit", 0) for t in dt_trades)
    qu_profit  = sum(t.get("profit", 0) for t in qu_trades)

    lines = [
        f"📊 <b>StocksMB Bot v2 — Tagesbericht {_date_str()}</b>",
        f"   Portfolio: {pf_val:,.0f} USD ({total_r:+.1f}% ggü. Start)",
        f"   Cash: {pf['cash']:,.0f} USD",
        f"",
        f"   ⚡ DT-Slots: {_count_by_mode(pf, 'daytrading')}/{MAX_DT_POSITIONS} "
        f"· Realisiert: {dt_profit:+,.0f} USD ({len(dt_trades)} Trades)",
        f"   💎 Quality-Slots: {_count_by_mode(pf, 'quality')}/{MAX_QU_POSITIONS} "
        f"· Realisiert: {qu_profit:+,.0f} USD ({len(qu_trades)} Trades)",
    ]
    if pnl_map:
        lines.append("")
        for tkr, d in pnl_map.items():
            p     = d.get("pnl_pct")
            label = "⚡" if d.get("mode") == "daytrading" else "💎"
            lines.append(
                f"   {label} {'🟢' if (p or 0) >= 0 else '🔴'} {tkr}: {p:+.1f}%"
                if p else f"   {label} ⚪ {tkr}: k.A."
            )
    _telegram("\n".join(lines))


def _date_str() -> str:
    return datetime.now(MEZ).strftime("%d.%m.%Y")


# ── Haupt-Zyklen ───────────────────────────────────────────────────────────────
def run_daytrading_cycle() -> None:
    if not _is_market_open():
        return
    print(f"[{datetime.now(MEZ).strftime('%H:%M')}] DT-Zyklus …")
    pf = _load_portfolio()
    try:
        signals = _api_signals()
        regime  = signals.get("macro", {}).get("regime", "Neutral")
        _check_sells(pf, regime)
        _try_buy_daytrading(pf, regime)
        _save_portfolio(pf)
    except Exception as e:
        print(f"[DT-Fehler] {e}")
        _telegram(f"⚠️ <b>DT-Bot-Fehler:</b> {e}")


def run_quality_cycle() -> None:
    if not _is_market_open():
        return
    print(f"[{datetime.now(MEZ).strftime('%H:%M')}] Quality-Zyklus …")
    pf = _load_portfolio()
    try:
        signals = _api_signals()
        _try_buy_quality(pf, signals)
        _save_portfolio(pf)
    except Exception as e:
        print(f"[QU-Fehler] {e}")
        _telegram(f"⚠️ <b>Quality-Bot-Fehler:</b> {e}")


def run_eod_close() -> None:
    """21:45 MEZ — alle DT-Positionen zwangsweise schließen."""
    now = datetime.now(MEZ)
    if now.weekday() >= 5:
        return
    pf = _load_portfolio()
    _close_daytrading_positions(pf)


# ── Scheduler ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  StocksMB Paper-Trading Bot v2.0")
    print(f"  API: {API_URL}")
    print(f"  DT-Slots: {MAX_DT_POSITIONS} · SL {DT_STOP_LOSS*100:.0f}% · TP +{DT_TAKE_PROFIT*100:.0f}%")
    print(f"  QU-Slots: {MAX_QU_POSITIONS} · SL {QU_STOP_LOSS*100:.0f}% · TP +{QU_TAKE_PROFIT*100:.0f}%")
    print("=" * 55)

    pf = _load_portfolio()
    _telegram(
        f"🤖 <b>Bot v2.0 gestartet — {_date_str()}</b>\n"
        f"   API: {API_URL}\n"
        f"   ⚡ Daytrading: {MAX_DT_POSITIONS} Slots · SL −{abs(DT_STOP_LOSS)*100:.0f}% · "
        f"TP +{DT_TAKE_PROFIT*100:.0f}% · Close 21:45\n"
        f"   💎 Quality: {MAX_QU_POSITIONS} Slots · SL −{abs(QU_STOP_LOSS)*100:.0f}% · "
        f"TP +{QU_TAKE_PROFIT*100:.0f}%\n"
        f"   Startkapital: {pf['cash']:,.0f} USD"
    )

    # Daytrading: alle 5 Minuten
    schedule.every(5).minutes.do(run_daytrading_cycle)
    # Quality/Swing: alle 15 Minuten
    schedule.every(15).minutes.do(run_quality_cycle)
    # DT zwangsweise schließen um 21:45
    schedule.every().day.at("21:45").do(run_eod_close)
    # Tagesbericht um 22:05
    schedule.every().day.at("22:05").do(lambda: _daily_report(_load_portfolio()))

    # Sofort starten
    run_daytrading_cycle()
    run_quality_cycle()

    while True:
        schedule.run_pending()
        time.sleep(15)
