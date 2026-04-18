#!/usr/bin/env python3
"""
StocksMB Daily Screener
Läuft als GitHub Action (Mo–Fr, 7:00 MEZ).
Berechnet Score + Fair Value für ~80 Qualitätsaktien,
filtert günstig bewertete und sendet Top-5 via Telegram.
"""
import os
import sys
import time
import requests
import yfinance as yf
import pandas as pd
from datetime import date

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ── Kuratierte Qualitäts-Watchlist (~80 Titel) ───────────────────────────────
WATCHLIST = [
    # US Tech / Software
    "AAPL", "MSFT", "GOOGL", "META", "AMZN", "NVDA", "AVGO",
    "CRM", "ADBE", "NOW", "INTU", "PANW", "DDOG", "MDB", "SNOW",
    # Halbleiter
    "TSM", "ASML", "AMAT", "LRCX", "KLAC", "AMD", "MRVL",
    # Finanzials
    "BRK-B", "JPM", "V", "MA", "AXP", "SPGI", "MCO", "ICE",
    # Healthcare / Pharma
    "LLY", "NVO", "UNH", "TMO", "DHR", "ISRG", "ABT", "ABBV",
    # Consumer / Retail
    "COST", "MCD", "SBUX", "NKE", "LVMUY", "BKNG", "CMG",
    # Industrial / Infrastruktur
    "CAT", "DE", "HON", "LIN", "ETN", "ITW",
    # Energie / Utilities
    "XOM", "NEE", "WMB",
    # EU / Global
    "SAP", "ASML", "IDEXY",   # SAP, ASML (US ADR), Hermès ADR
    # Dividenden / Value
    "JNJ", "PG", "KO", "PEP", "WMT", "HD",
    # Quality Compounder
    "MSCI", "MELI", "CPRT", "ODFL", "WST", "ROP", "FICO",
]


# ── Telegram ─────────────────────────────────────────────────────────────────
def send_telegram(msg: str) -> None:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️  TELEGRAM_BOT_TOKEN oder TELEGRAM_CHAT_ID fehlt.")
        print(msg)
        return
    resp = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
        timeout=15,
    )
    if not resp.ok:
        print(f"Telegram-Fehler: {resp.text}")


# ── Score-Berechnung (0–100) ──────────────────────────────────────────────────
def calc_score(info: dict) -> int:
    score = 0

    # Umsatzwachstum (trailing YoY)
    rg = info.get("revenueGrowth") or 0
    if rg > 0.20:   score += 20
    elif rg > 0.10: score += 12
    elif rg > 0.03: score += 6

    # Bruttomarge
    gm = info.get("grossMargins") or 0
    if gm > 0.60:   score += 20
    elif gm > 0.40: score += 12
    elif gm > 0.25: score += 6

    # Operative Marge
    om = info.get("operatingMargins") or 0
    if om > 0.25:   score += 15
    elif om > 0.15: score += 9
    elif om > 0.05: score += 4

    # FCF Yield
    fcf = info.get("freeCashflow") or 0
    mkt = info.get("marketCap") or 1
    fcy = fcf / mkt if mkt else 0
    if fcy > 0.05:  score += 15
    elif fcy > 0.02: score += 8
    elif fcy > 0:   score += 4

    # Return on Equity
    roe = info.get("returnOnEquity") or 0
    if roe > 0.25:  score += 15
    elif roe > 0.15: score += 9
    elif roe > 0.08: score += 4

    # Verschuldung (Debt/Equity)
    de = info.get("debtToEquity") or 0
    if de < 30:     score += 10
    elif de < 80:   score += 5

    # Positives EPS
    if (info.get("trailingEps") or 0) > 0:
        score += 5

    return min(score, 100)


# ── Fair-Value-Schätzung ──────────────────────────────────────────────────────
def calc_fair_value(info: dict) -> float | None:
    eps     = info.get("trailingEps") or 0
    rg_pct  = (info.get("revenueGrowth") or 0) * 100   # in %
    fcf     = info.get("freeCashflow") or 0
    shares  = info.get("sharesOutstanding") or 0

    # Graham-Formel: FV = EPS × (8.5 + 2 × Wachstum%)
    graham = None
    if eps > 0 and 0 < rg_pct <= 50:
        graham = eps * (8.5 + 2 * rg_pct)

    # FCF-Methode: 20× FCF pro Aktie (konservatives KGV-Äquivalent)
    fcf_fv = None
    if fcf > 0 and shares > 0:
        fcf_fv = (fcf * 20) / shares

    if graham and fcf_fv:
        return round((graham * 0.4 + fcf_fv * 0.6), 2)   # FCF stärker gewichtet
    return round(graham or fcf_fv, 2) if (graham or fcf_fv) else None


# ── Screener ──────────────────────────────────────────────────────────────────
def screen() -> list[dict]:
    results = []
    total = len(WATCHLIST)

    for i, tkr in enumerate(WATCHLIST, 1):
        print(f"[{i}/{total}] {tkr}", end=" ", flush=True)
        try:
            info  = yf.Ticker(tkr).info
            price = info.get("currentPrice") or info.get("regularMarketPrice")
            if not price:
                print("– kein Preis")
                time.sleep(1)
                continue

            score = calc_score(info)
            fv    = calc_fair_value(info)

            print(f"Score={score}  FV={fv}  Kurs={price:.2f}")

            # Filter: guter Score UND mindestens 8 % unter Fair Value
            if score >= 65 and fv and price < fv * 0.92:
                discount = (fv - price) / fv * 100
                results.append({
                    "ticker":   tkr,
                    "name":     info.get("shortName", tkr)[:28],
                    "price":    price,
                    "fv":       fv,
                    "discount": discount,
                    "score":    score,
                    "currency": info.get("currency", "USD"),
                })
        except Exception as e:
            print(f"Fehler: {e}")

        time.sleep(1.5)   # rate-limit-freundlich

    # Sortierung: Score × Discount (beste Kombi oben)
    results.sort(key=lambda x: x["score"] * x["discount"], reverse=True)
    return results[:5]


# ── Nachricht zusammenbauen ───────────────────────────────────────────────────
def build_message(picks: list[dict]) -> str:
    today = date.today().strftime("%d. %b %Y")
    header = f"📊 <b>StocksMB Screener — {today}</b>\n"

    if not picks:
        return (
            header
            + "\nHeute keine Aktien mit Score ≥ 65 gefunden,\n"
            + "die ≥ 8 % unter ihrem geschätzten Fair Value handeln."
        )

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    lines  = [header, "🟢 <b>Günstig unter Fair Value (Score ≥ 65):</b>\n"]
    for idx, p in enumerate(picks):
        cur = p["currency"]
        lines.append(
            f"{medals[idx]} <b>{p['ticker']}</b> – {p['name']}\n"
            f"   Score {p['score']}/100  ·  "
            f"Kurs {p['price']:.2f} {cur}  ·  "
            f"FV ~{p['fv']:.2f}  ·  "
            f"Discount <b>-{p['discount']:.1f}%</b>\n"
        )

    lines.append(
        "\n⚠️ <i>Automatische Berechnung auf Basis öffentlicher Daten.\n"
        "Kein Anlageberatung — eigene Recherche empfohlen.</i>"
    )
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== StocksMB Daily Screener ===")
    picks   = screen()
    message = build_message(picks)
    print("\n--- Telegram-Nachricht ---")
    print(message)
    send_telegram(message)
    print("\nFertig.")
    sys.exit(0)
