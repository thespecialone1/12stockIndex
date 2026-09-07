#!/usr/bin/env python3
"""Build report/index.html: inject portfolio data into the HTML template."""
import json, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
REPORT = os.path.join(BASE, "report")

port = json.load(open(os.path.join(DATA, "portfolio.json")))
deep = json.load(open(os.path.join(DATA, "deep_data.json")))
ksew = json.load(open(os.path.join(DATA, "kse100_weights.json")))

SHORT = {
    "OIL & GAS EXPLORATION COMPANIES": "E&P",
    "COMMERCIAL BANKS": "Banks",
    "FERTILIZER": "Fertilizer",
    "FOOD & PERSONAL CARE PRODUCTS": "Foods & PC",
    "POWER GENERATION & DISTRIBUTION": "Power",
    "CEMENT": "Cement",
    "TECHNOLOGY & COMMUNICATION": "Tech",
    "PHARMACEUTICALS": "Pharma",
}

# sparklines: last 130 normalized points per stock
for s in port["stocks"]:
    ph = sorted(deep[s["symbol"]]["price_history"], key=lambda x: x["date"])[-130:]
    base = ph[0]["price"]
    s["spark"] = [round(p["price"] / base * 100 - 100, 1) for p in ph]
    s["sector_short"] = SHORT.get(s["sector"], s["sector"])
    s["mcap_b"] = round(s["mcap"] / 1e9)

# downsampled curves for the chart
def downsample(pts, n=150):
    if len(pts) <= n:
        return pts
    step = len(pts) / n
    return [pts[int(i * step)] for i in range(n)] + [pts[-1]]

port["backtest"]["kse100_s"] = downsample(port["backtest"]["kse100"])
port["backtest"]["portfolio_s"] = downsample(port["backtest"]["portfolio"])

# market context
port["market"] = {
    "kse100": 173636.08, "kse_chg": -0.97,
    "hi52": 191032.73, "lo52": 144119.44,
    "kse_pe": "7.0–7.8", "kse_dy": 6.3, "kse_roe": 20.1,
    "policy_rate": 11.5, "brent": 101.67, "pkr": 277.4,
    "yoy_pct": 11.24, "ytd_pct": -1.54,
}
port["kse_concentration"] = {
    "top10": ksew["top10_concentration"],
    "banks_ep": round(ksew["sector_weights"].get("COMMERCIAL BANKS", 0)
                      + ksew["sector_weights"].get("OIL & GAS EXPLORATION COMPANIES", 0), 1),
    "sector_weights": ksew["sector_weights"],
}
# alpha summary (price-only, equal weight)
port["alpha"] = {
    "m3": {"port": 3.6, "idx": 1.9, "diff": 1.7},
    "m6": {"port": 16.4, "idx": 10.3, "diff": 6.1},
    "m12": {"port": 13.8, "idx": 12.6, "diff": 1.2},
}

tpl = open(os.path.join(BASE, "report", "template.html")).read()
html = tpl.replace("/*__DATA__*/", json.dumps(port, ensure_ascii=False))
os.makedirs(REPORT, exist_ok=True)
open(os.path.join(REPORT, "index.html"), "w").write(html)
print("wrote report/index.html", len(html), "bytes")
