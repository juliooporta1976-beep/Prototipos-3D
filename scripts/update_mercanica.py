#!/usr/bin/env python3
"""Genera mercanica-data.json y aplica fluctuación diaria automática."""
import csv, json, os, re, urllib.request, sys, random
from datetime import datetime, timedelta, timezone

HTML, OUT, CSV = "MercaNica.html", "mercanica-data.json", "mercanica-precios.csv"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

html = open(HTML, encoding="utf-8").read()
m = re.search(r'<script id="SEED" type="application/json">\s*(.*?)\s*</script>', html, re.S)
if not m:
    sys.exit("No encontré el bloque SEED en MercaNica.html")
data = json.loads(m.group(1))
ids = {p["id"] for p in data["products"]}

# 1) Leer precios anteriores del JSON si existe
prev_data = {}
if os.path.exists(OUT):
    try:
        prev_data = json.load(open(OUT, encoding="utf-8"))
        data["basePrices"] = prev_data.get("basePrices", data["basePrices"])
        data["fx"] = prev_data.get("fx", data["fx"])
    except Exception:
        pass

prev_base = dict(data["basePrices"])

# 2) Precios manuales del CSV (si los hay, tienen prioridad)
n = 0
if os.path.exists(CSV):
    raw = [l for l in open(CSV, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    for r in csv.DictReader(raw):
        try:
            pid = r["id"].strip()
            v = float(r["precio_nio"])
        except Exception:
            continue
        if pid in ids and 0.5 <= v <= 100000:
            data["basePrices"][pid] = v
            n += 1

# 3) FLUCTUACIÓN AUTOMÁTICA (Si no se cambió manualmente en el CSV)
for pid, price in data["basePrices"].items():
    if prev_base.get(pid) == price:  # Si el usuario no lo cambió a mano
        # Variación aleatoria entre -1.5% y +2.5% (simula inflación)
        variacion = random.uniform(-0.015, 0.025)
        nuevo_precio = int(round(price * (1 + variacion)))
        data["basePrices"][pid] = max(1, nuevo_precio) # Evitar precios negativos o cero

# 4) Tipo de cambio (protección anti-salto)
try:
    with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=20) as r:
        rates = json.load(r)["rates"]
    for c, old_v in list(data["fx"].items()):
        if c == "NIO" or c not in rates or "NIO" not in rates: continue
        new = rates["NIO"] / rates[c]
        if old_v and abs(new / old_v - 1) <= 0.05:
            data["fx"][c] = round(new, 4)
except Exception as e:
    pass

data["updated"] = today
data["version"] = today.replace("-", ".") + ".1"

json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"MercaNica: precios actualizados con fluctuación diaria.")
