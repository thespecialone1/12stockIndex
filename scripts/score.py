#!/usr/bin/env python3
"""Score the deep shortlist and produce the final 12-stock portfolio with analysis."""
import json, os, math
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

ks = json.load(open(os.path.join(DATA, "key_stats.json")))
deep = json.load(open(os.path.join(DATA, "deep_data.json")))
kse100 = json.load(open(os.path.join(DATA, "kse100_history.json")))

def f(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def fnum(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default

def pct_rank(vals, higher_better=True):
    xs = [(i, v) for i, v in enumerate(vals) if v is not None]
    if not xs:
        return {i: 0.5 for i in range(len(vals))}
    order = sorted(xs, key=lambda t: t[1], reverse=not higher_better)
    ranks = {}
    for pos, (i, v) in enumerate(order):
        ranks[i] = (pos + 1) / len(order)
    return ranks

rows = []
for sym, dd in deep.items():
    k = ks.get(sym, {})
    r = {"symbol": sym, "name": k.get("name", ""), "sector": k.get("sector_name", ""),
         "pe": f(k.get("stat_Price to Earnings")), "pb": f(k.get("stat_Price to Book Value")),
         "dy": f(k.get("stat_Dividend Yield (%)")), "eps": f(k.get("stat_Earnings Per Share")),
         "mcap": f(k.get("stat_Market cap")), "peg": f(k.get("stat_PEG Ratio")),
         "close": f(k.get("close")), "hi52": f(k.get("stat_52 week high price")),
         "lo52": f(k.get("stat_52 week low price")), "nim": f(k.get("stat_Net Income Margin (%)")),
         "ttm_eps": None, "eps_yoy": None, "eps_latest_q": None, "eps_q_yoy": None,
         "rev_latest": None, "rev_q_yoy": None, "ret_1y": None, "ret_6m": None, "ret_3m": None,
         "vol": None, "off_peak": None, "off_52h": None, "dps_growth_2y": None, "dps_consistency": None}

    # quarterly EPS -> TTM + YoY growth
    eps_q = sorted([(d[:10], fnum(v)) for d, v in dd.get("q_Basic EPS", []) if fnum(v) is not None])
    if len(eps_q) >= 8:
        ttm = sum(v for _, v in eps_q[-4:])
        prev_ttm = sum(v for _, v in eps_q[-8:-4])
        r["ttm_eps"] = round(ttm, 2)
        r["eps_yoy"] = round((ttm / prev_ttm - 1) * 100, 1) if prev_ttm else None
        r["eps_latest_q"] = eps_q[-1][1]
        r["eps_q_yoy"] = round((eps_q[-1][1] / eps_q[-5][1] - 1) * 100, 1) if eps_q[-5][1] else None
        # revenue latest quarter YoY
        rev_q = sorted([(d[:10], fnum(v)) for d, v in dd.get("q_Revenue", []) if fnum(v) is not None and fnum(v) > 0])
        if len(rev_q) >= 2:
            r["rev_latest"] = rev_q[-1][1]
            if len(rev_q) >= 5:
                r["rev_q_yoy"] = round((rev_q[-1][1] / rev_q[-5][1] - 1) * 100, 1)
    else:
        r["ttm_eps"] = r["eps"]

    # ratios latest year (pick most recent year with data)
    ratios = dd.get("ratios", {})
    def ratio(key):
        years = ratios.get(key, {})
        if not years:
            return None
        yr = max(years.keys())
        v = years[yr]
        return v if v not in (5.39, 5.390) else None
    roe_a = ratio("Return on Average Total Capital (%)")
    roe_b = ratio("Return on Average Invested Capital (%)")
    roe_raw = None
    for cand in (roe_a, roe_b):
        if cand is not None and 0 <= cand <= 60:
            roe_raw = max(roe_raw or 0, cand)
    r["roe"] = roe_raw
    r["roe_implied"] = round((r["pb"] / r["pe"]) * 100, 1) if (r["pb"] and r["pe"]) else None
    r["roa"] = ratio("Return on Average Assets (%)")
    r["de"] = ratio("Debt to Equity (%)")
    r["cur"] = ratio("Current Ratio (x)")
    r["icov"] = ratio("Interest Coverage (x)")
    r["opm"] = ratio("Operating Margin (x)")
    r["ebitda_m"] = ratio("EBITDA Margin (%)")
    r["payout"] = ratio("Dividend Payout Ratio")
    r["fcfps"] = ratio("Free Cash Flow Per Share")
    r["ev_ebitda"] = ratio("Enterprise Value to EBITDA (x)")
    r["eps_yoy_ratio"] = ratio("EPS Basic YoY Growth (%)")
    r["dps_yoy_ratio"] = ratio("DPS YoY Growth (%)")

    # dividends history
    div = dd.get("dividends", {}).get("dividendsPerShare") or []
    dps_hist = {}
    for entry in div:
        for yr, v in entry.items():
            vv = fnum(v)
            if vv is not None:
                dps_hist[int(yr)] = vv
    r["dps_hist"] = dps_hist
    yrs = sorted(dps_hist.keys())
    if len(yrs) >= 4:
        recent = sum(dps_hist[y] for y in yrs[-2:])
        older = sum(dps_hist[y] for y in yrs[-4:-2])
        r["dps_growth_2y"] = round((recent / older - 1) * 100, 1) if older else None
        r["dps_consistency"] = sum(1 for y in yrs if dps_hist[y] > 0) / len(yrs)

    # price history -> returns (anchor from last date; fallback to earliest point)
    ph = sorted(dd.get("price_history", []), key=lambda x: x["date"])
    if len(ph) > 30:
        import datetime
        def ret_from(n_days):
            last_d = datetime.date.fromisoformat(ph[-1]["date"][:10])
            d0 = last_d - datetime.timedelta(days=n_days)
            cands = [p for p in ph if p["date"][:10] <= str(d0)]
            base = cands[-1]["price"] if cands else ph[0]["price"]
            last = ph[-1]["price"]
            return (last / base - 1) * 100
        r["ret_1y"] = round(ret_from(365), 1)
        r["ret_6m"] = round(ret_from(183), 1)
        r["ret_3m"] = round(ret_from(92), 1)
        px = [p["price"] for p in ph]
        r["vol"] = None
        if len(px) > 30:
            import statistics
            rets = [math.log(px[i] / px[i-1]) for i in range(1, len(px)) if px[i-1] > 0]
            r["vol"] = round(statistics.stdev(rets) * math.sqrt(252) * 100, 1) if len(rets) > 10 else None
        peak = max(px)
        r["off_peak"] = round((px[-1] / peak - 1) * 100, 1)

    if r.get("close") and r.get("hi52"):
        r["off_52h"] = round((r["close"] / r["hi52"] - 1) * 100, 1)

    # winsorize outliers before ranking
    def clip(v, lo, hi):
        return max(lo, min(hi, v)) if v is not None else None
    r["eps_yoy_c"] = clip(r["eps_yoy"], -100, 200)
    r["nim_c"] = clip(r["nim"], -20, 80)
    r["dpsg_c"] = clip(r["dps_growth_2y"], -100, 300)
    r["roe_c"] = clip(r["roe"] if r["roe"] is not None else r["roe_implied"], 0, 60)
    rows.append(r)

print(f"deep rows: {len(rows)}")

# factor ranks (use winsorized variants)
idx = list(range(len(rows)))
pe_r = pct_rank([x["pe"] for x in rows], higher_better=False)
dy_r = pct_rank([x["dy"] for x in rows], higher_better=True)
roe_r = pct_rank([x["roe_c"] for x in rows], higher_better=True)
nim_r = pct_rank([x["nim_c"] for x in rows], higher_better=True)
epsg_r = pct_rank([x["eps_yoy_c"] for x in rows], higher_better=True)
r1y_r = pct_rank([x["ret_1y"] for x in rows], higher_better=True)
offh_r = pct_rank([x["off_52h"] for x in rows], higher_better=True)
dpsg_r = pct_rank([x["dpsg_c"] for x in rows], higher_better=True)
mcap_r = pct_rank([x["mcap"] for x in rows], higher_better=True)

EXCLUDE = {"TRG", "SEARL", "KTML", "SNGP", "NPL", "PRL"}
for i, r in enumerate(rows):
    def g(rank_map):
        return rank_map.get(i, 0.5)
    score = (0.14 * g(pe_r) + 0.10 * g(dy_r) + 0.16 * g(roe_r) + 0.12 * g(nim_r)
             + 0.12 * g(epsg_r) + 0.12 * g(r1y_r) + 0.10 * g(offh_r)
             + 0.08 * g(dpsg_r) + 0.06 * g(mcap_r))
    r["score"] = round(score, 3)
    if r["symbol"] in EXCLUDE:
        r["score"] = -1
        r["excluded"] = True

rows.sort(key=lambda r: -r["score"])
print(f"\n{'score':>6} {'sym':8s} {'sector':34s} {'P/E':>6} {'DY':>5} {'ROE':>6} {'NIM':>5} {'EPSg':>7} {'1y%':>7} {'off52h':>7} {'DPSg':>7}")
for r in rows:
    print(f"{r['score']:6.3f} {r['symbol']:8s} {r['sector'][:34]:34s} {r['pe'] or 0:6.2f} {r['dy'] or 0:5.2f} {r['roe_c'] or 0:6.1f} {r['nim_c'] or 0:5.1f} {r['eps_yoy_c'] or 0:7.1f} {r['ret_1y'] or 0:7.1f} {r['off_52h'] or 0:7.1f} {r['dpsg_c'] or 0:7.1f}")

json.dump(rows, open(os.path.join(DATA, "scored.json"), "w"), indent=1)
print("\nSaved scored.json")
