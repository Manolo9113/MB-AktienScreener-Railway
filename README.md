# 📈 StocksMB — Aktienscreener & Trading System

Professioneller Aktienscreener auf Basis von Python/Streamlit, deployed auf Railway.
Analysiert Aktien nach Qualität, Value, Burggraben und Daytrading-Tauglichkeit.

## Was ist StocksMB?

StocksMB besteht aus drei Komponenten:

| Komponente | Datei | Beschreibung |
|---|---|---|
| **Streamlit App** | `app.py` | Web-Frontend mit Charts, Scores, KI-Analyse |
| **FastAPI** | `api.py` | REST-API für externe Bots und Tools |
| **Trading Bot** | `bot/bot.py` | Paper-Trading Bot mit Dual-Strategie |

---

## Scores erklärt

### ⭐ Quality Score (0–100)
Bewertet die operative Qualität eines Unternehmens.

| Kriterium | Punkte | Gut | OK |
|---|---|---|---|
| Gross Margin | 15 | ≥ 60% | ≥ 40% |
| ROIC | 15 | ≥ 20% | ≥ 10% |
| Revenue Growth | 12 | ≥ 15% | ≥ 5% |
| FCF Yield | 12 | ≥ 5% | ≥ 2% |
| Profit Margin | 10 | ≥ 15% | ≥ 5% |
| Operating Margin | 8 | ≥ 20% | ≥ 10% |
| PEG Ratio | 8 | ≤ 1.5x | ≤ 2.5x |
| Rule of 40 | 20 | ≥ 40 | ≥ 20 |

> Rule of 40 wird nur für SaaS- und Cybersecurity-Unternehmen bewertet.

---

### 💎 Value Score (0–100)
Bewertet klassische Value-Kriterien nach Buffett-Stil.

| Kriterium | Punkte |
|---|---|
| P/E Ratio | 25 |
| FCF Yield | 20 |
| Price/Book | 15 |
| EV/EBITDA | 15 |
| Debt/Equity | 10 |
| Dividend Yield | 10 |
| Revenue Growth | 5 |

---

### 🏰 Moat Score (0–100) → Wide / Narrow / No Moat
Bewertet die Wettbewerbsposition.

| Kriterium | Punkte |
|---|---|
| ROIC | 30 |
| Gross Margin | 30 |
| Operating Margin | 20 |
| Profit Margin | 10 |
| Revenue Growth | 10 |

**Schwellen:** ≥ 65 = Wide Moat 🏰 · 35–64 = Narrow Moat 🛡️ · < 35 = No Moat ⚠️

**Erkannte Moat-Typen:**
- 🌐 Network Effects (Social, Payment, Gaming)
- 🔒 Switching Costs (SaaS, Cloud, ERP)
- 💡 Intangible Assets (Pharma, Luxus, Marken)
- 💰 Cost Advantages (Retail, Logistik)
- ⚖️ Efficient Scale (Utilities, Telekom)
- 💎 Pricing Power (Bruttomarge > 55%)

---

### 🔬 Piotroski F-Score (0–9)
9 binäre Kriterien aus dem Jahresabschluss.

**Profitabilität (4 Punkte)**
1. ROA > 0?
2. Operating Cash Flow > 0?
3. ROA verbessert (YoY)?
4. CFO/TA > ROA? (Earnings Quality)

**Kapitalstruktur (3 Punkte)**
5. Verschuldung gesunken?
6. Current Ratio verbessert?
7. Keine Verwässerung?

**Effizienz (2 Punkte)**
8. Bruttomarge verbessert?
9. Asset Turnover verbessert?

---

### ⚡ Daytrading Score (0–100)
Bewertet Intraday-Handelstauglichkeit.

| Kriterium | Punkte |
|---|---|
| Ø Tagesvolumen | 30 |
| ATR% (Tagesspanne) | 25 |
| Beta | 20 |
| Kursrange ($20–300) | 15 |
| Marktkapitalisierung | 10 |

---

## DCF Fair Value
10-Jahres-Projektion des Free Cash Flow + Terminal Value (Gordon Growth Model).

```
FV = Σ FCF_t / (1+r)^t  +  FCF_10 × (1+g) / (r−g) / Aktienanzahl
```

| Parameter | Standard | Slider |
|---|---|---|
| Wachstumsrate | Revenue Growth | 0–50% |
| Terminal Growth | 2% | 1–5% |
| Diskontierungsrate (WACC) | 10% | 5–15% |
| Projektionsjahre | 10 | 5–15 |

---

## Technische Indikatoren

