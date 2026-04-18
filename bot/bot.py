#!/usr/bin/env python3
"""
StocksMB Paper-Trading Bot  v1.0
Pollt die StocksMB API alle 15 Minuten während Handelszeiten (Mo–Fr, 15:30–22:00 MEZ).
Führt Paper-Trades durch, speichert Portfolio lokal, meldet via Telegram.

Umgebungsvariablen:
  STOCKSMB_API_URL      z.B. https://stocksmb-api.railway.app
  STOCKSMB_API_KEY      optional (wenn API-Key gesetzt)
  TELEGRAM_BOT_TOKEN    für Trade-Notifications
  TELEGRAM_CHAT_ID      Ziel-Chat

Strategie (Paper-Trading):
  BUY:  Wenn Macro = Risk-On + Quality-Score ≥ 70 + Discount ≥ 8%
        Max. 5 gleichzeitige Positionen, je Position 20% des Portfolios
  SELL: Stop-Loss −5%, Take-Profit +15%, oder Macro wechselt auf Risk-Off
"""

import os
import json
import time
import schedule
import requests
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# ── Konfiguration ─────────────────────────────────────────────────────────────
API_URL     = os.environ.get("STOCKSMB_API_URL", "http://localhost:8000").rstrip("/")
API_KEY     = os.environ.get("STOCKSMB_API_KEY", "")
TG_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID", "")

PORTFOLIO_FILE  = os.path.join(os.path.dirname(__file__), "portfolio.json")
INITIAL_CASH    = 100_000.0   # Startkapital (Paper)
MAX_POSITIONS   = 5           # Max. gleichzeitige Positionen
POSITION_SIZE   = 0.20        # 20% des Portfolios pro Position
STOP_LOSS       = -0.05       # −5% Stop-Loss
TAKE_PROFIT     = +0.15       # +15% Take-Profit
MIN_QUALITY_SC  = 70          # Mindest-Quality-Score zum Kaufen
MIN_DISCOUNT    = 6.0         # Mindest-Abschlag vom Fair Value (%)
MEZ             = ZoneInfo("Europe/Berlin")

HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}


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


