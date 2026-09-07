#!/usr/bin/env python3
"""Collect key stats + about (sector) for all currently-listed PSX symbols via the market-data feed API.

Set MARKET_API_BASE to the feed host, e.g. https://feed.example.com/api"""
import json, subprocess, time, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
API_BASE = os.environ.get("MARKET_API_BASE", "").rstrip("/")
if not API_BASE:
    raise SystemExit("Set MARKET_API_BASE env var first")

def curl(url, post=False, retries=3):
    for attempt in range(retries):
        cmd = ["curl", "-s", "-m", "25", "-H", "User-Agent: Mozilla/5.0"]
        if post:
            cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", "{}"]
        cmd.append(url)
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        try:
            return json.loads(out)
        except Exception:
            time.sleep(1.0)
    return None

# universe = currently listed symbols from PSX market-watch
sector_codes = json.load(open(os.path.join(DATA, "psx_sector_map.json")))
listed_in = json.load(open(os.path.join(DATA, "psx_listed_in.json")))
symbols = sorted(sector_codes.keys())
print(f"universe: {len(symbols)} symbols", flush=True)

# market listing: latest row per symbol for close/change
listing_rows = json.load(open(os.path.join(DATA, "market_listing.json")))
sarm = {}
for r in listing_rows:
    s = r["symbol"]
    if s not in sarm or r.get("date", "") > sarm[s].get("date", ""):
        sarm[s] = r
print(f"market listing rows mapped: {len(sarm)}", flush=True)

out = {}
n = 0
for sym in symbols:
    rec = {"symbol": sym, "sector_code": sector_codes[sym], "listed_in": listed_in.get(sym, "")}
    lr = sarm.get(sym, {})
    rec["name"] = lr.get("name", "")
    rec["close"] = lr.get("close")
    rec["change_pct"] = lr.get("changepercentage")
    rec["volume_avg_5d"] = None
    # key stats
    d = curl(f"API_BASE/stocks/details/{sym}", post=True)
    if d and d.get("success"):
        for m in d["response"]:
            rec["stat_" + m["metricName"]] = m["afValue"]
    # about / sector name
    a = curl(f"API_BASE/stocks/about?symbol={sym}")
    if a and a.get("success"):
        r = a["response"] or {}
        rec["sector_name"] = r.get("sector")
        rec["industry"] = r.get("industry")
        rec["listed_at"] = r.get("listedat")
        rec["isin"] = r.get("isin")
        rec["company_size"] = r.get("company_size")
        rec["free_float_pct"] = r.get("freefloat")
    out[sym] = rec
    n += 1
    if n % 25 == 0:
        print(f"{n}/{len(symbols)} done", flush=True)
        json.dump(out, open(os.path.join(DATA, "key_stats.json"), "w"), indent=1)
    time.sleep(0.08)

json.dump(out, open(os.path.join(DATA, "key_stats.json"), "w"), indent=1)
print("DONE", len(out), flush=True)
