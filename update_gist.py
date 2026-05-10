#!/usr/bin/env python3
"""
update_gist.py — Schreibt Daytrading-Picks in ein öffentliches GitHub Gist.

Env-Variablen (in Railway setzen):
  GITHUB_TOKEN  — GitHub PAT mit 'gist'-Scope
  GIST_ID       — ID des bestehenden Gists (leer lassen beim ersten Lauf;
                  das Script gibt dann die neue ID aus → in Railway eintragen)

Railway Cron-Service: python update_gist.py, Schedule: 0 * * * *
"""
import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd
import requests
import yfinance as yf

_DAYTRADING_POOL = [
    "TQQQ", "SQQQ", "UPRO", "SPXU", "QQQ", "SPY", "NVDA", "TSLA", "AMD", "META",
    "AAPL", "MSFT", "AMZN", "GOOGL", "NFLX", "SMCI", "ARM", "PLTR", "COIN", "MSTR",
    "IONQ", "RIVN", "LCID", "SOFI", "HOOD", "GME", "AMC", "BYND", "SPCE", "BBBY",
]


def fetch_picks() -> list:
    results = []
    for tkr in _DAYTRADING_POOL:
        try:
            obj = yf.Ticker(tkr)
            info = obj.info
            hist = obj.history(period="30d")
            if hist.empty or len(hist) < 5:
                continue
            price = float(hist["Close"].iloc[-1])
            if price <= 0:
                continue
            high, low, close = hist["High"], hist["Low"], hist["Close"]
            prev = close.shift(1)
            tr = pd.concat(
                [high - low, (high - prev).abs(), (low - prev).abs()], axis=1
            ).max(axis=1)
            atr_pct = float(tr.tail(14).mean() / price * 100)
            avg_vol = float(hist["Volume"].iloc[:-1].mean()) or 1
            rel_vol = float(hist["Volume"].iloc[-1]) / avg_vol
            name = info.get("shortName", tkr)
            typ = (
                "Leveraged ETF"
                if any(x in name for x in ["3x", "Ultra", "ProShares", "Direxion"])
                else "ETF" if info.get("quoteType") == "ETF"
                else "Aktie"
            )
            results.append({
                "ticker":  tkr,
                "name":    name,
                "price":   round(price, 2),
                "atr_pct": round(atr_pct, 1),
                "rel_vol": round(rel_vol, 2),
                "typ":     typ,
                "score":   round(atr_pct * 0.6 + rel_vol * 0.4, 2),
            })
        except Exception as exc:
            print(f"[SKIP] {tkr}: {exc}", file=sys.stderr)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:15]


def push_to_gist(picks: list) -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("GITHUB_TOKEN nicht gesetzt — abbruch.", file=sys.stderr)
        sys.exit(1)

    gist_id = os.environ.get("GIST_ID", "").strip()

    payload = {
        "updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(picks),
        "picks": picks,
    }
    content = json.dumps(payload, indent=2, ensure_ascii=False)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if gist_id:
        r = requests.patch(
            f"https://api.github.com/gists/{gist_id}",
            headers=headers,
            json={"files": {"daytrading_picks.json": {"content": content}}},
            timeout=15,
        )
    else:
        r = requests.post(
            "https://api.github.com/gists",
            headers=headers,
            json={
                "description": "MB-AktienScreener — Daytrading Picks (stündlich)",
                "public": True,
                "files": {"daytrading_picks.json": {"content": content}},
            },
            timeout=15,
        )

    r.raise_for_status()
    data = r.json()

    if not gist_id:
        gist_id = data["id"]
        raw_url = data["files"]["daytrading_picks.json"]["raw_url"]
        print("=" * 60)
        print(f"Gist erstellt!")
        print(f"  GIST_ID  = {gist_id}")
        print(f"  HTML URL = {data['html_url']}")
        print(f"  RAW URL  = {raw_url}")
        print("Trage GIST_ID als Railway-Umgebungsvariable ein.")
        print("=" * 60)
    else:
        raw_url = data["files"]["daytrading_picks.json"]["raw_url"]
        print(f"Gist aktualisiert → {raw_url}")

    return raw_url


if __name__ == "__main__":
    print(f"[{datetime.now(timezone.utc).strftime('%H:%M UTC')}] Lade Daytrading-Daten …")
    picks = fetch_picks()
    print(f"{len(picks)} Picks berechnet.")
    push_to_gist(picks)
