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