# ── Portfolio laden / speichern ───────────────────────────────────────────────
def _load_portfolio() -> dict:
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {
        "cash":      INITIAL_CASH,
        "positions": {},   # ticker → {shares, entry_price, entry_date, score}
        "trades":    [],   # Trade-Protokoll
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


def _api_score(ticker: str) -> dict:
    r = requests.get(f"{API_URL}/score/{ticker}", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()


def _current_price(ticker: str) -> float:
    """Aktuellen Kurs via API holen (nutzt Score-Endpoint)."""
    data = _api_score(ticker)
    return data.get("price", 0.0)


# ── Portfolio-Kennzahlen ──────────────────────────────────────────────────────
def _portfolio_value(pf: dict) -> float:
    total = pf["cash"]
    for tkr, pos in pf["positions"].items():
        try:
            price = _current_price(tkr)
            total += pos["shares"] * price
        except Exception:
            total += pos["shares"] * pos["entry_price"]
    return total


def _open_pnl(pf: dict) -> dict:
    result = {}
    for tkr, pos in pf["positions"].items():
        try:
            price = _current_price(tkr)
            pnl   = (price - pos["entry_price"]) / pos["entry_price"] * 100
            result[tkr] = {"current_price": price, "pnl_pct": round(pnl, 2)}
        except Exception:
            result[tkr] = {"current_price": None, "pnl_pct": None}
    return result


# ── Handelsstunden prüfen ─────────────────────────────────────────────────────
def _is_market_open() -> bool:
    now = datetime.now(MEZ)
    if now.weekday() >= 5:          # Samstag / Sonntag
        return False
    h = now.hour + now.minute / 60
    return 15.5 <= h < 22.0         # NYSE: 15:30–22:00 MEZ


# ── BUY-Logik ─────────────────────────────────────────────────────────────────
def _try_buy(pf: dict, signals: dict) -> None:
    macro   = signals.get("macro", {})
    regime  = macro.get("regime", "Neutral")
    picks   = signals.get("quality_picks", [])
    pf_val  = _portfolio_value(pf)

    if regime == "Risk-Off":
        print(f"[Bot] Macro Risk-Off — kein Kauf")
        return
    if len(pf["positions"]) >= MAX_POSITIONS:
        print(f"[Bot] Max. Positionen ({MAX_POSITIONS}) erreicht")
        return

    for pick in picks:
        tkr      = pick["ticker"]
        score    = pick.get("score", 0)
        discount = pick.get("discount_pct", 0)
        price    = pick.get("price", 0)

        if tkr in pf["positions"]:
            continue
        if score < MIN_QUALITY_SC:
            continue
        if (discount or 0) < MIN_DISCOUNT:
            continue
        if price <= 0:
            continue

        position_cash = pf_val * POSITION_SIZE
        shares        = int(position_cash / price)
        if shares <= 0:
            continue
        cost = shares * price
        if cost > pf["cash"]:
            continue

        # Kaufen
        pf["cash"] -= cost
        pf["positions"][tkr] = {
            "shares":      shares,
            "entry_price": price,
            "entry_date":  datetime.now(MEZ).isoformat(),
            "score":       score,
            "fair_value":  pick.get("fair_value"),
        }
        trade = {
            "action": "BUY", "ticker": tkr, "shares": shares,
            "price": price, "cost": round(cost, 2),
            "score": score, "discount_pct": discount,
            "regime": regime,
            "ts": datetime.now(MEZ).isoformat(),
        }
        pf["trades"].append(trade)

        msg = (
            f"🟢 <b>PAPER BUY — {tkr}</b>\n"
            f"   Kurs: {price:.2f} USD · {shares} Stk · Kosten: {cost:,.0f} USD\n"
            f"   Score: {score}/100 · Discount: {discount:.1f}%\n"
            f"   Regime: {regime} · Portfolio: {_portfolio_value(pf):,.0f} USD"
        )
        _telegram(msg)
        print(f"[BUY] {tkr} @ {price:.2f} × {shares} = {cost:,.0f} USD")

        if len(pf["positions"]) >= MAX_POSITIONS:
            break


# ── SELL-Logik ────────────────────────────────────────────────────────────────
def _check_sells(pf: dict, regime: str) -> None:
    to_sell = []

    for tkr, pos in pf["positions"].items():
        try:
            price = _current_price(tkr)
        except Exception:
            continue
        pnl = (price - pos["entry_price"]) / pos["entry_price"]

        reason = None
        if pnl <= STOP_LOSS:
            reason = f"Stop-Loss ({pnl*100:.1f}%)"
        elif pnl >= TAKE_PROFIT:
            reason = f"Take-Profit ({pnl*100:.1f}%)"
        elif regime == "Risk-Off":
            reason = f"Macro Risk-Off (P&L: {pnl*100:.1f}%)"

        if reason:
            to_sell.append((tkr, price, pnl, reason))

    for tkr, price, pnl, reason in to_sell:
        pos      = pf["positions"].pop(tkr)
        proceeds = pos["shares"] * price
        pf["cash"] += proceeds
        profit   = proceeds - pos["shares"] * pos["entry_price"]

        trade = {
            "action": "SELL", "ticker": tkr, "shares": pos["shares"],
            "price": price, "proceeds": round(proceeds, 2),
            "profit": round(profit, 2), "pnl_pct": round(pnl * 100, 2),
            "reason": reason,
            "ts": datetime.now(MEZ).isoformat(),
        }
        pf["trades"].append(trade)

        emoji = "🔴" if pnl < 0 else "🟡"
        msg = (
            f"{emoji} <b>PAPER SELL — {tkr}</b>\n"
            f"   Kurs: {price:.2f} USD · Erlös: {proceeds:,.0f} USD\n"
            f"   P&L: {profit:+,.0f} USD ({pnl*100:+.1f}%)\n"
            f"   Grund: {reason}"
        )
        _telegram(msg)
        print(f"[SELL] {tkr} @ {price:.2f} — {reason} — P&L: {profit:+,.0f}")


# ── Täglicher Status-Report ───────────────────────────────────────────────────
def _daily_report(pf: dict) -> None:
    pf_val  = _portfolio_value(pf)
    total_r = (pf_val - INITIAL_CASH) / INITIAL_CASH * 100
    pnl_map = _open_pnl(pf)

    lines = [
        f"📊 <b>StocksMB Bot — Tagesbericht {date_str()}</b>",
        f"   Portfolio: {pf_val:,.0f} USD ({total_r:+.1f}% ggü. Start)",
        f"   Cash: {pf['cash']:,.0f} USD",
        f"   Positionen: {len(pf['positions'])}/{MAX_POSITIONS}",
    ]
    for tkr, d in pnl_map.items():
        p = d.get("pnl_pct")
        lines.append(f"   {'🟢' if (p or 0) >= 0 else '🔴'} {tkr}: {p:+.1f}%" if p else f"   ⚪ {tkr}: k.A.")
    lines.append(f"\n   Trades gesamt: {len(pf['trades'])}")
    _telegram("\n".join(lines))


def date_str():
    return datetime.now(MEZ).strftime("%d.%m.%Y")


# ── Haupt-Zyklus ──────────────────────────────────────────────────────────────
def run_cycle() -> None:
    if not _is_market_open():
        print(f"[{datetime.now(MEZ).strftime('%H:%M')}] Markt geschlossen — überspringe")
        return

    print(f"[{datetime.now(MEZ).strftime('%H:%M')}] Zyklus startet …")
    pf = _load_portfolio()

    try:
        signals = _api_signals()
        regime  = signals.get("macro", {}).get("regime", "Neutral")
        action  = signals.get("bot_action", "SELECTIVE")

        print(f"  Macro: {regime} | Action: {action}")
        _check_sells(pf, regime)
        if action in ("BUY", "SELECTIVE"):
            _try_buy(pf, signals)

        _save_portfolio(pf)

    except Exception as e:
        print(f"[Fehler] {e}")
        _telegram(f"⚠️ <b>Bot-Fehler:</b> {e}")


# ── Scheduler ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  StocksMB Paper-Trading Bot v1.0")
    print(f"  API: {API_URL}")
    print("=" * 50)

    pf = _load_portfolio()
    _telegram(
        f"🤖 <b>Bot gestartet — {date_str()}</b>\n"
        f"   Startkapital: {pf['cash']:,.0f} USD\n"
        f"   API: {API_URL}\n"
        f"   Strategie: Quality Score ≥ {MIN_QUALITY_SC}, Discount ≥ {MIN_DISCOUNT}%\n"
        f"   Stop-Loss: {STOP_LOSS*100:.0f}% · Take-Profit: {TAKE_PROFIT*100:.0f}%"
    )

    # Alle 15 Minuten während Handelszeit
    schedule.every(15).minutes.do(run_cycle)
    # Täglicher Report um 22:05 MEZ
    schedule.every().day.at("22:05").do(lambda: _daily_report(_load_portfolio()))

    run_cycle()  # sofort einmal starten

    while True:
        schedule.run_pending()
        time.sleep(30)
