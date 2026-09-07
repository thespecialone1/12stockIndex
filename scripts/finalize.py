#!/usr/bin/env python3
"""Finalize the 12stockIndex portfolio: picks, weights, stats, backtest curve vs KSE100."""
import json, os, datetime, statistics

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

scored = {r["symbol"]: r for r in json.load(open(os.path.join(DATA, "scored.json")))}
deep = json.load(open(os.path.join(DATA, "deep_data.json")))
listing = json.load(open(os.path.join(DATA, "market_listing.json")))
names = {r["symbol"]: r.get("name", "") for r in listing}
kse100_raw = json.load(open(os.path.join(DATA, "kse100_history.json")))
kse100 = sorted([{"date": d, "price": v} for d, v in kse100_raw], key=lambda x: x["date"])

PICKS = ["OGDC", "POL", "UBL", "MEBL", "FATIMA", "FFC", "HUBC", "LUCK", "SYS", "AGP", "COLG", "FCEPL"]

THESIS = {
    "OGDC": "Pakistan's largest E&P; purest leverage to $95–100+ Brent at ~5.7x earnings with an 8–12% yield floor. Any progress on gas circular-debt realisation (Rs3.4tr) is a direct re-rating catalyst.",
    "POL": "Oil-heavy, privately managed, zero net debt. Trades 4.7% off its 52-week high with a ~13.7% trailing yield while EPS is recovering +47% YoY — the market is paying you to own the oil story.",
    "UBL": "The biggest bank earner on PSX (+31% YoY in 2Q26). 7.1x earnings, 7.5% yield, EPS +37% TTM. Direct beneficiary of the FY27 super-tax cut (10%→8%) and of foreign flows returning to banks.",
    "MEBL": "Premium Islamic franchise with best-in-class CASA and the sector's strongest tape: +44% over 12 months, only 6.6% off its high. Rate normalisation and Islamic-branch expansion keep ROE ~23%.",
    "FATIMA": "Highest-quality fertiliser compounder: 27% ROE, +21.6% 1-year, EPS +15% and a 6.2% yield. New capacity and NPK/export mix diversify it away from pure urea-pricing risk.",
    "FFC": "The fertiliser sector leader (2.5Mt urea + FFBL DAP) at 8.9x with a 7.5% yield and 50% dividend growth. A defensive cash machine — hold through the expected ~20% sector earnings dip, get paid to wait.",
    "HUBC": "Largest IPP with its revised, locked-in PPA. 5.4x earnings, ~9.7% yield and a 69.8% margin. Circular-debt clearance is the catalyst that could re-rate it 15–25%; the yield pays meanwhile.",
    "LUCK": "Lowest-cost cement leader at 15.6Mt with Iraq/DRC diversification. 7.1x earnings, EPS +15.7%. The main levered play on the rate-cut + construction stimulus cycle.",
    "SYS": "Pakistan's flagship IT exporter compounding EPS +26% on record $4.6bn IT exports, with the IT tax exemption extended to 2029. USD revenue hedges the PKR and oil-shock risk in the rest of the book.",
    "AGP": "Pharma's best launch pipeline and export growth at 12.2x — below the sector's 10-year average — with record gross margins from API deflation and price deregulation holding.",
    "COLG": "Defensive staple with ~46% ROE, 26% EBITDA margins and pricing power through the inflation spike. A 5.4% yield anchor that outperforms in risk-off tapes.",
    "FCEPL": "FrieslandCampina's margin-expansion turnaround: revenue +12%, operating profit +54%, gross margin +350bps, EPS +155% and +67% over 12 months — consumer growth at a fair price.",
}

RISKS = {
    "OGDC": "Oil-price reversal or new windfall levies; circular-debt realisation keeps getting pushed.",
    "POL": "Same oil/levy exposure; yield depends on payouts staying elevated.",
    "UBL": "NIM compression as rates eventually fall; ADR tax on low-advance banks.",
    "MEBL": "Premium valuation vs peers; Islamic market share is getting crowded.",
    "FATIMA": "Gas-price hikes and government urea-price pressure hit FY26–27 earnings.",
    "FFC": "Sector profit may fall ~20% on gas/urea policy; dividend growth could pause.",
    "HUBC": "Structural dispatch decline (solar/CTBCM) and cash-conversion risk on receivables.",
    "LUCK": "Coal/oil cost spikes; new capacity in the south keeps pricing competitive.",
    "SYS": "Global IT spend cycle and US visa/immigration policy are outside local control.",
    "AGP": "A reversal of pharma deregulation or a rebound in API costs would squeeze the record margins.",
    "COLG": "18% GST on milk/dairy hits volumes; full valuation limits upside in a rally.",
    "FCEPL": "Rich P/E (~19.7x) — needs the margin story to keep delivering; oil-driven input costs.",
}

