#!/usr/bin/env python3
"""Genera mercanica-data.json a diario: precios curados (CSV) + tipo de cambio + fecha."""
import csv, json, os, re, urllib.request, sys
from datetime import datetime, timedelta, timezone

HTML, OUT, CSV = "MercaNica.html", "mercanica-data.json", "mercanica-precios.csv"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

html = open(HTML, encoding="utf-8").read()
m = re.search(r'<script id="SEED" type="application/json">\s*(.*?)\s*</script>', html, re.S)
if not m:
    sys.exit("No encontré el bloque SEED en MercaNica.html")
data = json.loads(m.group(1))
ids = {p["id"] for p in data["products"]}
prev_base = dict(data["basePrices"])

# 1) Precios del CSV (con validación)
n, skip = 0, 0
if os.path.exists(CSV):
    raw = [l for l in open(CSV, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    for r in csv.DictReader(raw):
        try:
            pid = r["id"].strip()
            v = float(r["precio_nio"])
            force = "#force" in (r.get("fecha") or "")
        except Exception:
            skip += 1; continue
        if pid not in ids:
            print(f"  · id desconocido: {pid}"); skip += 1; continue
        if not (0.5 <= v <= 100000):
            print(f"  · precio fuera de rango: {pid}={v}"); skip += 1; continue
        old = prev_base.get(pid, v)
        if old and not force and old > 0 and abs(v/old - 1) > 0.5:
            print(f"  · cambio >50% en {pid}: {old}→{v} (agrega #force si es real)"); skip += 1; continue
        data["basePrices"][pid] = v
        n += 1
print(f"CSV: {n} aplicados, {skip} omitidos")

# 2) Tipo de cambio (con protección anti-salto >5%)
prev_fx = {}
if os.path.exists(OUT):
    try: prev_fx = json.load(open(OUT, encoding="utf-8")).get("fx", {})
    except Exception: pass
for k, v in prev_fx.items():
    if k in data["fx"]: data["fx"][k] = v
try:
    with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=20) as r:
        rates = json.load(r)["rates"]
    for c, old_v in list(data["fx"].items()):
        if c == "NIO" or c not in rates or "NIO" not in rates: continue
        new = rates["NIO"] / rates[c]
        if old_v and abs(new / old_v - 1) <= 0.05:
            data["fx"][c] = round(new, 4)
except Exception as e:
    print("FX omitido:", e)

# 3) ¿Cambió algo real? Si no, no reescribo
changed = (data["basePrices"] != prev_base) or (data.get("fx") != prev_fx)
data["updated"] = today
data["version"] = today.replace("-", ".") + ".1"

if not changed and os.path.exists(OUT):
    print("Sin cambios reales, no reescribo", OUT)
    sys.exit(0)

json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("listo", OUT, data["version"])