| Indikator | Periode | Quelle | Bedeutung |
|---|---|---|---|
| **RSI** | 14 Tage | Kurshistorie | > 70 überkauft, < 30 überverkauft |
| **MACD** | 12/26/9 EMA | Kurshistorie | Crossover = Trendwechsel-Signal |
| **EMA** | 20/50/100/200 | Kurshistorie | Trendrichtung + % Abstand |
| **Fibonacci** | 7 Levels | 52W High/Low | Unterstützungs-/Widerstandszonen |
| **ATR%** | 14 Tage | High/Low/Close | Ø tägliche Bewegung in % |
| **Rel. Volumen** | Heute vs Ø | Volumen | > 1.5× = erhöhte Aktivität |
| **Beta** | — | yfinance | Volatilität vs. S&P 500 |
| **52W-Position** | — | 52W H/L | (Kurs−Tief)/(Hoch−Tief) in % |

---

## Screening-Listen

### Quality Watchlist (~50 Titel)
Verwendet für Haupt-Screener und Top-Picks.

```
Tech:       AAPL, MSFT, GOOGL, META, AMZN, NVDA, AVGO, CRM, ADBE, NOW,
            INTU, PANW, DDOG, MDB, TSM, ASML, AMAT, AMD
Finance:    BRK-B, JPM, V, MA, AXP, SPGI, MCO
Healthcare: LLY, NVO, UNH, TMO, ISRG, ABT
Consumer:   COST, MCD, NKE, BKNG, CMG
Industrial: CAT, HON, LIN, ETN
Staples:    JNJ, PG, KO, WMT, HD
Other:      MSCI, MELI, CPRT, FICO, ROP
```

**Aufnahmekriterien:** Score ≥ 65 + Kurs ≥ 5% unter Fair Value

---

### Value Watchlist (~55 Titel, API)
Klassische Value-Aktien nach Buffett-Kriterien.

```
Financials:  BRK-B, JPM, BAC, C, WFC, GS, MS, USB, TFC
Energie:     XOM, CVX, COP, EOG, PSX, VLO, MPC, OXY
Healthcare:  JNJ, PFE, ABBV, MRK, BMY, GILD, CVS, CI
Staples:     KO, PEP, PG, WMT, TGT, CL, GIS, MO, PM
Industrie:   GE, CAT, HON, MMM, EMR, RTX, LMT, NOC
Telecom:     T, VZ, CMCSA, DIS, WBD, F, GM, STLA
Utilities:   NEE, DUK, SO, D, AEP
REITs:       SPG, O, VTR, PLD, AMT
Tech Value:  INTC, CSCO, IBM, QCOM, TXN, HPQ
```

---

### Tradeable Watchlist (~35 Titel, API)
Gut handelbare Aktien mit hohem Volumen.

```
Mega-Cap:   AAPL, MSFT, NVDA, AMD, AMZN, GOOGL, META, TSLA
Finance:    BAC, C, JPM, WFC, GS
Growth:     PLTR, COIN, SOFI, HOOD, RIVN, NIO
ETFs:       SPY, QQQ, IWM, XLF, XLE, XLK, GLD
```

---

### Daytrading Watchlist (~40 Titel, API)
Hohe Volatilität und Liquidität für Intraday-Trading.

```
Leveraged:  TQQQ, SQQQ, SPXL, SPXU, UPRO, TNA, TZA, LABU, LABD, UVXY
Proxies:    SPY, QQQ, IWM
Volatile:   TSLA, NVDA, AMD, META, AMZN, MSTR, COIN, PLTR, SOFI, HOOD
ETFs:       ARKK, XBI, GDX, KWEB, IBIT
```

> ⚠️ Leveraged ETFs nur für erfahrene Trader — täglicher Wertverlust durch Rebalancing möglich.

---

## Datenpunkte pro Aktie

| Kategorie | Felder |
|---|---|
| **Kurs** | Aktuell, 52W High/Low, tägl. Änderung |
| **Bewertung** | P/E, Forward P/E, P/B, EV/EBITDA, PEG |
| **Cashflow** | FCF, FCF Yield, FCF Margin, Price/FCF |
| **Rentabilität** | ROE, ROIC, Gross/Op./Profit Margin |
| **Wachstum** | Revenue Growth, Earnings Growth, EPS |
| **Bilanz** | Debt/Equity, Net Cash/Share, Current Ratio |
| **Dividende** | Yield, Payout Ratio, Consecutive Years |
| **Analysten** | Kursziel, Upside, Consensus, # Analysten |
| **Prognose** | Forward EPS, EPS-Schätzungen, Revenue-Schätzungen |

