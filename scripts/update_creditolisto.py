#!/usr/bin/env python3
"""Genera creditolisto-data.json con la tasa de cambio actualizada del dólar."""
import json, urllib.request
from datetime import datetime, timezone, timedelta

OUT = "creditolisto-data.json"
today = (datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d")

bcn_rate = 36.6243  # Valor por defecto (respaldo por si falla el internet)

try:
    # Buscamos la tasa de cambio actual
    with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=20) as r:
        rates = json.load(r).get("rates", {})
        if "NIO" in rates:
            bcn_rate = round(rates["NIO"], 4)
except Exception as e:
    print(f"⚠️ No se pudo obtener la tasa en línea, se usará la de respaldo: {e}")

data = {
    "version": today.replace("-", ".") + ".1",
    "updated": today,
    "bcnRate": bcn_rate
}

# Guardamos el archivo JSON
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

print(f"✅ CreditoListo: Tasa BCN actualizada a {bcn_rate} córdobas por dólar.")