# ---- equal weight ----
w = 1.0 / len(PICKS)
port = {"name": "12stockIndex", "as_of": "2026-09-07", "currency": "PKR",
        "benchmark": "KSE-100", "stocks": [], "methodology": {
            "equal_weight": "Each of the 12 stocks starts at an equal 8.33% weight, rebalanced quarterly.",
            "selection": "Quant screen (value 24%, quality 28%, momentum 22%, income 14%, size 12%) over all 495 listed PSX names, then a sector-diversification cap (max 2 per sector) and a macro/qualitative overlay from broker and media research.",
            "objective": "Outperform the KSE-100 over 12–24 months with lower concentration risk than the index's top-heavy banks/energy tilt."}}

for sym in PICKS:
    r = scored[sym]
    d = deep.get(sym, {})
    dps = r.get("dps_hist", {})
    yrs = sorted(dps.keys())
    last_dps = dps.get(yrs[-1]) if yrs else None
    port["stocks"].append({
        "symbol": sym,
        "name": names.get(sym, sym),
        "sector": r["sector"],
        "weight": round(w * 100, 2),
        "price": r["close"],
        "pe": r["pe"], "pb": r["pb"], "dy": r["dy"], "eps": r["ttm_eps"] or r["eps"],
        "roe": r["roe_c"], "eps_yoy": r["eps_yoy_c"],
        "ret_1y": r["ret_1y"], "ret_6m": r["ret_6m"], "ret_3m": r["ret_3m"],
        "off_52h": r["off_52h"], "mcap": r["mcap"],
        "dps": last_dps, "dps_growth_2y": r["dpsg_c"],
        "thesis": THESIS[sym], "risk": RISKS[sym]})

# ---- portfolio-level stats ----
def avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None

def harmonic(xs):
    xs = [x for x in xs if x is not None and x > 0]
    return len(xs) / sum(1 / x for x in xs) if xs else None

pe_p = harmonic([s["pe"] for s in port["stocks"]])
dy_p = avg([s["dy"] for s in port["stocks"]])
roe_p = avg([s["roe"] for s in port["stocks"]])
epsg_p = avg([s["eps_yoy"] for s in port["stocks"]])
r1y = avg([s["ret_1y"] for s in port["stocks"]])
r6m = avg([s["ret_6m"] for s in port["stocks"]])
r3m = avg([s["ret_3m"] for s in port["stocks"]])
port["stats"] = {"pe": round(pe_p, 1), "dy": round(dy_p, 1), "roe": round(roe_p, 1),
                 "eps_growth": round(epsg_p, 1), "ret_1y": round(r1y, 1),
                 "ret_6m": round(r6m, 1), "ret_3m": round(r3m, 1)}

# sector allocation
from collections import defaultdict
sect = defaultdict(float)
for s in port["stocks"]:
    sect[s["sector"]] += s["weight"]
port["sectors"] = {k: round(v, 1) for k, v in sorted(sect.items(), key=lambda kv: -kv[1])}

# ---- normalized backtest curves (price-only) ----
def norm_series(points):
    pts = sorted(points, key=lambda x: x["date"])
    base = pts[0]["price"]
    return [(p["date"][:10], round(p["price"] / base * 100, 2)) for p in pts]

bench = norm_series(kse100)
# portfolio curve = daily average of normalized series
series_map = {}
for s in port["stocks"]:
    series_map[s["symbol"]] = dict(norm_series(deep[s["symbol"]]["price_history"]))
dates = sorted(set().union(*[set(m.keys()) for m in series_map.values()]))
port_curve = []
for dt in dates:
    vals = [m[dt] for m in series_map.values() if dt in m]
    if len(vals) >= len(series_map) * 0.75:
        port_curve.append((dt, round(sum(vals) / len(vals), 2)))
bench_map = dict(bench)
port_curve = [(d, v) for d, v in port_curve if d in bench_map]

port["backtest"] = {
    "note": "Price-only, equal-weight, no dividends, no rebalancing. Understates both the portfolio (its 6.4% average yield beats the index's) and the KSE-100.",
    "kse100": bench,
    "portfolio": port_curve,
    "port_1y_price_ret": round(port_curve[-1][1] - 100, 2) if port_curve else None,
    "kse100_1y_price_ret": round(bench[-1][1] - 100, 2) if bench else None}

json.dump(port, open(os.path.join(DATA, "portfolio.json"), "w"), indent=1)
print("=== 12stockIndex ===")
print("stats:", port["stats"])
print("sectors:", port["sectors"])
print("backtest:", port["backtest"]["port_1y_price_ret"], "vs KSE100", port["backtest"]["kse100_1y_price_ret"])
for s in port["stocks"]:
    print(f"{s['symbol']:7s} w{s['weight']:5.1f}% P/E {s['pe']:5.2f} DY {s['dy']:5.2f} ROE {s['roe']:5.1f} EPSg {s['eps_yoy']:6.1f} 1y {s['ret_1y']:6.1f}% {s['sector'][:30]}")
