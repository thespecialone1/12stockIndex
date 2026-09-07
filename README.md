# 12stockIndex

**Twelve PSX stocks. One job: beat the KSE-100.**

An equal-weight, 12-stock Pakistan Stock Exchange portfolio — built by scraping all 495 listed companies, screening for liquidity and quality, scoring 54 finalists on value/quality/momentum/income, capping each sector at two names, and overlaying the latest macro research.

## The 12 (equal weight, 8.33% each)

| Sector | Holdings |
|---|---|
| E&P | OGDC, POL |
| Banks | UBL, MEBL |
| Fertilizer | FATIMA, FFC |
| Foods & Personal Care | COLG, FCEPL |
| Power | HUBC |
| Cement | LUCK |
| Tech | SYS |
| Pharma | AGP |

**Book stats (Sep 7, 2026 close):** harmonized P/E 8.5x · ROE 23.9% · dividend yield 5.9% · TTM EPS growth +29.3%.
**Price-only backtest vs KSE-100:** +1.7pp alpha (3M) · +6.1pp (6M) · +1.2pp (12M).

## Viewing the report

Open [`report/index.html`](report/index.html) in a browser — it's fully self-contained (no build step, no server needed).

## Repository structure

- `report/` — the generated report (`index.html`) and the Checklist Design audit (`AUDIT.md`)
- `scripts/` — the reproducible research pipeline:
  1. `collect_key_stats.py` — pulls prices, P/E, EPS, yields, market caps for every listed symbol
  2. `screen.py` — liquidity/quality screen (495 → 81)
  3. `collect_deep.py` — quarterly income statements, ratios, dividends, 1-year price history for finalists
  4. `score.py` — five-factor composite scoring
  5. `finalize.py` — portfolio construction, sector caps, backtest vs KSE-100
  6. `build_report.py` — injects data into the HTML template
- `data/` — collected datasets (universe, key stats, deep fundamentals, scores, final `portfolio.json`)

**Running the pipeline:** the collection scripts read the data-feed host from the `MARKET_API_BASE` environment variable (see `scripts/.env.example`) — set it, then run the six scripts in order.

## Roadmap

**Daily-habit layer (why users come back every day):**
1. **Live tape** — intraday portfolio value vs KSE-100, updated every few minutes, with a "beat the market today?" badge that flips green/red.
2. **Close-of-day digest** — one message at market close: portfolio ±x% vs index ±y%, top mover, tomorrow's earnings/dividend dates. Email + WhatsApp.
3. **Streaks** — "N trading days beating the index" counter with milestones — the core retention loop.
4. **Alerts** — earnings dates, dividend announcements, 52-week breakouts, rebalance reminders. Push + email.
5. **Own-book tracker** — let users log real trades and see their book vs 12stockIndex vs KSE-100; a small leaderboard.
6. **Daily "why it moved"** — one auto-generated paragraph linking each mover to the day's news.

**Platform layer:**
7. **PWA** — installable, offline-cached, push notifications.
8. **Nightly refresh pipeline** — a scheduled job that re-scrapes fundamentals each trading day and re-renders the report, so the page is never stale.
9. **Deeper backtest** — dividends + quarterly rebalancing included, drawdowns, volatility, Sharpe, rolling 1-year windows.
10. **Sector rotation view** — intraday heatmap of the 12 names plus sector momentum ranking.

**Data discipline:** data compiled from public Pakistan market feeds. This is research, not investment advice.
