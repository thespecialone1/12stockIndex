#!/usr/bin/env python3
"""Screen the universe to a ~35-name shortlist using key stats."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

ks = json.load(open(os.path.join(DATA, "key_stats.json")))

EXCLUDE_SECTORS = {
    "CLOSE - END MUTUAL FUND", "MODARABAS", "MODARABA", "EXCHANGE TRADED FUNDS",
    "REAL ESTATE INVESTMENT TRUST", "LEASING COMPANIES", "CLOSE - END MUTUAL FUNDS",
}

def f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

rows = []
for sym, r in ks.items():
    sec = (r.get("sector_name") or "").upper()
    mcap = f(r.get("stat_Market cap"))
    eps = f(r.get("stat_Earnings Per Share"))
    pe = f(r.get("stat_Price to Earnings"))
    pb = f(r.get("stat_Price to Book Value"))
    dy = f(r.get("stat_Dividend Yield (%)"))
    nim = f(r.get("stat_Net Income Margin (%)"))
    peg = f(r.get("stat_PEG Ratio"))
    close = f(r.get("close"))
    hi52 = f(r.get("stat_52 week high price"))
    lo52 = f(r.get("stat_52 week low price"))
    ff = f(r.get("stat_Free Float %"))
    if not mcap or mcap < 25e9: continue
    if sec in EXCLUDE_SECTORS: continue
    if eps is None or eps <= 0: continue
    if close is None or close <= 0: continue
    if pe is None or not (1.5 < pe < 40): continue
    if ff is not None and ff < 10: continue
    off_high = None
    if hi52 and close:
        off_high = (close / hi52 - 1) * 100
    rows.append(dict(symbol=sym, name=r.get("name",""), sector=r.get("sector_name",""),
                     close=close, mcap=mcap, eps=eps, pe=pe, pb=pb, dy=dy, nim=nim,
                     peg=peg, off_high=off_high, ff=ff,
                     chg_d=r.get("change_pct"), listed=r.get("listed_in","")))

print(f"passed screen: {len(rows)}")

# composite value score
def pct_rank(vals, higher_better=True, low_good=None):
    """rank among non-None values; returns 0..1"""
    import statistics
    xs = [v for v in vals if v is not None]
    if not xs: return {}
    if higher_better:
        order = sorted(xs)
    else:
        order = sorted(xs, reverse=True)
    n = len(order)
    return {v: (order.index(v) + 1) / n for v in set(order)}

pe_rank = pct_rank([r["pe"] for r in rows], higher_better=False)   # lower P/E better
dy_rank = pct_rank([r["dy"] for r in rows], higher_better=True)
nim_rank = pct_rank([r["nim"] for r in rows], higher_better=True)
mcap_rank = pct_rank([r["mcap"] for r in rows], higher_better=True)
off_rank = pct_rank([r["off_high"] for r in rows], higher_better=True)  # less below 52w high = stronger

for r in rows:
    score = 0.0
    if r["pe"] is not None: score += 0.35 * pe_rank[r["pe"]]
    if r["dy"] is not None: score += 0.20 * dy_rank[r["dy"]]
    if r["nim"] is not None: score += 0.20 * nim_rank[r["nim"]]
    score += 0.10 * mcap_rank[r["mcap"]]
    if r["off_high"] is not None: score += 0.15 * off_rank[r["off_high"]]
    r["score"] = round(score, 3)

rows.sort(key=lambda r: -r["score"])
for r in rows[:45]:
    print(f"{r['score']:.3f} {r['symbol']:9s} {r['sector'][:34]:34s} P/E {r['pe']:6.2f} DY {r['dy'] or 0:5.2f} MCap {r['mcap']/1e9:8.0f}B off52H {r['off_high']:6.1f}% NIM {r['nim'] or 0:5.1f}")

# shortlist: top ~35 but cap sector at 6 to keep breadth
from collections import defaultdict
cnt = defaultdict(int)
short = []
for r in rows:
    sec = r["sector"]
    if cnt[sec] >= 6: continue
    short.append(r["symbol"])
    cnt[sec] += 1
    if len(short) >= 35: break
print("\nSHORTLIST:", ", ".join(short))
open(os.path.join(BASE, "shortlist.txt"), "w").write("\n".join(short) + "\n")
json.dump(rows, open(os.path.join(DATA, "screened.json"), "w"), indent=1)