---

## API-Dokumentation

Alle Endpoints außer `/` und `/health` erfordern den Header `X-API-Key` wenn `STOCKSMB_API_KEY` gesetzt ist.

### Endpoints

#### `GET /`
Health-Check. Öffentlich.
```json
{"app": "StocksMB API", "version": "1.1.0", "status": "online"}
```

#### `GET /score/{ticker}`
Alle Scores + Fair Value für einen Ticker.
```bash
curl -H "X-API-Key: deinkey" https://deine-api.railway.app/score/AAPL
```
```json
{
  "ticker": "AAPL",
  "price": 213.49,
  "scores": {
    "quality": 82,
    "value": 54,
    "tradeable": 91,
    "daytrading": 78,
    "composite": 72.3
  },
  "daytrading_detail": {
    "volumen": {"wert": 55.2, "einheit": "M/Tag", "label": "Extrem hoch"},
    "atr_pct": {"wert": 1.8, "einheit": "%"},
    "beta": {"wert": 1.24}
  },
  "fair_value": 198.50,
  "discount_pct": -7.5
}
```

#### `GET /screener/quality?top_n=5&min_score=65`
Top-Qualitätsaktien unter Fair Value.

| Parameter | Standard | Beschreibung |
|---|---|---|
| `top_n` | 5 | Anzahl Ergebnisse (1–20) |
| `min_score` | 65 | Mindest-Quality-Score |

#### `GET /screener/value?top_n=10&min_score=55`
Value-Picks nach P/E, FCF, Dividende.

#### `GET /screener/tradeable?top_n=15`
Liquideste, gut handelbare Aktien.

#### `GET /screener/daytrading?min_atr_pct=2.5&min_score=60&top_n=10`
Daytrading-Kandidaten nach ATR% und Volumen.

| Parameter | Standard | Beschreibung |
|---|---|---|
| `top_n` | 15 | Anzahl Ergebnisse |
| `min_score` | 50 | Mindest-DT-Score |
| `min_atr_pct` | 1.5 | Mindest-ATR% |
| `min_volume_m` | 5.0 | Mindest-Volumen Mio/Tag |

#### `GET /signals?top_n=5`
Makro-Regime + Top-Picks für den Trading-Bot.
```json
{
  "macro": {
    "regime": "Risk-On",
    "note": "Zinskurve normal (+0.42%)",
    "hy_signal": "OK"
  },
  "bot_action": "BUY",
  "quality_picks": [...],
  "value_picks": [...]
}
```

**Makro-Regime-Logik:**
- T10Y2Y > 0.5% → Risk-On
- T10Y2Y −0.2% bis 0.5% → Neutral
- T10Y2Y < −0.2% → Risk-Off
- HY-Spread > 600bp → überschreibt zu Risk-Off

---

## Trading Bot

### Dual-Strategie

```
┌─────────────────────────────────────────────────────┐
│  DAYTRADING (3 Slots)     │  QUALITY/SWING (2 Slots)│
│  ─────────────────────    │  ──────────────────────  │
│  Quelle: /screener/dt     │  Quelle: /signals        │
│  Score ≥ 60               │  Score ≥ 70              │
│  ATR% ≥ 2.5%              │  Discount ≥ 6%           │
│  Position: 15%            │  Position: 20%           │
│  Stop-Loss: −3%           │  Stop-Loss: −5%          │
│  Take-Profit: +8%         │  Take-Profit: +15%       │
│  Poll: alle 5 Min         │  Poll: alle 15 Min       │
│  Close: 21:45 MEZ         │  Close: bei Risk-Off     │
└─────────────────────────────────────────────────────┘
```

### Telegram Notifications
Jeder Trade löst eine Nachricht aus:
```
⚡ PAPER BUY [DT] — TSLA
   Kurs: 248.30 USD · 60 Stk · 14.898 USD
   DT-Score: 78/100 · ATR: 3.2%
   SL: −3% · TP: +8%
```

### Tagesbericht (22:05 MEZ)
```
📊 StocksMB Bot v2 — Tagesbericht 24.04.2026
   Portfolio: 102.340 USD (+2.3% ggü. Start)
   ⚡ DT-Slots: 0/3 · Realisiert: +1.840 USD (4 Trades)
   💎 Quality-Slots: 2/2 · Realisiert: +0 USD (0 Trades)
   💎 🟢 AAPL: +3.2%
   💎 🟢 MSFT: +1.8%
```
