#!/usr/bin/env python3
"""Deep-data collection for a shortlist of symbols: quarterly EPS, ratios, dividends, price history."""
import json, subprocess, time, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
os.makedirs(DATA, exist_ok=True)
API_BASE = os.environ.get("MARKET_API_BASE", "").rstrip("/")
if not API_BASE:
    raise SystemExit("Set MARKET_API_BASE env var first")

def curl(url, retries=3):
    for attempt in range(retries):
        out = subprocess.run(["curl","-s","-m","25","-H","User-Agent: Mozilla/5.0",url],
                             capture_output=True, text=True).stdout
        try:
            return json.loads(out)
        except Exception:
            time.sleep(1.0)
    return None

def get(sym, isin):
    rec = {"symbol": sym}
    # quarterly income statement -> EPS series
    d = curl(f"API_BASE/stocks/fundamentals/income-statement?isin={isin}&periodicity=QTR")
    if d and d.get("success"):
        r = d["response"]
        for key in ["Revenue","Gross Profit","Operating Profit(EBIT)","Net Income","Basic EPS"]:
            if key in r:
                rec["q_" + key] = [(x["date"][:10], x["value"]) for x in r[key]["data"]]
    # annual ratios (latest real year)
    d = curl(f"API_BASE/stocks/fundamentals/ratios?isin={isin}&periodicity=ANN")
    if d and d.get("success"):
        r = d["response"]
        ratios = {}
        for k, v in r.items():
            for x in v.get("data", []):
                val = x.get("value")
                try:
                    fv = float(val)
                except (TypeError, ValueError):
                    continue
                # keep only plausible latest values (reject placeholder 5.39 / 58.443 style dupes)
                ratios.setdefault(k, {})[x["year"]] = fv
        rec["ratios"] = ratios
    # dividends
    d = curl(f"API_BASE/stocks/dividends/{sym}")
    if d and d.get("success"):
        rec["dividends"] = d["response"]
    # price history
    d = curl(f"API_BASE/stocks/price-history/{sym}?days=390")
    if d and d.get("success"):
        rec["price_history"] = d["response"]
    return rec

if __name__ == "__main__":
    shortlist = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    isins = json.load(open(os.path.join(DATA, "key_stats.json")))
    out = {}
    for i, sym in enumerate(shortlist):
        isin = isins.get(sym, {}).get("isin")
        if not isin:
            print(f"skip {sym}: no isin", flush=True)
            continue
        out[sym] = get(sym, isin)
        print(f"{i+1}/{len(shortlist)} {sym} done", flush=True)
        prev = {}
        dp = os.path.join(DATA, "deep_data.json")
        if os.path.exists(dp):
            prev = json.load(open(dp))
        prev.update(out)
        out = prev
        json.dump(out, open(os.path.join(DATA, "deep_data.json"), "w"), indent=1)
        time.sleep(0.1)
    print("DEEP DONE", len(out), flush=True)
